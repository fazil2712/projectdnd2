import re
from typing import AsyncGenerator, Dict, Any, Optional, Tuple, List


class StreamParser:
    """
    Parses LLM streaming tokens in real-time, buffering potential markup tags
    and detecting structured DM interrupts and game events:
      - <CHECK_REQUEST type="..." target="..." dc="..." reason="..."/>
      - <ACTION_REJECT reason="..."/>
      - <ITEM_GRANT name="..." quantity="..." .../>
      - <ITEM_CONSUME name="..." quantity="..."/>
      - <LEVEL_UP level="..." reason="..."/>
    """

    # Tag regexes supporting single/double/unquoted attributes, case-insensitivity,
    # optional closing tags, and stripping optional wrapping markdown fences (` or ```xml).
    CHECK_REQUEST_REGEX = re.compile(
        r'(?:```(?:xml)?\s*|`\s*)?<CHECK_REQUEST\s+([^>]*?)(?:/>|>(?:[\s\S]*?</CHECK_REQUEST>)?)(?:\s*```|\s*`)?',
        re.IGNORECASE
    )
    ACTION_REJECT_REGEX = re.compile(
        r'(?:```(?:xml)?\s*|`\s*)?<ACTION_REJECT\s+([^>]*?)(?:/>|>(?:[\s\S]*?</ACTION_REJECT>)?)(?:\s*```|\s*`)?',
        re.IGNORECASE
    )
    ITEM_GRANT_REGEX = re.compile(
        r'(?:```(?:xml)?\s*|`\s*)?<ITEM_GRANT\s+([^>]*?)(?:/>|>(?:[\s\S]*?</ITEM_GRANT>)?)(?:\s*```|\s*`)?',
        re.IGNORECASE
    )
    ITEM_CONSUME_REGEX = re.compile(
        r'(?:```(?:xml)?\s*|`\s*)?<ITEM_CONSUME\s+([^>]*?)(?:/>|>(?:[\s\S]*?</ITEM_CONSUME>)?)(?:\s*```|\s*`)?',
        re.IGNORECASE
    )
    LEVEL_UP_REGEX = re.compile(
        r'(?:```(?:xml)?\s*|`\s*)?<LEVEL_UP\s+([^>]*?)(?:/>|>(?:[\s\S]*?</LEVEL_UP>)?)(?:\s*```|\s*`)?',
        re.IGNORECASE
    )

    TAG_PATTERNS = [
        ("item_grant", ITEM_GRANT_REGEX),
        ("item_consume", ITEM_CONSUME_REGEX),
        ("level_up", LEVEL_UP_REGEX),
        ("action_reject", ACTION_REJECT_REGEX),
        ("check_request", CHECK_REQUEST_REGEX),
    ]

    ATTR_REGEX = re.compile(r'([a-zA-Z_0-9\-]+)\s*=\s*(?:["\']([^"\']*)["\']|([^\s>]+))')

    VALID_TAG_PREFIXES = (
        "<check_request",
        "<action_reject",
        "<item_consume",
        "<item_grant",
        "<level_up",
    )

    def __init__(self):
        self.buffer = ""
        self.accumulated_clean_text = ""
        self.check_triggered: Optional[Dict[str, Any]] = None
        self.rejection_triggered: Optional[Dict[str, Any]] = None
        self.items_granted: list = []
        self.items_consumed: list = []
        self.level_ups: list = []

    def _parse_attributes(self, attr_string: str) -> Dict[str, str]:
        """
        Extracts key-value pairs from attribute string.
        Supports single quotes, double quotes, unquoted values, and case-insensitive keys.
        """
        attrs = {}
        for match in self.ATTR_REGEX.finditer(attr_string):
            key = match.group(1).lower()
            val = (match.group(2) if match.group(2) is not None else match.group(3) or "").strip()
            attrs[key] = val
        return attrs

    async def process_token_stream(
        self,
        token_stream: AsyncGenerator[str, None]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Consumes raw token stream and yields structured events:
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

            # Multi-tag loop: check and consume any tags present in buffer in order of appearance
            while True:
                matches: List[Tuple[str, Any]] = []
                for tag_type, regex in self.TAG_PATTERNS:
                    m = regex.search(self.buffer)
                    if m:
                        matches.append((tag_type, m))

                if not matches:
                    break

                # Pick the earliest tag match in the buffer
                tag_type, match = min(matches, key=lambda x: x[1].start())

                # Flush text preceding the matched tag
                pre_text = self.buffer[:match.start()]
                if pre_text:
                    self.accumulated_clean_text += pre_text
                    yield {"type": "token", "content": pre_text}

                attrs = self._parse_attributes(match.group(1))

                if tag_type == "item_grant":
                    self.items_granted.append(attrs)
                    yield {"type": "item_granted", "item": attrs}
                elif tag_type == "item_consume":
                    self.items_consumed.append(attrs)
                    yield {"type": "item_consumed", "consumption": attrs}
                elif tag_type == "level_up":
                    self.level_ups.append(attrs)
                    yield {"type": "level_up", "level_up": attrs}
                elif tag_type == "action_reject":
                    reason = attrs.get("reason", "Action violates fictional boundaries or rules.")
                    self.rejection_triggered = {"reason": reason}
                    yield {"type": "action_rejected", "rejection": self.rejection_triggered}
                elif tag_type == "check_request":
                    check_type = attrs.get("type", "skill").lower()
                    target = attrs.get("target", "Dexterity")
                    raw_dc = attrs.get("dc", "15")
                    try:
                        dc = int(re.sub(r"[^\d]", "", str(raw_dc)) or 15)
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

                    # Halt further narrative stream on check
                    self.buffer = ""
                    yield {"type": "done", "narrative": self.accumulated_clean_text.strip()}
                    return

                # Advance buffer past the matched tag
                self.buffer = self.buffer[match.end():]

            # Buffer hang prevention:
            # If buffer contains '<', check if it could be a valid tag candidate
            if "<" in self.buffer:
                # Find the start of potential tag (including any markdown fence immediately before it)
                fence_m = re.search(r'(?:```(?:xml)?\s*|`\s*)?<', self.buffer)
                tag_start = fence_m.start() if fence_m else self.buffer.find("<")

                # If there is safe text before the candidate, flush it immediately
                if tag_start > 0:
                    emit_chunk = self.buffer[:tag_start]
                    self.accumulated_clean_text += emit_chunk
                    yield {"type": "token", "content": emit_chunk}
                    self.buffer = self.buffer[tag_start:]

                # Inspect candidate tag prefix
                candidate = re.sub(r'^(?:```(?:xml)?\s*|`\s*)', '', self.buffer, flags=re.IGNORECASE).lower()
                is_valid_prefix = any(
                    p.startswith(candidate) or candidate.startswith(p)
                    for p in self.VALID_TAG_PREFIXES
                )
                newline_in_prefix = ("\n" in candidate and not any(candidate.startswith(p) for p in self.VALID_TAG_PREFIXES))
                exceeds_max_buffer = len(self.buffer) > 300
                unmatched_closed_tag = (">" in self.buffer)

                if not is_valid_prefix or newline_in_prefix or exceeds_max_buffer or unmatched_closed_tag:
                    # Not a valid incomplete tag; flush it out as normal prose tokens
                    self.accumulated_clean_text += self.buffer
                    yield {"type": "token", "content": self.buffer}
                    self.buffer = ""
            else:
                # No '<' at all; flush entire buffer
                if self.buffer:
                    self.accumulated_clean_text += self.buffer
                    yield {"type": "token", "content": self.buffer}
                    self.buffer = ""

        # Stream end: flush any residual buffer tokens rather than dropping
        if self.buffer:
            self.accumulated_clean_text += self.buffer
            yield {"type": "token", "content": self.buffer}
            self.buffer = ""

        yield {"type": "done", "narrative": self.accumulated_clean_text.strip()}
