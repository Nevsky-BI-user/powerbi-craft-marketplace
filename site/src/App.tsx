import { useEffect, useMemo, useRef, useState } from "react";
import catalogJson from "./catalog.json";
import inventoryJson from "./inventory.json";
import type { Catalog, Inventory, Plugin } from "./types";
import { CopyRow } from "./components/Copy";
import { PluginSection, pluralSkills } from "./components/PluginSection";
import { GroupSection, StandaloneSection, GROUP_LABELS, filterInvGroup } from "./components/InventorySection";
import { InstallAll } from "./components/InstallAll";
import { HowTo } from "./components/HowTo";
import { WhatsNew } from "./components/WhatsNew";
import { fetchCounts, topSkills, telemetryOn, track } from "./telemetry";

const catalog = catalogJson as Catalog;
const inventory = inventoryJson as Inventory;

const SECTION_IDS = [
  "powerbi-craft", "anthropic", "microsoft", "goblin", "standalone", "install-all", "how-to",
];

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

  // Підсвітка активного розділу в навігації
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const hit = entries.find((e) => e.isIntersecting);
        if (hit) setActiveSection(hit.target.id);
      },
      { rootMargin: "-96px 0px -75% 0px" },
    );
    for (const id of SECTION_IDS) {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    }
    return () => observer.disconnect();
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
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    setActiveSection(id);
  };

  const mp = catalog.marketplace;
  const hookPlugins = catalog.plugins.filter((p) => p.hasHooks).length;
  const agentCount = catalog.plugins.reduce((n, p) => n + p.agents.length, 0);

  // Загальні цифри середовища (шапка)
  const invUnique = inventory.groups.reduce((n, g) => n + g.uniqueCount, 0);
  const totalSkills = catalog.totals.skills + invUnique;
  const totalPlugins =
    catalog.totals.plugins + inventory.groups.reduce((n, g) => n + g.plugins.length, 0);
  const standaloneGroup = inventory.groups.find((g) => g.group === "standalone");
  const sourceRepos = standaloneGroup?.sources?.filter((s) => s.repo).length ?? 0;
  const totalSources = 1 + inventory.groups.filter((g) => g.repo).length + sourceRepos;

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

  return (
    <div className="container">
      <header className="hero" id="top">
        <h1>{mp.name}</h1>
        <p className="sub">{mp.description}</p>
        <div className="metrics">
          <div className="metric">
            <div className="label">скілів у середовищі</div>
            <div className="value">{totalSkills}</div>
          </div>
          <div className="metric">
            <div className="label">з них powerbi-craft</div>
            <div className="value">{catalog.totals.skills}</div>
          </div>
          <div className="metric">
            <div className="label">плагінів</div>
            <div className="value">{totalPlugins}</div>
          </div>
          <div className="metric">
            <div className="label">джерел встановлення</div>
            <div className="value">{totalSources}</div>
          </div>
        </div>
        <p className="snapshot">
          Один каталог — усе середовище Claude Code автора. Розділ powerbi-craft оновлюється
          автоматично з кожним пушем; решта — знімок від {inventory.snapshotDate}.
        </p>
        <CopyRow text={`claude plugin marketplace add ${mp.repo}`} kind="marketplace" item="hero" />
      </header>

      <nav className="topnav" aria-label="Розділи каталогу">
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
          placeholder="Пошук у всіх розділах: назва, опис або тригер — «зебра», «fabric», «tdd»… (клавіша /)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Пошук скілів"
        />
        {q && (
          <p className="search-hint">
            {totalFound
              ? `Знайдено скілів: ${totalFound}`
              : "Нічого не знайдено — спробуйте інше слово"}
          </p>
        )}
      </nav>

      <section id="powerbi-craft">
        <h2>powerbi-craft — плагіни та скіли</h2>
        <p className="section-intro">
          Маркетплейс автора: {catalog.totals.plugins} плагінів, {pluralSkills(catalog.totals.skills)},{" "}
          {agentCount} субагенти, {hookPlugins} плагін із хуком автоперевірки.
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
      <HowTo catalog={catalog} />
      <WhatsNew entries={catalog.changelog} />

      {showTop && (
        <button className="totop" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          ↑ Нагору
        </button>
      )}

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
  );
}
