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

/** Один блок = одна команда терміналу.
 *
 *  Деякі джерела (Microsoft) пакують той самий набір скілів у кілька плагінів,
 *  що перекриваються: 46 скілів розкладені по 6 плагінах, 42 з них повторюються
 *  до пʼяти разів. Показувати шість карток із шістьма командами означає шість
 *  разів показати одне й те саме. Тому беремо мінімальний набір плагінів, який
 *  покриває всі скіли (жадібне покриття), а решту нарізок ховаємо в деталі.
 *
 *  Там, де плагіни не перетинаються (Anthropic, Kurt Buhler), повертає їх усі —
 *  кожен зі своєю командою, як і було. */
export function coverPlugins(
  plugins: InvPlugin[],
  preferName?: string,
): { chosen: InvPlugin[]; rest: InvPlugin[] } {
  const distinct = new Set(plugins.flatMap((p) => p.skills.map((s) => s.name)));
  const sum = plugins.reduce((n, p) => n + p.skills.length, 0);
  if (sum === distinct.size) return { chosen: plugins, rest: [] };

  const covered = new Set<string>();
  const pool = [...plugins];
  const chosen: InvPlugin[] = [];
  const gain = (p: InvPlugin) => p.skills.filter((s) => !covered.has(s.name)).length;
  // за однакового покриття виграє плагін, названий як сам репозиторій:
  // «skills-for-fabric» упізнаваніший за рівний йому «fabric-skills»
  const rank = (p: InvPlugin) => (p.name === preferName ? 0 : 1);
  while (covered.size < distinct.size && pool.length) {
    pool.sort((a, b) => gain(b) - gain(a) || rank(a) - rank(b) || a.name.localeCompare(b.name));
    const best = pool.shift()!;
    if (gain(best) === 0) break;
    best.skills.forEach((s) => covered.add(s.name));
    chosen.push(best);
  }
  const takenNames = new Set(chosen.map((p) => p.name));
  return { chosen, rest: plugins.filter((p) => !takenNames.has(p.name)) };
}

/** Підкатегорія скіла за його іменем: набори Microsoft називають скіли
 *  <тема>-<роль>-cli, тож роль читається з імені й ділить довгий список на
 *  осмислені купки. Порожній рядок = категорії немає. */
const CATEGORY_LABELS: Record<string, string> = {
  authoring: "Авторинг",
  consumption: "Споживання",
  operations: "Операції",
  migration: "Міграції",
};

function categoryOf(name: string): string {
  if (name.startsWith("powerbi-")) return "Power BI";
  const parts = name.split("-");
  const last = parts[parts.length - 1] === "cli" ? parts[parts.length - 2] : parts[parts.length - 1];
  return CATEGORY_LABELS[last] ?? "";
}

type Cluster = { label: string; skills: InvSkill[] };

/** Розбивка скілів плагіна по підкатегоріях. Дрібні купки зливаються в «Решту»;
 *  якщо осмислених категорій менше двох, повертає один безіменний блок. */
export function clusterSkills(skills: InvSkill[]): Cluster[] {
  if (skills.length < 10) return [{ label: "", skills }];
  const byCat = new Map<string, InvSkill[]>();
  for (const s of skills) {
    const c = categoryOf(s.name);
    if (!c) continue;
    const list = byCat.get(c) ?? [];
    list.push(s);
    byCat.set(c, list);
  }
  const named = [...byCat.entries()].filter(([, list]) => list.length >= 3);
  if (named.length < 2) return [{ label: "", skills }];
  const takenNames = new Set(named.flatMap(([, list]) => list.map((s) => s.name)));
  const rest = skills.filter((s) => !takenNames.has(s.name));
  const clusters: Cluster[] = named
    .sort((a, b) => b[1].length - a[1].length)
    .map(([label, list]) => ({ label, skills: list }));
  if (rest.length) clusters.push({ label: "Решта", skills: rest });
  return clusters;
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

/** Картка скіла всередині плагіна: команда встановлення НЕ дублюється —
 *  вона одна на весь блок, зверху. Тут лише те, що стосується самого скіла. */
function MarketSkillCard(props: { skill: InvSkill; plugin: InvPlugin }) {
  const { skill, plugin } = props;
  return (
    <div className="skillcard">
      <h3>
        {skill.name} <span className="meta">· входить у {plugin.name}</span>
      </h3>
      {skillTip(skill) && <p className="desc">{skillTip(skill)}</p>}
    </div>
  );
}

function StandaloneSkillCard(props: { skill: InvSkill; source: InvSource }) {
  const { skill, source } = props;
  return (
    <div className="skillcard">
      <h3>{skill.name}</h3>
      {skillTip(skill) && <p className="desc">{skillTip(skill)}</p>}
      {source.repo && source.marketplace && (
        <p className="meta" style={{ margin: 0 }}>
          Ставиться командою підключення маркетплейсу вище, далі <code>/plugin</code> і вибрати
          плагін із цим скілом.
        </p>
      )}
      {source.repo && !source.marketplace && source.dir !== null && (
        <details open>
          <summary>Промпт для Claude Code — забрати цей скіл</summary>
          <CopyRow
            text={standalonePrompt(skill.name, source.repo, source.dir)}
            kind="skill-prompt"
            item={`standalone:${skill.name}`}
          />
        </details>
      )}
      {!source.repo && (
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

/** Чіпи скілів із підкатегоріями; відкрита картка одна на весь блок. */
function SkillChips<T>(props: {
  clusters: Cluster[];
  payload: T;
  groupClass: string;
  trackPrefix: string;
  renderCard: (payload: T, skill: InvSkill) => ReactNode;
}) {
  const { clusters, payload, groupClass, trackPrefix, renderCard } = props;
  const [open, setOpen] = useState<string | null>(null);
  const openSkill = clusters.flatMap((c) => c.skills).find((s) => s.name === open) ?? null;
  return (
    <>
      {clusters.map((c, i) => (
        <div className="subgroup" key={c.label || `c${i}`}>
          {c.label && (
            <p className="sublabel">
              {c.label} <span>· {c.skills.length}</span>
            </p>
          )}
          <div className="chips">
            {c.skills.map((skill) => (
              <button
                key={skill.name}
                className={`chip ${groupClass}${open === skill.name ? " open" : ""}`}
                aria-expanded={open === skill.name}
                data-tip={skillTip(skill) || undefined}
                onClick={() => {
                  const next = open === skill.name ? null : skill.name;
                  setOpen(next);
                  if (next) track("skill-view", `${trackPrefix}:${skill.name}`);
                }}
              >
                {skill.name}
              </button>
            ))}
          </div>
        </div>
      ))}
      {openSkill && renderCard(payload, openSkill)}
    </>
  );
}

/** Розділ маркетплейс-групи (Anthropic / Microsoft / Kurt Buhler) — уже відфільтрованої. */
export function GroupSection(props: { group: InvGroup }) {
  const { group } = props;
  if (group.skillCount === 0) return null;
  const { chosen, rest } = coverPlugins(group.plugins, group.repo?.split("/").pop());
  const counts =
    rest.length > 0
      ? `${pluralSkills(group.uniqueCount)}; джерело пакує їх у ${group.plugins.length} наборів, що перекриваються — нижче ${chosen.length === 1 ? "одна команда" : `${chosen.length} команди`}, що дають усе`
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
            Спершу підключіть маркетплейс (один раз), далі беріть команди з карток нижче:
          </p>
          <CopyRow text={group.addCmd} kind="marketplace" item={group.group} />
        </>
      )}
      <div className="cards-grid">
        {chosen.map((p) => (
          <div className={`plugin inv-${group.group}`} id={`mp-${group.group}-${p.name}`} key={p.name}>
            <div className="plugin-head">
              <h3>{p.name}</h3>
              <span className="tagline">{pluralSkills(p.skills.length)}</span>
            </div>
            {p.short && <p className="plugin-desc">{p.short}</p>}
            <CopyRow text={p.installCmd} kind="plugin" item={`${group.group}:${p.name}`} />
            <SkillChips
              clusters={clusterSkills(p.skills)}
              payload={p}
              groupClass={`g-${group.group}`}
              trackPrefix={group.group}
              renderCard={(plugin, skill) => <MarketSkillCard skill={skill} plugin={plugin} />}
            />
          </div>
        ))}
      </div>
      {rest.length > 0 && (
        <details className="alt-bundles">
          <summary>Ті самі скіли іншими нарізками ({rest.length})</summary>
          <p className="meta">
            Джерело публікує кілька плагінів, що перекриваються: ті самі скіли лежать одразу в
            кількох. Команди вище дають усі {group.uniqueCount}. Ці — підмножини, беріть, якщо
            потрібен саме вужчий зріз.
          </p>
          {rest.map((p) => (
            <div className="alt-row" key={p.name}>
              <span className="meta">
                {p.name} · {pluralSkills(p.skills.length)}
              </span>
              <CopyRow text={p.installCmd} kind="plugin" item={`${group.group}:${p.name}`} />
            </div>
          ))}
        </details>
      )}
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
            <SkillChips
              clusters={clusterSkills(src.skills)}
              payload={src}
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
