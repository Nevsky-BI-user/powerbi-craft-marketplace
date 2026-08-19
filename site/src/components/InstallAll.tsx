import { useState } from "react";
import type { Catalog, Inventory, InvGroup, InvSource } from "../types";
import { CopyBlock } from "./Copy";
import { coverPlugins } from "./InventorySection";
import { pluralSkills } from "./PluginSection";

/** Обсяг встановлення: лише свій маркетплейс чи весь набір, описаний на сторінці. */
export type Scope = "craft" | "all";

function marketGroups(inv: Inventory): InvGroup[] {
  return inv.groups.filter((g) => g.group !== "standalone");
}

/** Імена скілів, які приходять разом із плагінами. */
function pluginSkillNames(cat: Catalog, inv: Inventory): Set<string> {
  const names = new Set<string>();
  cat.plugins.forEach((p) => p.skills.forEach((s) => names.add(s.name)));
  inv.groups.forEach((g) => g.plugins.forEach((p) => p.skills.forEach((s) => names.add(s.name))));
  return names;
}

/** Скільки різних скілів дає повний набір: джерела перетинаються
 *  (той самий superpowers лежить і плагіном, і окремими файлами),
 *  тож рахуємо унікальні імена, а не суму. */
export function totalSkills(cat: Catalog, inv: Inventory): number {
  const names = pluginSkillNames(cat, inv);
  inv.groups.forEach((g) =>
    g.sources?.forEach((s) => s.skills.forEach((k) => names.add(k.name))),
  );
  return names.size;
}

/** Джерела окремих скілів за способом встановлення. Ті, чиї скіли повністю
 *  дублюють уже поставлені плагіни, відпадають: ставити двічі те саме не треба. */
export function standaloneSources(
  cat: Catalog,
  inv: Inventory,
): { markets: InvSource[]; repos: InvSource[]; manual: InvSource[] } {
  const covered = pluginSkillNames(cat, inv);
  const all = inv.groups.find((g) => g.group === "standalone")?.sources ?? [];
  const fresh = all.filter((s) => s.skills.some((k) => !covered.has(k.name)));
  return {
    markets: fresh.filter((s) => s.repo && s.marketplace),
    repos: fresh.filter((s) => s.repo && !s.marketplace && s.dir !== null),
    manual: fresh.filter((s) => !s.repo || (!s.marketplace && s.dir === null)),
  };
}

function craftLines(cat: Catalog): string[] {
  return [
    `claude plugin marketplace add ${cat.marketplace.repo}`,
    ...cat.plugins.map((p) => `claude plugin install ${p.name}@${cat.marketplace.name}`),
  ];
}

/** Скрипт без башевої граматики: самі команди й рядки коментарів, які однаково
 *  розуміють cmd-подібні оболонки, PowerShell і zsh. */
export function terminalScript(cat: Catalog, inv: Inventory, scope: Scope): string {
  if (scope === "craft") return craftLines(cat).join("\n") + "\n";

  const out = [`# powerbi-craft — ${cat.totals.plugins} плагінів`, ...craftLines(cat)];
  for (const g of marketGroups(inv)) {
    const { chosen } = coverPlugins(g.plugins, g.repo?.split("/").pop());
    out.push("", g.addCmd ? `# ${g.title}` : `# ${g.title}: підключати не треба, він уже в Claude Code`);
    if (g.addCmd) out.push(g.addCmd);
    out.push(...chosen.map((p) => p.installCmd));
  }
  const { markets } = standaloneSources(cat, inv);
  if (markets.length) {
    out.push("", "# джерела окремих скілів: підключити, далі /plugin → вибрати потрібні");
    out.push(...markets.map((s) => `claude plugin marketplace add ${s.repo}`));
  }
  return out.join("\n") + "\n";
}

/** Звірка з уже встановленим — те, чого не вміє термінальний скрипт: агент
 *  бачить середовище користувача, тож перед встановленням шукає перекриття
 *  і питає, що робити з кожним дублем. */
const DEDUPE_STEP =
  `Перш ніж щось ставити, звір список із тим, що в мене вже є: подивись claude plugin list ` +
  `і теки в ~/.claude/skills. Якщо скіл, який збираєшся поставити, вже стоїть — окремою текою ` +
  `чи в складі іншого плагіна (та сама назва або явно те саме призначення за description ` +
  `у SKILL.md) — не встановлюй мовчки поруч. Покажи мені кожну таку пару (що вже стоїть, ` +
  `що прийде, чим відрізняються) і спитай, що робити: змерджити в один (перенести мої ` +
  `локальні доповнення й прибрати зайву копію), залишити обидва чи замінити старе новим. ` +
  `Зроби, як я виберу, і лише потім став решту.`;

function craftPrompt(cat: Catalog): string {
  const names = cat.plugins.map((p) => p.name).join(", ");
  return (
    `Підключи маркетплейс Claude Code плагінів і встанови всі його плагіни:\n` +
    `1. Виконай: claude plugin marketplace add ${cat.marketplace.repo}\n` +
    `2. ${DEDUPE_STEP}\n` +
    `3. Встанови всі плагіни (кількість: ${cat.plugins.length}): ${names} — ` +
    `кожен командою claude plugin install <назва>@${cat.marketplace.name}\n` +
    `4. Перевір командою claude plugin list, що зʼявились усі (${cat.plugins.length} шт.) і мають статус enabled.\n` +
    `5. Скіли з різних плагінів посилаються один на одного, тому потрібен повний набір — не пропускай плагіни.\n` +
    `6. Наприкінці нагадай мені вручну увімкнути автооновлення: /plugin → Marketplaces → ` +
    `${cat.marketplace.name} → Enable auto-update (для сторонніх маркетплейсів воно вимкнене за замовчуванням).`
  );
}

function fullPrompt(cat: Catalog, inv: Inventory): string {
  const { markets, repos } = standaloneSources(cat, inv);
  const steps: string[] = [
    DEDUPE_STEP,
    `Підключи маркетплейс ${cat.marketplace.repo} і встанови всі ${cat.plugins.length} плагінів ` +
      `(${cat.plugins.map((p) => p.name).join(", ")}) командами ` +
      `claude plugin install <назва>@${cat.marketplace.name}.`,
  ];
  for (const g of marketGroups(inv)) {
    const { chosen } = coverPlugins(g.plugins, g.repo?.split("/").pop());
    const add = g.addCmd ? `виконай ${g.addCmd}, далі ` : "маркетплейс уже вбудований, підключати не треба, тож просто ";
    steps.push(
      `${g.title}: ${add}постав плагіни ` +
        `${chosen.map((p) => p.installCmd.replace("claude plugin install ", "")).join(", ")} ` +
        `(команда claude plugin install <назва>@<маркетплейс>).`,
    );
  }
  if (markets.length) {
    const list = markets
      .map((s) => `${s.repo} (скіли: ${s.skills.map((k) => k.name).join(", ")})`)
      .join("; ");
    steps.push(
      `Ці репозиторії теж маркетплейси, але потрібні скіли лежать у різних плагінах. ` +
        `Для кожного виконай claude plugin marketplace add <репозиторій>, подивись список плагінів ` +
        `(claude plugin list або файл .claude-plugin/marketplace.json у репозиторії) і постав ті, ` +
        `що містять названі скіли: ${list}.`,
    );
  }
  if (repos.length) {
    const list = repos
      .map(
        (s) =>
          `github.com/${s.repo}${s.dir ? `, тека ${s.dir}/` : ""} — ` +
          `${s.skills.map((k) => k.name).join(", ")}`,
      )
      .join("; ");
    steps.push(
      `Ці скіли лежать у звичайних репозиторіях без маркетплейсу. Для кожного зроби sparse checkout ` +
        `теки скіла і скопіюй її вміст у ~/.claude/skills/<назва скіла>/, перевіривши, що SKILL.md ` +
        `на місці: ${list}.`,
    );
  }
  steps.push(
    `Перевір результат: claude plugin list — усі плагіни зі статусом enabled; ` +
      `у ~/.claude/skills — теки скілів зі SKILL.md. Покажи, чого не вдалося поставити.`,
  );
  steps.push(
    `Наприкінці нагадай мені увімкнути автооновлення вручну: /plugin → Marketplaces → ` +
      `${cat.marketplace.name} → Enable auto-update (для сторонніх маркетплейсів воно вимкнене за замовчуванням).`,
  );
  return (
    `Постав мені повний набір Claude Code з каталогу powerbi-craft: плагіни з кількох ` +
    `маркетплейсів плюс кілька окремих скілів. Роби по кроках і не пропускай пункти.\n\n` +
    steps.map((s, i) => `${i + 1}. ${s}`).join("\n") +
    `\n\nЦе весь список. Якщо якийсь плагін чи скіл не знайдеться, так і скажи, ` +
    `не заміняй його схожим.`
  );
}

export function agentPrompt(cat: Catalog, inv: Inventory, scope: Scope): string {
  return scope === "craft" ? craftPrompt(cat) : fullPrompt(cat, inv);
}

export function InstallAll(props: { catalog: Catalog; inventory: Inventory }) {
  const { catalog, inventory } = props;
  const [scope, setScope] = useState<Scope>("all");
  const [tab, setTab] = useState<"term" | "prompt">("term");
  const { repos, manual } = standaloneSources(catalog, inventory);
  const loose = repos.reduce((n, s) => n + s.skills.length, 0);
  const manualCount = manual.reduce((n, s) => n + s.skills.length, 0);
  const text =
    tab === "term"
      ? terminalScript(catalog, inventory, scope)
      : agentPrompt(catalog, inventory, scope);
  return (
    <section id="install-all">
      <h2>Встановити все одразу</h2>
      <div className="tabs" role="group" aria-label="Обсяг встановлення">
        <button className={scope === "all" ? "tab active" : "tab"}
          aria-pressed={scope === "all"} onClick={() => setScope("all")}>
          Усе з цієї сторінки · {pluralSkills(totalSkills(catalog, inventory))}
        </button>
        <button className={scope === "craft" ? "tab active" : "tab"}
          aria-pressed={scope === "craft"} onClick={() => setScope("craft")}>
          Тільки powerbi-craft · {pluralSkills(catalog.totals.skills)}
        </button>
      </div>
      <p style={{ color: "var(--text2)", fontSize: 14 }}>
        {scope === "craft" ? (
          <>
            Повний набір powerbi-craft: скіли з різних плагінів посилаються один на одного,
            тож повну силу дає лише повний комплект.
          </>
        ) : (
          <>
            Той самий powerbi-craft плюс набори Anthropic, Microsoft і Kurt Buhler та окремі
            скіли — усе, що описане вище на сторінці, одним заходом.
          </>
        )}
      </p>
      <p className="note">
        Термінал і промпт — два способи зробити те саме, а не два кроки, оберіть один.
        Термінал простіший: вставили рядки — все поставилось як є. Промпт для агента
        розумніший: перш ніж ставити, він звірить набір із уже встановленим у вас і про
        кожен дубль спитає, що робити — змерджити, залишити обидва чи замінити.
      </p>
      <div className="tabs" role="group" aria-label="Спосіб встановлення">
        <button className={tab === "term" ? "tab active" : "tab"}
          aria-pressed={tab === "term"} onClick={() => setTab("term")}>
          Термінал
        </button>
        <span className="or">або</span>
        <button className={tab === "prompt" ? "tab active" : "tab"}
          aria-pressed={tab === "prompt"} onClick={() => setTab("prompt")}>
          Промпт для Claude Code / Codex
        </button>
      </div>
      <CopyBlock text={text} kind={tab === "term" ? "all-terminal" : "all-prompt"} item={scope} />
      {scope === "all" && tab === "term" && (
        <p style={{ color: "var(--text2)", fontSize: 13.5 }}>
          Командами ставиться все, що лежить у маркетплейсах. Ще {pluralSkills(loose)} живуть
          у звичайних репозиторіях і потребують git — їх забирає промпт із сусідньої вкладки.
          У решти ({manualCount}) готового джерела немає зовсім: промпт для кожного лежить на
          його картці в розділі «Окремі скіли».
        </p>
      )}
    </section>
  );
}
