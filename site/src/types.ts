export interface Skill {
  name: string;
  short: string;
  description: string;
  triggers: string[];
}

export interface Plugin {
  name: string;
  version: string;
  description: string;
  tagline: string;
  hasHooks: boolean;
  agents: string[];
  skills: Skill[];
}

export interface ChangelogEntry {
  version: string;
  date: string;
  title: string;
  items: string[];
}

export interface Catalog {
  marketplace: { name: string; repo: string; description: string };
  totals: { plugins: number; skills: number };
  plugins: Plugin[];
  changelog: ChangelogEntry[];
}

export interface InvSkill {
  name: string;
  short: string;
  source?: string | null;
}

export interface InvPlugin {
  name: string;
  installCmd: string;
  skills: InvSkill[];
}

export interface InvGroup {
  group: "anthropic" | "microsoft" | "goblin" | "standalone" | "project";
  title: string;
  repo: string | null;
  addCmd: string | null;
  plugins: InvPlugin[];
  skills?: InvSkill[];
  skillCount: number;
  uniqueCount: number;
}

export interface Inventory {
  snapshotDate: string;
  groups: InvGroup[];
}
