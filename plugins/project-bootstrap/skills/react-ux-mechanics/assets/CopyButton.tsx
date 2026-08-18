import { useEffect, useRef, useState } from 'react';

/**
 * Портований компонент (react-ux-mechanics). Залежності: лише react.
 * Токени теми: border-line, border-ok, bg-ok-soft, text-ok, text-ink-soft,
 * azure — перейменувати під свою Tailwind-тему.
 */

/**
 * Кнопка «скопіювати в буфер» із видимим підтвердженням: після кліку на
 * півтори секунди стає зеленим «Скопійовано ✓» — без нього копіювання
 * виглядає як клік у порожнечу. `text` — лінивий: рядок збирається лише по
 * кліку, щоб не рахувати зведення на кожен рендер сторінки.
 */
export function CopyButton({
  text,
  label,
  title,
  className = '',
}: {
  text: () => string;
  label: string;
  title?: string;
  className?: string;
}) {
  const [done, setDone] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => {
    if (timer.current) clearTimeout(timer.current);
  }, []);

  const copy = async () => {
    const value = text();
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      // clipboard API недоступний (http-превʼю, старий браузер) — через textarea
      const ta = document.createElement('textarea');
      ta.value = value;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
    }
    setDone(true);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setDone(false), 1600);
  };

  return (
    <button
      type="button"
      onClick={() => void copy()}
      title={title}
      aria-live="polite"
      className={`rounded-md border px-3 py-2 text-[13px] font-medium transition-colors ${
        done
          ? 'border-ok/60 bg-ok-soft text-ok'
          : 'border-line text-ink-soft hover:border-azure hover:text-azure'
      } ${className}`}
    >
      {done ? 'Скопійовано ✓' : label}
    </button>
  );
}
