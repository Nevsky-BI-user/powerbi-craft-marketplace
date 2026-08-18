export interface Skill {
  name: string;
  short: string;
  /** Український короткий опис (кураторський словник); "" — ще не перекладено. */
  shortUk?: string;
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
  shortUk?: string;
}

export interface InvPlugin {
  name: string;
  installCmd: string;
  short?: string;
  shortUk?: string;
  skills: InvSkill[];
}

/** Публічне джерело окремих скілів: репозиторій + спосіб встановлення. */
export interface InvSource {
  id: string;
  title: string;
  repo: string | null;
  /** Префікс теки в репо, під яким лежать скіли ("" — корінь). null — джерела немає. */
  dir: string | null;
  /** true — репо є маркетплейсом плагінів, ставиться через claude plugin marketplace add. */
  marketplace: boolean;
  note: string;
  skills: InvSkill[];
}

export type InvGroupId = "anthropic" | "microsoft" | "goblin" | "standalone";

export interface InvGroup {
  group: InvGroupId;
  title: string;
  repo: string | null;
  addCmd: string | null;
  plugins: InvPlugin[];
  sources?: InvSource[];
  skillCount: number;
  uniqueCount: number;
}

export interface Inventory {
  snapshotDate: string;
  groups: InvGroup[];
}
