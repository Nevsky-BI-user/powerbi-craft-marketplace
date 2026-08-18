import { useState, type ReactNode } from "react";
import type { InvGroup, InvGroupId, InvPlugin, InvSkill, InvSource } from "../types";
import { CopyRow } from "./Copy";
import { pluralSkills, skillTip } from "./PluginSection";
import { track } from "../telemetry";

export const GROUP_LABELS: Record<InvGroupId, string> = {
  anthropic: "Anthropic",
  microsoft: "Microsoft",
  goblin: "Kurt Buhler",
  standalone: "окремі",
};

function skillMatches(q: string, s: InvSkill): boolean {
  return (
    s.name.toLowerCase().includes(q) ||
    s.short.toLowerCase().includes(q) ||
    (s.shortUk ?? "").toLowerCase().includes(q)
  );
}

/** Фільтр групи за пошуковим рядком; повертає групу лише з відповідними скілами. */
export function filterInvGroup(group: InvGroup, q: string): InvGroup {
  if (!q) return group;
  const plugins = group.plugins
    .map((p) => ({ ...p, skills: p.skills.filter((s) => skillMatches(q, s)) }))
    .filter((p) => p.skills.length > 0);
  const sources = group.sources
    ?.map((s) => ({ ...s, skills: s.skills.filter((sk) => skillMatches(q, sk)) }))
    .filter((s) => s.skills.length > 0);
  const count =
    plugins.reduce((n, p) => n + p.skills.length, 0) +
    (sources?.reduce((n, s) => n + s.skills.length, 0) ?? 0);
  const unique = new Set([
    ...plugins.flatMap((p) => p.skills.map((s) => s.name)),
    ...(sources?.flatMap((s) => s.skills.map((sk) => sk.name)) ?? []),
  ]);
  return { ...group, plugins, sources, skillCount: count, uniqueCount: unique.size };
}

function noSourcePrompt(name: string, desc: string): string {
  return (
    `Встанови скіл Claude Code «${name}» (${desc}). Канонічного репозиторію немає: ` +
    `пошукай на GitHub теку ${name} зі SKILL.md у публічних колекціях скілів і перевір, ` +
    `що опис збігається; знайшов — зроби sparse checkout у ~/.claude/skills/${name}/. ` +
    `Не знайшов — створи скіл сам: тека ~/.claude/skills/${name}/ зі SKILL.md ` +
    `(frontmatter name і description + інструкції), що реалізує описане. ` +
    `Наприкінці покажи name та description.`
  );
}

function standalonePrompt(name: string, repo: string, dir: string | null): string {
  const path = dir ? `${dir}/${name}` : name;
  return (
    `Встанови окремий скіл Claude Code «${name}» з github.com/${repo}: ` +
    `зроби sparse checkout теки ${path} і скопіюй її вміст у ~/.claude/skills/${name}/ ` +
    `(створи теку). Перевір, що SKILL.md на місці, і покажи його name та description.`
  );
}

function MarketSkillCard(props: { skill: InvSkill; group: InvGroup; plugin: InvPlugin }) {
  const { skill, group, plugin } = props;
  return (
    <div className="skillcard">
      <h3>
        {skill.name} <span className="meta">· плагін {plugin.name}</span>
      </h3>
      {skillTip(skill) && <p className="desc">{skillTip(skill)}</p>}
      <CopyRow text={plugin.installCmd} kind="plugin" item={`${group.group}:${plugin.name}`} />
    </div>
  );
}

function StandaloneSkillCard(props: { skill: InvSkill; source: InvSource }) {
  const { skill, source } = props;
  return (
    <div className="skillcard">
      <h3>{skill.name}</h3>
      {skillTip(skill) && <p className="desc">{skillTip(skill)}</p>}
      {source.repo ? (
        <>
          <p className="meta" style={{ margin: "0 0 8px" }}>
            Джерело:{" "}
            <a href={`https://github.com/${source.repo}`} target="_blank" rel="noreferrer">
              {source.repo}
            </a>
          </p>
          {source.marketplace ? (
            <>
              <CopyRow
                text={`claude plugin marketplace add ${source.repo}`}
                kind="marketplace"
                item={`standalone:${source.id}`}
              />
              <p className="meta" style={{ margin: "8px 0 0" }}>
                Цей репозиторій — теж маркетплейс: підключіть його, наберіть <code>/plugin</code> і
                виберіть плагін із цим скілом.
              </p>
            </>
          ) : source.dir !== null ? (
            <details open>
              <summary>Встановити цей скіл — промпт для Claude Code</summary>
              <CopyRow
                text={standalonePrompt(skill.name, source.repo, source.dir)}
                kind="skill-prompt"
                item={`standalone:${skill.name}`}
              />
            </details>
          ) : null}
        </>
      ) : (
        <details open>
          <summary>Промпт для Claude Code — знайти або відтворити цей скіл</summary>
          <CopyRow
            text={noSourcePrompt(skill.name, skillTip(skill))}
            kind="skill-prompt"
            item={`standalone:${skill.name}`}
          />
        </details>
      )}
    </div>
  );
}

function ChipGrid<T>(props: {
  entries: { key: string; skill: InvSkill; payload: T }[];
  groupClass: string;
  trackPrefix: string;
  renderCard: (payload: T, skill: InvSkill) => ReactNode;
}) {
  const { entries, groupClass, trackPrefix, renderCard } = props;
  const [open, setOpen] = useState<string | null>(null);
  const openEntry = entries.find((e) => e.key === open) ?? null;
  return (
    <>
      <div className="chips">
        {entries.map(({ key, skill }) => (
          <button
            key={key}
            className={`chip ${groupClass}${open === key ? " open" : ""}`}
            aria-expanded={open === key}
            data-tip={skillTip(skill) || undefined}
            onClick={() => {
              const next = open === key ? null : key;
              setOpen(next);
              if (next) track("skill-view", `${trackPrefix}:${skill.name}`);
            }}
          >
            {skill.name}
          </button>
        ))}
      </div>
      {openEntry && renderCard(openEntry.payload, openEntry.skill)}
    </>
  );
}

/** Розділ маркетплейс-групи (Anthropic / Microsoft / Kurt Buhler) — уже відфільтрованої.
 *  Кожен плагін — окрема картка з описом, командою і власним якорем mp-<група>-<плагін>. */
export function GroupSection(props: { group: InvGroup }) {
  const { group } = props;
  if (group.skillCount === 0) return null;
  const counts =
    group.uniqueCount !== group.skillCount
      ? `${pluralSkills(group.skillCount)} у ${group.plugins.length} плагінах (${group.uniqueCount} унікальних: набори перекриваються)`
      : `${pluralSkills(group.skillCount)} у ${group.plugins.length} плагінах`;
  return (
    <section id={group.group}>
      <h2>
        {group.title}{" "}
        <span className={`badge gdot g-${group.group}`}>{GROUP_LABELS[group.group]}</span>
      </h2>
      <p className="section-intro">
        {counts}
        {group.repo && (
          <>
            {" · "}
            <a href={`https://github.com/${group.repo}`} target="_blank" rel="noreferrer">
              github.com/{group.repo}
            </a>
          </>
        )}
      </p>
      {group.group === "anthropic" && (
        <p className="section-intro">
          Це офіційний маркетплейс, він уже підключений у кожному Claude Code, тож досить
          команди з картки плагіна. Вбудованих скілів застосунку (docx, pptx, xlsx) тут немає:
          вони і так частина Claude.
        </p>
      )}
      {group.addCmd && (
        <>
          <p className="section-intro">
            Спершу підключіть маркетплейс (один раз), далі беріть команди з карток плагінів:
          </p>
          <CopyRow text={group.addCmd} kind="marketplace" item={group.group} />
        </>
      )}
      <div className="cards-grid">
        {group.plugins.map((p) => (
          <div className={`plugin inv-${group.group}`} id={`mp-${group.group}-${p.name}`} key={p.name}>
            <div className="plugin-head">
              <h3>{p.name}</h3>
              <span className="tagline">{pluralSkills(p.skills.length)}</span>
            </div>
            {p.short && <p className="plugin-desc">{p.short}</p>}
            <CopyRow text={p.installCmd} kind="plugin" item={`${group.group}:${p.name}`} />
            <ChipGrid
              entries={p.skills.map((s) => ({ key: s.name, skill: s, payload: p }))}
              groupClass={`g-${group.group}`}
              trackPrefix={group.group}
              renderCard={(plugin, skill) => (
                <MarketSkillCard skill={skill} group={group} plugin={plugin} />
              )}
            />
          </div>
        ))}
      </div>
    </section>
  );
}

/** Розділ окремих скілів, згрупованих за публічним джерелом. */
export function StandaloneSection(props: { group: InvGroup }) {
  const { group } = props;
  const sources = group.sources ?? [];
  if (group.skillCount === 0) return null;
  return (
    <section id="standalone">
      <h2>
        Окремі скіли{" "}
        <span className="badge gdot g-standalone">{GROUP_LABELS.standalone}</span>
      </h2>
      <p className="section-intro">
        Ці скіли не належать жодному плагіну, вони просто лежать у <code>~/.claude/skills</code>.
        Більшість походить із публічних репозиторіїв, тож поруч із кожним є спосіб поставити
        його й собі. Де канонічного репозиторію немає, на картці лежить промпт: скопіюйте
        його в Claude Code, і той знайде або відтворить скіл сам.
      </p>
      <div className="cards-grid">
      {sources.map((src) => (
        <div className="plugin inv-standalone" key={src.id} id={`src-${src.id}`}>
          <div className="plugin-head">
            <h3>{src.title}</h3>
            <span className="tagline">{pluralSkills(src.skills.length)}</span>
            {src.repo && (
              <a href={`https://github.com/${src.repo}`} target="_blank" rel="noreferrer">
                github.com/{src.repo}
              </a>
            )}
          </div>
          {src.note && <p className="plugin-desc">{src.note}</p>}
          {src.repo && src.marketplace && (
            <CopyRow
              text={`claude plugin marketplace add ${src.repo}`}
              kind="marketplace"
              item={`standalone:${src.id}`}
            />
          )}
          <ChipGrid
            entries={src.skills.map((s) => ({ key: s.name, skill: s, payload: src }))}
            groupClass="g-standalone"
            trackPrefix="standalone"
            renderCard={(source, skill) => <StandaloneSkillCard skill={skill} source={source} />}
          />
        </div>
      ))}
      </div>
    </section>
  );
}
