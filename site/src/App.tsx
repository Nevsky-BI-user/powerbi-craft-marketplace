import { useEffect, useMemo, useRef, useState } from "react";
import catalogJson from "./catalog.json";
import inventoryJson from "./inventory.json";
import type { Catalog, Inventory, Plugin } from "./types";
import { CopyButton } from "./components/Copy";
import { PluginSection, PLUGIN_ICONS, pluralSkills } from "./components/PluginSection";
import { GroupSection, StandaloneSection, GROUP_LABELS, filterInvGroup, coverPlugins } from "./components/InventorySection";
import { InstallAll } from "./components/InstallAll";
import { Requirements } from "./components/Requirements";
import { HowTo } from "./components/HowTo";
import { WhatsNew } from "./components/WhatsNew";
import { fetchCounts, topSkills, telemetryOn, track } from "./telemetry";

const catalog = catalogJson as Catalog;
const inventory = inventoryJson as Inventory;

const SECTION_IDS = [
  "powerbi-craft", "anthropic", "microsoft", "goblin", "standalone",
  "install-all", "requirements", "how-to",
];

const SECTION_INFO: Record<string, { icon: string; title: string; desc: string }> = {
  "powerbi-craft": {
    icon: "🧰",
    title: "powerbi-craft",
    desc: "Power BI / Fabric report-craft skills: visuals, report UX, design language, quality gates, DAX, PBIP devops, data storytelling.",
  },
  anthropic: {
    icon: "📦",
    title: "Бандл Anthropic",
    desc: "Plugins from the official Claude Code marketplace: setup, skill authoring, frontend design, superpowers.",
  },
  microsoft: {
    icon: "🧱",
    title: "Microsoft skills-for-fabric",
    desc: "Microsoft Skills for Fabric: Spark, warehouses, event streams, real-time intelligence, CLI automation.",
  },
  goblin: {
    icon: "👺",
    title: "Kurt Buhler (data-goblin)",
    desc: "Agentic Power BI development: semantic models, PBIR reports, Tabular Editor, DAX.",
  },
  standalone: {
    icon: "🧩",
    title: "Окремі скіли",
    desc: "Скіли, що живуть просто в ~/.claude/skills. Згруповані за репозиторіями, з яких їх можна поставити й собі.",
  },
  "install-all": {
    icon: "⚡",
    title: "Встановити все",
    desc: "Скрипт для термінала або промпт для агента, і весь powerbi-craft ставиться за раз.",
  },
  requirements: {
    icon: "🖥️",
    title: "Що потрібно системі",
    desc: "Що працює всюди, де потрібен python 3, а що тримається Windows разом із Power BI Desktop.",
  },
  "how-to": {
    icon: "📖",
    title: "Як почати",
    desc: "Пʼять кроків від чистого Claude Code до робочого набору, включно з автооновленням.",
  },
};

const UK_MONTHS = [
  "січня", "лютого", "березня", "квітня", "травня", "червня",
  "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
];

function ukDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  return `${d} ${UK_MONTHS[m - 1]} ${y}`;
}

function matches(q: string, hay: string): boolean {
  return hay.toLowerCase().includes(q);
}

function filterPlugin(p: Plugin, q: string): Plugin | null {
  if (!q) return p;
  if (matches(q, p.name) || matches(q, p.description)) return p;
  const skills = p.skills.filter(
    (s) =>
      matches(q, s.name) ||
      matches(q, s.description) ||
      (s.shortUk ? matches(q, s.shortUk) : false) ||
      s.triggers.some((t) => matches(q, t)),
  );
  return skills.length ? { ...p, skills } : null;
}

export default function App() {
  const [query, setQuery] = useState("");
  const [openSkill, setOpenSkill] = useState<string | null>(
    () => window.location.hash.slice(1) || null,
  );
  const [popular, setPopular] = useState<Set<string>>(new Set());
  const [activeSection, setActiveSection] = useState<string>("powerbi-craft");
  const [showTop, setShowTop] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const navRef = useRef<HTMLElement>(null);

  // Висота липкої навігації в --navh: від неї залежать відступ якорів
  // (scroll-margin-top) і поріг, за яким розділ вважається активним
  useEffect(() => {
    const el = navRef.current;
    if (!el) return;
    const set = () => {
      const h = Math.round(el.getBoundingClientRect().height);
      document.documentElement.style.setProperty("--navh", `${h}px`);
    };
    set();
    const ro = new ResizeObserver(set);
    ro.observe(el);
    window.addEventListener("resize", set);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", set);
    };
  }, []);

  useEffect(() => {
    fetchCounts().then((c) => setPopular(topSkills(c, 5)));
  }, []);

  useEffect(() => {
    const onHash = () => setOpenSkill(window.location.hash.slice(1) || null);
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    const target = window.location.hash.slice(1);
    if (target) document.getElementById(target)?.scrollIntoView({ block: "center" });
  }, []);

  // Активний розділ — обчислення від прокрутки (стійкіше за IntersectionObserver
  // у вбудованих/емульованих переглядачах): останній розділ, чий верх зайшов під навігацію
  useEffect(() => {
    const compute = () => {
      const navH = navRef.current?.getBoundingClientRect().height ?? 128;
      const line = navH + 42;
      let current = SECTION_IDS[0];
      for (const id of SECTION_IDS) {
        const el = document.getElementById(id);
        if (!el) continue;
        if (el.getBoundingClientRect().top <= line) current = id;
        else break;
      }
      setActiveSection((prev) => (prev === current ? prev : current));
    };
    compute();
    window.addEventListener("scroll", compute, { passive: true });
    window.addEventListener("resize", compute);
    return () => {
      window.removeEventListener("scroll", compute);
      window.removeEventListener("resize", compute);
    };
  }, []);

  // «/» фокусує пошук; кнопка «нагору» після прокрутки
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement;
      if (e.key === "/" && t.tagName !== "INPUT" && t.tagName !== "TEXTAREA") {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    const onScroll = () => setShowTop(window.scrollY > 600);
    window.addEventListener("keydown", onKey);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  const q = query.trim().toLowerCase();
  const visible = useMemo(
    () => catalog.plugins.map((p) => filterPlugin(p, q)).filter((p): p is Plugin => p !== null),
    [q],
  );
  const pbFound = visible.reduce((n, p) => n + p.skills.length, 0);
  const invFiltered = useMemo(
    () => inventory.groups.map((g) => filterInvGroup(g, q)),
    [q],
  );
  const totalFound = pbFound + invFiltered.reduce((n, g) => n + g.uniqueCount, 0);

  const toggle = (name: string) => {
    const next = openSkill === name ? null : name;
    setOpenSkill(next);
    if (next) track("skill-view", next);
    history.replaceState(null, "", next ? `#${next}` : window.location.pathname);
  };

  const goTo = (id: string) => {
    const el = document.getElementById(id);
    if (!el) return;
    const margin = parseFloat(getComputedStyle(el).scrollMarginTop) || 0;
    window.scrollTo({
      top: window.scrollY + el.getBoundingClientRect().top - margin,
      behavior: "smooth",
    });
    if (SECTION_IDS.includes(id)) {
      setActiveSection(id);
      return;
    }
    // Вибір конкретного плагіна: підсвічуємо картку, інакше клік виглядає як промах
    el.classList.remove("flash");
    void el.offsetWidth;
    el.classList.add("flash");
    window.setTimeout(() => el.classList.remove("flash"), 1900);
  };

  const mp = catalog.marketplace;
  const hookPlugins = catalog.plugins.filter((p) => p.hasHooks).length;
  const agentCount = catalog.plugins.reduce((n, p) => n + p.agents.length, 0);

  const groupCount = (id: string): number => {
    if (id === "powerbi-craft") return q ? pbFound : catalog.totals.skills;
    const g = (q ? invFiltered : inventory.groups).find((x) => x.group === id);
    return g?.uniqueCount ?? 0;
  };
  const navItems = [
    { id: "powerbi-craft", label: "powerbi-craft", cls: "" },
    { id: "anthropic", label: GROUP_LABELS.anthropic, cls: "g-anthropic" },
    { id: "microsoft", label: GROUP_LABELS.microsoft, cls: "g-microsoft" },
    { id: "goblin", label: GROUP_LABELS.goblin, cls: "g-goblin" },
    { id: "standalone", label: "Окремі", cls: "g-standalone" },
  ];

  // Контекст активного розділу для бічної панелі та мобільного рядка
  const info = SECTION_INFO[activeSection] ?? SECTION_INFO["powerbi-craft"];
  const activeGroup = inventory.groups.find((g) => g.group === activeSection);
  const skillSection = ["powerbi-craft", "anthropic", "microsoft", "goblin", "standalone"].includes(activeSection);
  const ctxRepo = activeSection === "powerbi-craft" ? mp.repo : activeGroup?.repo ?? null;
  const ctxInstall =
    activeSection === "powerbi-craft"
      ? `claude plugin marketplace add ${mp.repo}`
      : activeGroup?.addCmd ?? null;
  const filteredGroup = invFiltered.find((g) => g.group === activeSection);
  const toc: { label: string; anchor: string; tip?: string }[] =
    activeSection === "powerbi-craft"
      ? visible.map((p) => ({
          label: `${PLUGIN_ICONS[p.name] ?? "🧩"} ${p.name.replace(/^pbi-/, "")}`,
          anchor: `p-${p.name}`,
          tip: p.description,
        }))
      : activeSection === "standalone"
        ? (filteredGroup?.sources ?? []).map((s) => ({
            label: s.title,
            anchor: `src-${s.id}`,
            tip: `${pluralSkills(s.skills.length)}${s.repo ? ` · github.com/${s.repo}` : ""}`,
          }))
        : coverPlugins(filteredGroup?.plugins ?? [], activeGroup?.repo?.split("/").pop()).chosen.map((p) => ({
            label: p.name,
            anchor: `mp-${activeSection}-${p.name}`,
            tip: p.short,
          }));

  return (
    <div className="container">
      <header className="hero" id="top">
        <h1>Каталог скілів Claude Code</h1>
        <p className="sub">
          Тут зібрано ціле робоче середовище Claude Code: powerbi-craft, набори Anthropic,
          Microsoft і Kurt Buhler та півсотні окремих скілів. Наведіть курсор на скіл, щоб
          побачити, що він робить; команда чи промпт встановлення лежить поруч. Знімок
          від {ukDate(inventory.snapshotDate)}.
        </p>
      </header>

      <nav className="topnav" aria-label="Розділи каталогу" ref={navRef}>
        <div className="navline">
          <div className="navrow">
            {navItems.map((n) => {
              const count = groupCount(n.id);
              return (
                <button
                  key={n.id}
                  className={`chip navchip ${n.cls}${activeSection === n.id ? " active" : ""}${count === 0 ? " dim" : ""}`}
                  onClick={() => goTo(n.id)}
                >
                  {n.label} · {count}
                </button>
              );
            })}
            <button
              className={`chip navchip quiet${activeSection === "install-all" ? " active" : ""}`}
              onClick={() => goTo("install-all")}
            >
              Встановити все
            </button>
            <button
              className={`chip navchip quiet${activeSection === "requirements" ? " active" : ""}`}
              onClick={() => goTo("requirements")}
            >
              Вимоги
            </button>
            <button
              className={`chip navchip quiet${activeSection === "how-to" ? " active" : ""}`}
              onClick={() => goTo("how-to")}
            >
              Як почати
            </button>
          </div>
          <input
            ref={searchRef}
            type="search"
            className="search"
            placeholder="Пошук: назва, опис або тригер… (клавіша /)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Пошук скілів"
          />
        </div>
        {q && (
          <p className="search-hint">
            {totalFound
              ? `Знайдено скілів: ${totalFound}`
              : "Нічого не знайдено — спробуйте інше слово"}
          </p>
        )}

        <div className="sectionband" aria-label="Активний розділ">
          <span className="band-ico" aria-hidden="true">{info.icon}</span>
          <div className="band-main">
            <div className="band-title">
              <b>{info.title}</b>
              {skillSection && <span className="band-cnt">{pluralSkills(groupCount(activeSection))}</span>}
              {activeSection === "powerbi-craft" && (
                <span className="band-cnt">
                  {agentCount} субагенти · {hookPlugins} плагін із хуком
                </span>
              )}
              {ctxRepo && (
                <a href={`https://github.com/${ctxRepo}`} target="_blank" rel="noreferrer">
                  github.com/{ctxRepo}
                </a>
              )}
            </div>
            {/* Опис показуємо там, де немає переліку плагінів: у розділі зі списком
                корисніший сам список, а опис лишається вступом на початку розділу */}
            {toc.length === 0 && <p className="band-desc">{info.desc}</p>}
            {toc.length > 0 && (
              <div className="bandchips">
                {toc.map((t) => (
                  <button
                    key={t.anchor}
                    className="chip bandchip"
                    data-tip={t.tip || undefined}
                    onClick={() => goTo(t.anchor)}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            )}
          </div>
          {ctxInstall && (
            <div className="band-copy" title={ctxInstall}>
              <span className="band-cnt">команда підключення</span>
              <CopyButton text={ctxInstall} kind="marketplace" item={`band:${activeSection}`} />
            </div>
          )}
        </div>
      </nav>

      <div className="content">
          <section id="powerbi-craft">
            <h2>powerbi-craft — плагіни та скіли</h2>
            <p className="section-intro">
              Девʼять плагінів і {pluralSkills(catalog.totals.skills)}, а з ними {agentCount} субагенти-ревʼюери
              та хук автоперевірки звіту. Найкраще ставити все разом: скіли посилаються один на одного.
            </p>
            <div className="cards-grid">
              {visible.map((p) => (
                <PluginSection
                  key={p.name}
                  plugin={p}
                  repo={mp.repo}
                  mpName={mp.name}
                  openSkill={openSkill}
                  onToggle={toggle}
                  popular={popular}
                />
              ))}
            </div>
          </section>

          {invFiltered
            .filter((g) => g.group !== "standalone")
            .map((g) => (
              <GroupSection key={g.group} group={g} />
            ))}
          {(() => {
            const st = invFiltered.find((g) => g.group === "standalone");
            return st ? <StandaloneSection group={st} /> : null;
          })()}

          <InstallAll catalog={catalog} />
          <Requirements />
          <HowTo catalog={catalog} />
          <WhatsNew entries={catalog.changelog} />

          <footer>
            <p>
              <a href={`https://github.com/${mp.repo}`} target="_blank" rel="noreferrer">
                github.com/{mp.repo}
              </a>{" "}
              · MIT · зібрано автоматично з метаданих скілів
              {telemetryOn ? " · лічильники: анонімні події копіювань і відкриттів карток скілів" : ""}
            </p>
          </footer>
      </div>

      {showTop && (
        <button className="totop" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          ↑ Нагору
        </button>
      )}
    </div>
  );
}
