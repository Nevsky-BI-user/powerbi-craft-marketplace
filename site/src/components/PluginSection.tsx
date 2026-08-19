import type { Plugin, Skill } from "../types";
import { CopyRow } from "./Copy";
import { WIDE_FROM } from "./InventorySection";

export function pluralSkills(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return `${n} скіл`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${n} скіли`;
  return `${n} скілів`;
}

export const PLUGIN_ICONS: Record<string, string> = {
  "pbi-visuals": "📊",
  "pbi-report-ux": "🧭",
  "pbi-design-language": "🎨",
  "pbi-quality": "🔍",
  "report-storytelling": "📣",
  "dax-craft": "🧮",
  "pbip-devops": "🔀",
  "azure-ops": "☁️",
  "project-bootstrap": "🚀",
};

/** Опис для підказки/картки: український, якщо є, інакше оригінальний. */
export function skillTip(s: { short: string; shortUk?: string }): string {
  return s.shortUk || s.short;
}

function skillPrompt(plugin: string, skill: string, repo: string): string {
  return (
    `Встанови окремий скіл Claude Code «${skill}» з github.com/${repo}: ` +
    `зроби sparse checkout теки plugins/${plugin}/skills/${skill} і скопіюй її вміст ` +
    `у ~/.claude/skills/${skill}/ (створи теку). Перевір, що SKILL.md на місці, ` +
    `і покажи його name та description.`
  );
}

function SkillCard(props: { plugin: Plugin; skill: Skill; repo: string }) {
  const { plugin, skill, repo } = props;
  return (
    <div className="skillcard" id={skill.name}>
      <h3>
        {skill.name}{" "}
        <span className="meta">
          · плагін {plugin.name} {plugin.version} ·{" "}
          <a href={`#${skill.name}`} aria-label={`Пряме посилання на ${skill.name}`}>#</a>
        </span>
      </h3>
      <p className="desc">{skillTip(skill)}</p>
      {skill.triggers.length > 0 && (
        <p className="triggers">Тригери: {skill.triggers.map((t) => `«${t}»`).join(", ")}</p>
      )}
      <details>
        <summary>Лише цей скіл, без плагіна — промпт для Claude Code</summary>
        <CopyRow text={skillPrompt(plugin.name, skill.name, repo)} kind="skill-prompt" item={skill.name} />
      </details>
    </div>
  );
}

export function PluginSection(props: {
  plugin: Plugin;
  repo: string;
  mpName: string;
  openSkill: string | null;
  onToggle: (name: string) => void;
  popular: Set<string>;
}) {
  const { plugin, repo, mpName, openSkill, onToggle, popular } = props;
  const open = plugin.skills.find((s) => s.name === openSkill) ?? null;
  return (
    <section
      className={`plugin${plugin.skills.length >= WIDE_FROM ? " wide" : ""}`}
      id={`p-${plugin.name}`}
    >
      <div className="plugin-head">
        <span className="picon" aria-hidden="true">{PLUGIN_ICONS[plugin.name] ?? "🧩"}</span>
        <h3>{plugin.name}</h3>
        <span className="badge ver">{plugin.version}</span>
        <span className="tagline">
          {pluralSkills(plugin.skills.length)} · {plugin.tagline}
        </span>
        {plugin.hasHooks && (
          <span className="badge hook" title="Після встановлення додає автоматичну перевірку (PostToolUse-хук)">hook</span>
        )}
        {plugin.agents.length > 0 && (
          <span className="badge agent" title={`Субагенти: ${plugin.agents.join(", ")}`}>agent</span>
        )}
      </div>
      {plugin.description && <p className="plugin-desc">{plugin.description}</p>}
      <CopyRow text={`claude plugin install ${plugin.name}@${mpName}`} kind="plugin" item={plugin.name} />
      <div className="chips">
        {plugin.skills.map((s) => (
          <button
            key={s.name}
            className={openSkill === s.name ? "chip open" : "chip"}
            onClick={() => onToggle(s.name)}
            aria-expanded={openSkill === s.name}
            data-tip={skillTip(s)}
          >
            {s.name.replace(/^pbi-/, "")}
            {popular.has(s.name) && <span className="badge pop">топ</span>}
          </button>
        ))}
      </div>
      {open && <SkillCard plugin={plugin} skill={open} repo={repo} />}
    </section>
  );
}
