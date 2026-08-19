import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
  type RefObject,
} from 'react';

/**
 * Портований механізм scroll-reveal (react-ux-mechanics): entrance-анімації
 * стартують при першій появі блока у вʼюпорті, а не невидимо при завантаженні.
 * Працює В ПАРІ з CSS-класом .reveal-wait (див. animations.css) і guard-ом
 * у @media print — без нього нерозкриті блоки їдуть у PDF порожніми плямами.
 * Залежності: лише react.
 */

const THRESHOLD = 0.12;
/** нижню кромку вʼюпорта підіймаємо: блок оживає, впевнено зайшовши в кадр */
const ROOT_MARGIN = '0px 0px -8% 0px';
/** блок, що зʼявився пізніше цього порога, відкрито прокруткою — каскадна затримка йому ні до чого */
const LATE_REVEAL_MS = 600;

/** без IntersectionObserver (jsdom, старі рушії) і в reduced-motion — показ одразу */
function showsImmediately(): boolean {
  if (typeof window === 'undefined' || typeof IntersectionObserver === 'undefined') return true;
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true;
}

/** одноразовий сигнал «блок побачили»: після першого перетину observer відключається */
export function useReveal<T extends HTMLElement>(): { ref: RefObject<T | null>; shown: boolean } {
  const ref = useRef<T>(null);
  const [shown, setShown] = useState(showsImmediately);

  useEffect(() => {
    if (shown) return;
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (!entries.some((e) => e.isIntersecting)) return;
        io.disconnect();
        setShown(true);
      },
      { threshold: THRESHOLD, rootMargin: ROOT_MARGIN },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [shown]);

  return { ref, shown };
}

/**
 * Обгортка «анімувати при появі»: тримає клас reveal-wait (пауза всіх anim-*
 * всередині і на собі) до першої появи в кадрі. Це той самий div — класи
 * сітки/спани передаються через className, розкладка не зсувається.
 */
export function Reveal({
  className = '',
  style,
  delay,
  children,
}: {
  className?: string;
  style?: CSSProperties;
  /** каскадна затримка (мс); при «пізньому» reveal обнуляється — користувач дивиться саме сюди */
  delay?: number;
  children: ReactNode;
}) {
  const { ref, shown } = useReveal<HTMLDivElement>();
  const mountedAt = useRef(Date.now());
  const [delayMs, setDelayMs] = useState(delay ?? 0);

  // useLayoutEffect, не useEffect: зняття паузи й обнулення затримки мають
  // лягти в один кадр, інакше анімація стартує ще зі старою затримкою
  useLayoutEffect(() => {
    if (shown && Date.now() - mountedAt.current > LATE_REVEAL_MS) setDelayMs(0);
  }, [shown]);

  return (
    <div
      ref={ref}
      className={shown ? className : `reveal-wait ${className}`.trim()}
      style={delay === undefined ? style : { ...style, animationDelay: `${delayMs}ms` }}
    >
      {children}
    </div>
  );
}
