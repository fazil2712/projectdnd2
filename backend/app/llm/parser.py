import re
from typing import AsyncGenerator, Dict, Any, Optional, Tuple


class StreamParser:
    """
    Parses LLM streaming tokens in real-time, buffering potential markup tags
    and detecting structured DM interrupts:
      - <CHECK_REQUEST type="..." target="..." dc="..." reason="..."/>
      - <ACTION_REJECT reason="..."/>
    """

    CHECK_REQUEST_REGEX = re.compile(
        r'<CHECK_REQUEST\s+([^>]*?)(?:/>|>(?:.*?</CHECK_REQUEST>)?)',
        re.IGNORECASE | re.DOTALL
    )
    ACTION_REJECT_REGEX = re.compile(
        r'<ACTION_REJECT\s+([^>]*?)(?:/>|>(?:.*?</ACTION_REJECT>)?)',
        re.IGNORECASE | re.DOTALL
    )
    ITEM_GRANT_REGEX = re.compile(
        r'<ITEM_GRANT\s+([^>]*?)(?:/>|>(?:.*?</ITEM_GRANT>)?)',
        re.IGNORECASE | re.DOTALL
    )
    ITEM_CONSUME_REGEX = re.compile(
        r'<ITEM_CONSUME\s+([^>]*?)(?:/>|>(?:.*?</ITEM_CONSUME>)?)',
        re.IGNORECASE | re.DOTALL
    )
    LEVEL_UP_REGEX = re.compile(
        r'<LEVEL_UP\s+([^>]*?)(?:/>|>(?:.*?</LEVEL_UP>)?)',
        re.IGNORECASE | re.DOTALL
    )
    ATTR_REGEX = re.compile(r'(\w+)=["\']([^"\']*)["\']')

    def __init__(self):
        self.buffer = ""
        self.accumulated_clean_text = ""
        self.check_triggered: Optional[Dict[str, Any]] = None
        self.rejection_triggered: Optional[Dict[str, Any]] = None
        self.items_granted: list = []
        self.items_consumed: list = []
        self.level_ups: list = []

    def _parse_attributes(self, attr_string: str) -> Dict[str, str]:
        attrs = {}
        for match in self.ATTR_REGEX.finditer(attr_string):
            key = match.group(1).lower()
            val = match.group(2).strip()
            attrs[key] = val
        return attrs

    async def process_token_stream(
        self,
        token_stream: AsyncGenerator[str, None]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Consumes raw token stream, yields structured events:
          - {"type": "token", "content": str}
          - {"type": "check_required", "check": {...}}
          - {"type": "action_rejected", "rejection": {...}}
          - {"type": "item_granted", "item": {...}}
          - {"type": "item_consumed", "consumption": {...}}
          - {"type": "level_up", "level_up": {...}}
          - {"type": "done", "narrative": str}
        """
        async for token in token_stream:
            self.buffer += token

            # Check if an <ITEM_GRANT .../> is present
            grant_match = self.ITEM_GRANT_REGEX.search(self.buffer)
            if grant_match:
                pre_text = self.buffer[:grant_match.start()]
                if pre_text.strip():
                    self.accumulated_clean_text += pre_text
                    yield {"type": "token", "content": pre_text}
                attrs = self._parse_attributes(grant_match.group(1))
                self.items_granted.append(attrs)
                yield {"type": "item_granted", "item": attrs}
                self.buffer = self.buffer[grant_match.end():]
                continue

            # Check if an <ITEM_CONSUME .../> is present
            consume_match = self.ITEM_CONSUME_REGEX.search(self.buffer)
            if consume_match:
                pre_text = self.buffer[:consume_match.start()]
                if pre_text.strip():
                    self.accumulated_clean_text += pre_text
                    yield {"type": "token", "content": pre_text}
                attrs = self._parse_attributes(consume_match.group(1))
                self.items_consumed.append(attrs)
                yield {"type": "item_consumed", "consumption": attrs}
                self.buffer = self.buffer[consume_match.end():]
                continue

            # Check if a <LEVEL_UP .../> is present
            lvl_match = self.LEVEL_UP_REGEX.search(self.buffer)
            if lvl_match:
                pre_text = self.buffer[:lvl_match.start()]
                if pre_text.strip():
                    self.accumulated_clean_text += pre_text
                    yield {"type": "token", "content": pre_text}
                attrs = self._parse_attributes(lvl_match.group(1))
                self.level_ups.append(attrs)
                yield {"type": "level_up", "level_up": attrs}
                self.buffer = self.buffer[lvl_match.end():]
                continue

            # Check if an <ACTION_REJECT .../> is present
            reject_match = self.ACTION_REJECT_REGEX.search(self.buffer)
            if reject_match:
                pre_text = self.buffer[:reject_match.start()]
                if pre_text.strip():
                    self.accumulated_clean_text += pre_text
                    yield {"type": "token", "content": pre_text}

                attrs = self._parse_attributes(reject_match.group(1))
                reason = attrs.get("reason", "Action violates fictional boundaries or rules.")
                self.rejection_triggered = {"reason": reason}
                yield {"type": "action_rejected", "rejection": self.rejection_triggered}

                # Clear up to end of tag
                self.buffer = self.buffer[reject_match.end():]
                continue


            # Check if a <CHECK_REQUEST .../> is present
            check_match = self.CHECK_REQUEST_REGEX.search(self.buffer)
            if check_match:
                # Flush text preceding the check request
                pre_text = self.buffer[:check_match.start()]
                if pre_text:
                    self.accumulated_clean_text += pre_text
                    yield {"type": "token", "content": pre_text}

                attrs = self._parse_attributes(check_match.group(1))
                check_type = attrs.get("type", "skill").lower()
                target = attrs.get("target", "Dexterity")
                raw_dc = attrs.get("dc", "15")
                try:
                    dc = int(re.sub(r"[^\d]", "", raw_dc) or 15)
                except ValueError:
                    dc = 15
                reason = attrs.get("reason", f"Testing {target}")

                self.check_triggered = {
                    "type": check_type,
                    "target": target,
                    "dc": dc,
                    "reason": reason,
                }
                yield {"type": "check_required", "check": self.check_triggered}

                # When a check is required, halt further narrative stream!
                self.buffer = ""
                yield {"type": "done", "narrative": self.accumulated_clean_text.strip()}
                return

            # Safe emission: if buffer doesn't look like an uncompleted tag start
            if "<" in self.buffer:
                tag_start = self.buffer.find("<")
                # Emit text before the potential tag
                if tag_start > 0:
                    emit_chunk = self.buffer[:tag_start]
                    self.accumulated_clean_text += emit_chunk
                    yield {"type": "token", "content": emit_chunk}
                    self.buffer = self.buffer[tag_start:]
                # Keep the unclosed potential tag in the buffer unless it's clearly not a tag
                if len(self.buffer) > 250 and ">" not in self.buffer:
                    # Not a valid tag; flush it out
                    self.accumulated_clean_text += self.buffer
                    yield {"type": "token", "content": self.buffer}
                    self.buffer = ""
            else:
                # No '<' at all; flush buffer
                if self.buffer:
                    self.accumulated_clean_text += self.buffer
                    yield {"type": "token", "content": self.buffer}
                    self.buffer = ""

        if self.buffer:
            clean_remaining = self.CHECK_REQUEST_REGEX.sub("", self.buffer)
            clean_remaining = self.ACTION_REJECT_REGEX.sub("", clean_remaining)
            clean_remaining = self.ITEM_GRANT_REGEX.sub("", clean_remaining)
            clean_remaining = self.ITEM_CONSUME_REGEX.sub("", clean_remaining)
            clean_remaining = self.LEVEL_UP_REGEX.sub("", clean_remaining)
            if clean_remaining:
                self.accumulated_clean_text += clean_remaining
                yield {"type": "token", "content": clean_remaining}
            self.buffer = ""


        yield {"type": "done", "narrative": self.accumulated_clean_text.strip()}
