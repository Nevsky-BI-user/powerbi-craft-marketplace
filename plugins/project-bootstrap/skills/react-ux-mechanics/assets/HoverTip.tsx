import { useState, type CSSProperties, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

/**
 * Портований компонент (react-ux-mechanics). Залежності: лише react/react-dom.
 * Класи-токени теми (border-line, bg-card, text-navy, text-ink-soft, .num) —
 * з Tailwind-теми Naftogaz; в іншому проєкті перейменувати під свою тему.
 */

const TIP_W = 300; // max-width картки підказки — для клампу біля правого краю

/**
 * Жива підказка замість браузерного title: зʼявляється одразу (без секундної
 * затримки), у стилі застосунку, і йде за курсором. Рендериться порталом у
 * body — інакше overflow-обгортки таблиць і карток її обрізали б.
 *
 * text — багаторядковий рядок як у title: перший рядок — назва, решта —
 * значення; розриви рядків зберігаються. text=null → рендер без підказки.
 * На сенсорних екранах підказки немає (як не було й з title).
 */
export function HoverTip({
  text,
  children,
  className,
  style,
  as = 'div',
}: {
  text: string | null;
  children?: ReactNode;
  className?: string;
  style?: CSSProperties;
  /** span — для підказок на інлайн-елементах (бейджі) */
  as?: 'div' | 'span';
}) {
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
  const Tag = as;

  if (!text) {
    return (
      <Tag className={className} style={style}>
        {children}
      </Tag>
    );
  }

  const lines = text.split('\n');
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
            <div className="text-[12.5px] font-medium leading-snug text-navy">{lines[0]}</div>
            {lines.length > 1 && (
              <div className="num mt-0.5 whitespace-pre-line text-[12px] leading-relaxed text-ink-soft">
                {lines.slice(1).join('\n')}
              </div>
            )}
          </div>,
          document.body,
        )}
    </Tag>
  );
}
