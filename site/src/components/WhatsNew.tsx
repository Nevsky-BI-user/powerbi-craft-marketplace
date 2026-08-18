import type { ChangelogEntry } from "../types";

export function WhatsNew(props: { entries: ChangelogEntry[] }) {
  if (props.entries.length === 0) return null;
  const [head, ...rest] = props.entries;
  return (
    <section id="whats-new">
      <h2>Що нового</h2>
      <Release entry={head} />
      {rest.length > 0 && (
        <details>
          <summary style={{ cursor: "pointer", color: "var(--accent)", fontSize: 14 }}>
            Попередні релізи ({rest.length})
          </summary>
          {rest.map((e) => (
            <Release key={e.version} entry={e} />
          ))}
        </details>
      )}
    </section>
  );
}

function Release(props: { entry: ChangelogEntry }) {
  const e = props.entry;
  return (
    <div className="release">
      <h3>
        {e.version} <span className="date">— {e.date}</span>
      </h3>
      {e.title && <p style={{ margin: "6px 0 0", fontSize: 14 }}>{e.title}</p>}
      {e.items.length > 0 && (
        <ul>
          {e.items.map((it, i) => (
            <li key={i}>{it}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
