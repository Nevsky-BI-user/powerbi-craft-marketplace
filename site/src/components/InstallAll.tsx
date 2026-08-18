import { useState } from "react";
import type { Catalog } from "../types";
import { CopyBlock } from "./Copy";

export function terminalScript(cat: Catalog): string {
  const lines = [
    `claude plugin marketplace add ${cat.marketplace.repo}`,
    ...cat.plugins.map((p) => `claude plugin install ${p.name}@${cat.marketplace.name}`),
  ];
  return lines.join("\n") + "\n";
}

export function agentPrompt(cat: Catalog): string {
  const names = cat.plugins.map((p) => p.name).join(", ");
  return (
    `Підключи маркетплейс Claude Code плагінів і встанови всі його плагіни:\n` +
    `1. Виконай: claude plugin marketplace add ${cat.marketplace.repo}\n` +
    `2. Встанови всі плагіни (кількість: ${cat.plugins.length}): ${names} — ` +
    `кожен командою claude plugin install <назва>@${cat.marketplace.name}\n` +
    `3. Перевір командою claude plugin list, що зʼявились усі (${cat.plugins.length} шт.) і мають статус enabled.\n` +
    `4. Скіли з різних плагінів посилаються один на одного, тому потрібен повний набір — не пропускай плагіни.\n` +
    `5. Наприкінці нагадай мені вручну увімкнути автооновлення: /plugin → Marketplaces → ` +
    `${cat.marketplace.name} → Enable auto-update (для сторонніх маркетплейсів воно вимкнене за замовчуванням).`
  );
}

export function InstallAll(props: { catalog: Catalog }) {
  const [tab, setTab] = useState<"term" | "prompt">("term");
  return (
    <section id="install-all">
      <h2>Встановити все одразу</h2>
      <p style={{ color: "var(--text2)", fontSize: 14 }}>
        Рекомендований шлях — повний набір: скіли з різних плагінів посилаються один на одного,
        тож повну силу дає лише повний комплект.
      </p>
      <div className="tabs">
        <button className={tab === "term" ? "tab active" : "tab"}
          aria-pressed={tab === "term"} onClick={() => setTab("term")}>
          Термінал
        </button>
        <button className={tab === "prompt" ? "tab active" : "tab"}
          aria-pressed={tab === "prompt"} onClick={() => setTab("prompt")}>
          Промпт для Claude Code / Codex
        </button>
      </div>
      {tab === "term" ? (
        <CopyBlock text={terminalScript(props.catalog)} kind="all-terminal" item="all" />
      ) : (
        <CopyBlock text={agentPrompt(props.catalog)} kind="all-prompt" item="all" />
      )}
    </section>
  );
}
