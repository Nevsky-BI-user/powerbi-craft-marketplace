import { useEffect, useMemo, useState } from "react";
import catalogJson from "./catalog.json";
import type { Catalog, Plugin } from "./types";
import { CopyRow } from "./components/Copy";
import { PluginSection } from "./components/PluginSection";
import { InstallAll } from "./components/InstallAll";
import { HowTo } from "./components/HowTo";
import { WhatsNew } from "./components/WhatsNew";
import { fetchCounts, topSkills, telemetryOn, track } from "./telemetry";

const catalog = catalogJson as Catalog;

function matches(q: string, hay: string): boolean {
  return hay.toLowerCase().includes(q);
}

function filterPlugin(p: Plugin, q: string): Plugin | null {
  if (!q) return p;
  if (matches(q, p.name) || matches(q, p.description)) return p;
  const skills = p.skills.filter(
    (s) => matches(q, s.name) || matches(q, s.description) || s.triggers.some((t) => matches(q, t)),
  );
  return skills.length ? { ...p, skills } : null;
}

export default function App() {
  const [query, setQuery] = useState("");
  const [openSkill, setOpenSkill] = useState<string | null>(
    () => window.location.hash.slice(1) || null,
  );
  const [popular, setPopular] = useState<Set<string>>(new Set());

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

  const q = query.trim().toLowerCase();
  const visible = useMemo(
    () => catalog.plugins.map((p) => filterPlugin(p, q)).filter((p): p is Plugin => p !== null),
    [q],
  );
  const found = visible.reduce((n, p) => n + p.skills.length, 0);

  const toggle = (name: string) => {
    const next = openSkill === name ? null : name;
    setOpenSkill(next);
    if (next) track("skill-view", next);
    history.replaceState(null, "", next ? `#${next}` : window.location.pathname);
  };

  const mp = catalog.marketplace;
  const hookPlugins = catalog.plugins.filter((p) => p.hasHooks).length;
  const agentCount = catalog.plugins.reduce((n, p) => n + p.agents.length, 0);

  return (
    <div className="container">
      <header className="hero">
        <h1>{mp.name}</h1>
        <p className="sub">{mp.description}</p>
        <div className="metrics">
          <div className="metric">
            <div className="label">плагінів</div>
            <div className="value">{catalog.totals.plugins}</div>
          </div>
          <div className="metric">
            <div className="label">скілів</div>
            <div className="value">{catalog.totals.skills}</div>
          </div>
          <div className="metric">
            <div className="label">субагентів</div>
            <div className="value">{agentCount}</div>
          </div>
          <div className="metric">
            <div className="label">плагінів із хуками</div>
            <div className="value">{hookPlugins}</div>
          </div>
        </div>
        <CopyRow text={`claude plugin marketplace add ${mp.repo}`} kind="marketplace" item="hero" />
      </header>

      <section>
        <h2>Плагіни та скіли</h2>
        <input
          type="search"
          className="search"
          placeholder="Пошук: назва, опис або тригер — «зебра», «bookmark», «воронка»…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Пошук скілів"
        />
        {q && (
          <p className="search-hint">
            {found ? `Знайдено скілів: ${found}` : "Нічого не знайдено — спробуйте інше слово"}
          </p>
        )}
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
      </section>

      <InstallAll catalog={catalog} />
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
  );
}
