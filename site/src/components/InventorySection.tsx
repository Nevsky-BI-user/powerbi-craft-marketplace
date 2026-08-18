import { useState } from "react";
import type { InvGroup, InvPlugin, InvSkill, Inventory } from "../types";
import { CopyRow } from "./Copy";
import { track } from "../telemetry";

const GROUP_LABELS: Record<InvGroup["group"], string> = {
  anthropic: "Anthropic",
  microsoft: "Microsoft",
  goblin: "Kurt Buhler",
  standalone: "окремі",
  project: "проєктні",
};

function matches(q: string, s: InvSkill): boolean {
  return s.name.toLowerCase().includes(q) || s.short.toLowerCase().includes(q);
}

function SkillMiniCard(props: { skill: InvSkill; group: InvGroup; plugin?: InvPlugin }) {
  const { skill, group, plugin } = props;
  return (
    <div className="skillcard">
      <h3>{skill.name}</h3>
      {skill.short && <p className="desc">{skill.short}</p>}
      {plugin && <CopyRow text={plugin.installCmd} kind="plugin" item={`${group.group}:${plugin.name}`} />}
      {skill.source && (
        <p className="meta" style={{ margin: "8px 0 0" }}>
          Джерело: <a href={`https://github.com/${skill.source}`} target="_blank" rel="noreferrer">{skill.source}</a>
        </p>
      )}
      {!plugin && !skill.source && (
        <p className="meta" style={{ margin: "8px 0 0" }}>
          Публічного інсталятора немає — скіл живе локально на машині автора.
        </p>
      )}
    </div>
  );
}

function GroupBlock(props: { group: InvGroup; q: string }) {
  const { group, q } = props;
  const [open, setOpen] = useState<string | null>(null);
  const flat: { skill: InvSkill; plugin?: InvPlugin }[] = [
    ...group.plugins.flatMap((p) => p.skills.map((s) => ({ skill: s, plugin: p }))),
    ...(group.skills ?? []).map((s) => ({ skill: s, plugin: undefined })),
  ].filter((e) => !q || matches(q, e.skill));
  if (q && flat.length === 0) return null;
  const openEntry = flat.find((e) => `${e.plugin?.name ?? "-"}/${e.skill.name}` === open) ?? null;
  const counts =
    group.uniqueCount !== group.skillCount
      ? `${group.skillCount} скілів (${group.uniqueCount} унікальних — плагіни-набори перекриваються)`
      : `${group.skillCount} скілів`;
  return (
    <section className={`plugin inv-${group.group}`}>
      <div className="plugin-head">
        <h3>{group.title}</h3>
        <span className={`badge gdot g-${group.group}`}>{GROUP_LABELS[group.group]}</span>
        <span className="tagline">{counts}</span>
      </div>
      {group.repo && (
        <p className="plugin-desc">
          <a href={`https://github.com/${group.repo}`} target="_blank" rel="noreferrer">
            github.com/{group.repo}
          </a>
        </p>
      )}
      {group.addCmd && <CopyRow text={group.addCmd} kind="marketplace" item={group.group} />}
      {group.group === "anthropic" && (
        <p className="plugin-desc">
          Офіційний маркетплейс уже підключений у кожному Claude Code — окрема команда
          не потрібна. Вбудовані скіли застосунку (docx, pptx, xlsx тощо) сюди не входять:
          вони — частина самого Claude, а не встановлення.
        </p>
      )}
      {group.group === "project" && (
        <p className="plugin-desc">
          Живуть у приватних робочих репозиторіях поряд із кодом — показані для повноти
          карти, встановити їх ззовні не можна.
        </p>
      )}
      <div className="chips">
        {flat.map(({ skill, plugin }) => {
          const key = `${plugin?.name ?? "-"}/${skill.name}`;
          return (
            <button
              key={key}
              className={`chip g-${group.group}${open === key ? " open" : ""}`}
              aria-expanded={open === key}
              onClick={() => {
                const next = open === key ? null : key;
                setOpen(next);
                if (next) track("skill-view", `${group.group}:${skill.name}`);
              }}
            >
              {skill.name}
            </button>
          );
        })}
      </div>
      {openEntry && <SkillMiniCard skill={openEntry.skill} group={group} plugin={openEntry.plugin} />}
    </section>
  );
}

export function InventorySection(props: { inventory: Inventory; q: string }) {
  const { inventory, q } = props;
  return (
    <section id="environment">
      <h2>Решта середовища: всі скіли цієї машини</h2>
      <p style={{ color: "var(--text2)", fontSize: 14, maxWidth: 680 }}>
        powerbi-craft не працює у вакуумі. Це знімок повного набору скілів робочої машини
        автора станом на {inventory.snapshotDate} — з командами підключення там, де джерело
        публічне. Кожна група — своїм кольором.
      </p>
      <p className="legend">
        {inventory.groups.map((g) => (
          <span key={g.group} className={`chip g-${g.group} legend-chip`}>
            {GROUP_LABELS[g.group]} · {g.uniqueCount}
          </span>
        ))}
        <span className="chip legend-chip">powerbi-craft · 51</span>
      </p>
      {inventory.groups.map((g) => (
        <GroupBlock key={g.group} group={g} q={q} />
      ))}
    </section>
  );
}
