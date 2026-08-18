/**
 * Портований компонент (react-ux-mechanics). Без залежностей.
 * Токени теми: border-line, bg-card, bg-navy, text-ink-soft — перейменувати
 * під свою Tailwind-тему.
 */

/**
 * Сегментований перемикач: одна рамка, всередині — взаємовиключні варіанти,
 * активний виділений плашкою бренду. Для пар/трійок режимів (факт/план,
 * місяць/рік) він компактніший і чесніший за окремі кнопки чи select:
 * усі варіанти видно одразу, стан читається без розкриття списку.
 */
export function Segmented<T extends string>({
  options,
  value,
  onChange,
  ariaLabel,
  className = '',
}: {
  // NoInfer на options І onChange: T виводиться лише з value (тип стану
  // сторінки). Інакше з setState-колбека виводиться SetStateAction<...>,
  // який не проходить constraint `extends string`, і T падає в голий string.
  // NoInfer вимагає TypeScript ≥ 5.4; на старішому — явний generic на виклику:
  // <Segmented<'fact' | 'plan'> …/>

  options: readonly { value: NoInfer<T>; label: string }[];
  value: T;
  onChange: (v: NoInfer<T>) => void;
  ariaLabel?: string;
  className?: string;
}) {
  return (
    <div
      role="group"
      aria-label={ariaLabel}
      className={`inline-flex rounded-lg border border-line bg-card p-0.5 ${className}`}
    >
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          aria-pressed={o.value === value}
          className={`rounded-md px-3 py-1.5 text-[13px] transition-colors ${
            o.value === value ? 'bg-navy text-white' : 'text-ink-soft hover:text-navy'
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
