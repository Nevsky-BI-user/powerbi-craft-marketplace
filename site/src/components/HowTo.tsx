import type { Catalog } from "../types";
import { CopyRow } from "./Copy";

export function HowTo(props: { catalog: Catalog }) {
  const mp = props.catalog.marketplace;
  return (
    <section id="how-to">
      <h2>Як почати</h2>
      <ol className="steps">
        <li>
          Потрібен <a href="https://claude.com/claude-code" target="_blank" rel="noreferrer">Claude
          Code</a> (термінал, десктоп-застосунок або IDE-розширення). Команди встановлення
          працюють у будь-якому терміналі.
        </li>
        <li>
          Підключіть маркетплейс — одна команда в терміналі:
          <CopyRow text={`claude plugin marketplace add ${mp.repo}`} kind="marketplace" item="add" />
        </li>
        <li>
          Встановіть плагіни: <a href="#install-all">всі одразу</a> або вибірково — команда
          встановлення є на картці кожного плагіна і скіла вище.
        </li>
        <li>
          Перевірте результат:
          <CopyRow text="claude plugin list" kind="marketplace" item="verify" />
        </li>
        <li>
          Увімкніть автооновлення (раз, ~30 секунд): в інтерактивному Claude Code наберіть{" "}
          <code>/plugin</code> → вкладка Marketplaces → <b>{mp.name}</b> → Enable auto-update.
          Для сторонніх маркетплейсів воно вимкнене за замовчуванням, тому без цього кроку
          оновлення доведеться тягнути вручну:
          <CopyRow text={`claude plugin marketplace update ${mp.name}`} kind="marketplace" item="update" />
        </li>
      </ol>
      <div className="note">
        Що ставиться разом зі скілами: плагін pbi-report-ux містить хук, який після кожної правки
        файлів звіту автоматично перевіряє report.json. Хуку потрібні bash (на Windows — Git Bash,
        який Claude Code і так використовує) та python 3; без python хук тихо пропускається,
        а вимкнути його можна змінною POWERBI_CRAFT_HOOKS=0. Плагіни pbi-quality і
        report-storytelling містять read-only субагентів-ревʼюерів — вони не можуть редагувати
        ваші файли.
      </div>
    </section>
  );
}
