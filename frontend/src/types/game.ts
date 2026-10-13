export interface AbilityScores {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
}

export interface InventoryItem {
  id: string;
  name: string;
  quantity: number;
  weight_lbs: number;
  item_type: 'weapon' | 'armor' | 'shield' | 'potion' | 'scroll' | 'gear' | 'tool' | 'treasure' | string;
  equipped: boolean;
  damage?: string;
  damage_type?: string;
  armor_base?: number;
  armor_category?: string;
  properties: string[];
  description?: string;
}

export interface SpellSlotLevel {
  max_slots: number;
  used_slots: number;
}

export interface SpellSlots {
  level_1: SpellSlotLevel;
  level_2: SpellSlotLevel;
  level_3: SpellSlotLevel;
  level_4: SpellSlotLevel;
  level_5: SpellSlotLevel;
  level_6: SpellSlotLevel;
  level_7: SpellSlotLevel;
  level_8: SpellSlotLevel;
  level_9: SpellSlotLevel;
}

export interface DeathSaves {
  successes: number;
  failures: number;
}

export interface Character {
  name: string;
  character_class: string;
  subclass?: string;
  level: number;
  race: string;
  alignment: string;
  background: string;
  backstory?: string;
  racial_traits?: string[];
  abilities: AbilityScores;
  max_hp: number;
  current_hp: number;
  temp_hp: number;
  hit_dice_max: number;
  hit_dice_current: number;
  hit_die_type: string;
  death_saves: DeathSaves;
  saving_throw_proficiencies: string[];
  skill_proficiencies: string[];
  skill_expertise: string[];
  spellcasting_ability?: string;
  known_spells: string[];
  spell_slots: SpellSlots;
  inventory: InventoryItem[];
  conditions: string[];
  speed_feet: number;
  darkvision_feet: number;

  // Computed values
  proficiency_bonus: number;
  ability_modifiers: Record<string, number>;
  saving_throw_bonuses: Record<string, number>;
  skill_bonuses: Record<string, number>;
  passive_perception: number;
  armor_class: number;
  spell_save_dc?: number;
  spell_attack_bonus?: number;
  total_weight_carried: number;
  carrying_capacity_lbs: number;
  is_encumbered: boolean;
}

export interface CheckRequestData {
  type: 'skill' | 'save' | 'attack' | 'ability' | string;
  target: string;
  dc: number;
  reason: string;
  modifier?: number;
  resolved_name?: string;
}

export interface RollResult {
  raw_rolls: number[];
  selected_raw: number;
  dropped_raw?: number | null;
  modifier: number;
  total: number;
  advantage: boolean;
  disadvantage: boolean;
  is_critical_success: boolean;
  is_critical_failure: boolean;
  notation: string;
}

export interface CheckResolution {
  check_type: string;
  target: string;
  resolved_name: string;
  dc: number;
  modifier: number;
  roll: RollResult;
  success: boolean;
  margin: number;
  crit_note?: string;
  mechanical_summary: string;
}

export interface DamageResolution {
  weapon_name: string;
  damage_type: string;
  damage_total: number;
  dice_breakdown: string;
  is_critical: boolean;
  summary: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  description: string;
  vram_approx: string;
  status: 'ready' | 'downloading' | 'available' | 'failed';
  progress: number;
  message: string;
  is_active: boolean;
}

export interface NarrativeEntry {
  id: string;
  role: 'player' | 'dm' | 'system' | 'rejection';
  content: string;
  timestamp: string;
  metadata?: {
    check?: CheckRequestData;
    roll?: CheckResolution;
    damage?: DamageResolution;
  };
}
