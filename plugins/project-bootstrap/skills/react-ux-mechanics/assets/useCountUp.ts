import { useEffect, useRef, useState } from 'react';

/**
 * Портований хук (react-ux-mechanics). Залежності: лише react.
 */

/**
 * «Докрут» великої цифри до значення — ЛИШЕ при першій появі компонента.
 * Подальші зміни (перемикання місяця/фільтра) застосовуються миттєво: якби
 * цифри докручувались на кожен клік, вони б «танцювали» без упину.
 * Поважає prefers-reduced-motion: там значення ставиться одразу.
 *
 * ВАЖЛИВО: єдиний запуск списується і при target === null — тому KPI-плитку
 * монтувати лише з готовими даними (до того тримати скелетон), інакше
 * анімація «згорить» до приходу значення і цифра просто зʼявиться.
 */
export function useCountUp(target: number | null, ms = 750): number | null {
  const [display, setDisplay] = useState<number | null>(target === null ? null : 0);
  const played = useRef(false);

  useEffect(() => {
    if (played.current || target === null || Math.abs(target) < 1e-9) {
      played.current = true;
      setDisplay(target);
      return;
    }
    played.current = true;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setDisplay(target);
      return;
    }
    let raf = 0;
    const t0 = performance.now();
    const step = (t: number) => {
      const p = Math.min(1, (t - t0) / ms);
      // easeOutCubic: швидкий старт і мʼяке «сідання» на точне значення
      setDisplay(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf = requestAnimationFrame(step);
      else setDisplay(target);
    };
    raf = requestAnimationFrame(step);
    // страхувальний таймер: у фоновій вкладці requestAnimationFrame не тікає,
    // і без нього цифра застигала б на нулі до наступного рендера
    const settle = setTimeout(() => setDisplay(target), ms + 150);
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(settle);
    };
  }, [target, ms]);

  return display;
}
