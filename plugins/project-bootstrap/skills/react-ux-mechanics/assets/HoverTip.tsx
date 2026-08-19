import { useState, type CSSProperties, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

/**
 * Портований компонент (react-ux-mechanics). Залежності: лише react/react-dom.
 * Класи-токени теми (border-line, bg-card, text-navy, text-ink-soft, text-ok,
 * text-crit, text-warn-ink, .num) — з Tailwind-теми проєкту; в іншому проєкті
 * перейменувати під свою тему.
 *
 * ПРАВИЛО ДОДАНОЇ ЦІННОСТІ: підказка існує лише тоді, коли додає щось, чого
 * на екрані немає (порівняння, повну назву обрізаного підпису, пояснення).
 * Підказка, що повторює видимий підпис чи число, — шум: не вішати взагалі.
 */

const TIP_W = 300; // max-width картки підказки — для клампу біля правого краю

/** тон відхилення — та сама семантика, що в плашках: зелене на краще, червоне на гірше */
export type TipTone = 'none' | 'neutral' | 'ok' | 'okStrong' | 'warn' | 'crit' | 'critStrong';

/**
 * Рядок структурованої підказки: підпис → нейтральна пара значень → кольорове
 * відхилення ОКРЕМОЮ коміркою. Складені значення («−14,48 тис. т · −5,06%»
 * одним рядком) ламали стовпчик чисел — тому значення і дельта нарізно.
 */
export interface TipRow {
  label: string;
  /** нейтральна пара («271,9 проти 286,4») — колір несе лише delta */
  value: string;
  delta?: { text: string; tone: TipTone };
}

/** Заголовок + рядки «підпис → значення → відхилення». */
export interface RichTip {
  title: string;
  /** одиниця виміру — ОДИН раз біля заголовка, а не в кожному рядку */
  unit?: string | null;
  rows: TipRow[];
  /** пояснення під рядками («чому це добре/погано») — замість вкладеної другої підказки */
  note?: string;
}

const TONE_TEXT_CLS: Record<TipTone, string> = {
  none: 'text-ink-soft',
  neutral: 'text-ink-soft',
  ok: 'text-ok',
  okStrong: 'text-ok font-semibold',
  warn: 'text-warn-ink',
  crit: 'text-crit',
  critStrong: 'text-crit font-semibold',
};

/**
 * Жива підказка замість браузерного title: зʼявляється одразу, у стилі бренду,
 * йде за курсором. Портал у body — інакше overflow-обгортки її обрізали б.
 *
 * rich — компактна підказка чисел: «До плану: 271,9 проти 286,4 · −5,1%»,
 * «До травня: …» — пари абсолютів і тонована дельта, місяць після «до» в
 * родовому відмінку. text — простий багаторядковий рядок (перший — заголовок)
 * для підказок без порівнянь: пояснення, повна назва обрізаного підпису.
 * На сенсорних екранах підказки немає — критичні дані мають жити в розмітці.
 */
export function HoverTip({
  text,
  rich,
  children,
  className,
  style,
  as = 'div',
}: {
  text?: string | null;
  rich?: RichTip | null;
  children?: ReactNode;
  className?: string;
  style?: CSSProperties;
  /** span — для інлайн-елементів (бейджі); g — для груп усередині SVG */
  as?: 'div' | 'span' | 'g';
}) {
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
  const Tag = as;

  if (!rich && !text) {
    return (
      <Tag className={className} style={style}>
        {children}
      </Tag>
    );
  }

  const lines = text ? text.split('\n') : [];
  const track = (e: React.MouseEvent) => setPos({ x: e.clientX, y: e.clientY });
  // біля нижнього краю екрана підказка стає НАД курсором, щоб не обрізатись
  const below = pos !== null && pos.y < window.innerHeight - 180;

  return (
    <Tag
      className={className}
      style={style}
      onMouseEnter={track}
      onMouseMove={track}
      onMouseLeave={() => setPos(null)}
    >
      {children}
      {pos &&
        createPortal(
          <div
            role="tooltip"
            className="pointer-events-none fixed z-[80] rounded-lg border border-line bg-card px-3 py-2 shadow-[0_6px_20px_rgba(12,55,94,0.16)]"
            style={{
              left: Math.min(Math.max(pos.x + 14, 8), window.innerWidth - TIP_W - 8),
              top: below ? pos.y + 16 : undefined,
              bottom: below ? undefined : window.innerHeight - pos.y + 12,
              maxWidth: TIP_W,
            }}
          >
            {rich ? (
              <>
                <div className="text-[12.5px] font-medium leading-snug text-navy">
                  {rich.title}
                  {rich.unit && (
                    <span className="font-normal text-ink-faint"> · {rich.unit}</span>
                  )}
                </div>
                {rich.rows.length > 0 && (
                  <div className="mt-1 flex flex-col gap-0.5">
                    {rich.rows.map((r, i) => (
                      <div
                        key={i}
                        className="flex items-baseline justify-between gap-3 text-[12px] leading-snug"
                      >
                        <span className="text-ink-soft">{r.label}</span>
                        <span className="num whitespace-nowrap text-right text-ink">
                          {r.value}
                          {r.delta && (
                            <span className={`ml-2 ${TONE_TEXT_CLS[r.delta.tone]}`}>
                              {r.delta.text}
                            </span>
                          )}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
                {rich.note && (
                  <div className="mt-1.5 border-t border-line pt-1.5 text-[11.5px] leading-snug text-ink-soft">
                    {rich.note}
                  </div>
                )}
              </>
            ) : (
              <>
                <div className="text-[12.5px] font-medium leading-snug text-navy">{lines[0]}</div>
                {lines.length > 1 && (
                  <div className="num mt-0.5 whitespace-pre-line text-[12px] leading-relaxed text-ink-soft">
                    {lines.slice(1).join('\n')}
                  </div>
                )}
              </>
            )}
          </div>,
          document.body,
        )}
    </Tag>
  );
}
