import { Component, type ReactNode } from 'react';

/**
 * Портований компонент (react-ux-mechanics). Залежності: лише react.
 * Токени теми: border-line, bg-card, text-ink-soft, text-ink-faint, azure,
 * .num — перейменувати під свою Tailwind-тему.
 */

/**
 * Огорожа від помилок рендеру: блок, що спіткнувся об несподівані дані,
 * падає сам із чесним поясненням — а не тягне за собою всю сторінку білим
 * екраном. Клас — бо getDerivedStateFromError досі існує лише для класових
 * компонентів.
 *
 * Два місця застосування:
 * 1) навколо <Outlet/> маршрутів — з key={location.pathname}, щоб перехід
 *    на іншу сторінку скидав помилку;
 * 2) навколо кожного обчислювального блока дешборда — падає блок, не сторінка.
 */
export class ErrorBoundary extends Component<
  {
    children: ReactNode;
    /** що саме не побудувалось — підставляється в текст фолбека */
    label?: string;
    /** компактний фолбек без рамки — для огорож усередині наявної картки */
    bare?: boolean;
  },
  { error: Error | null }
> {
  state: { error: Error | null } = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // стек компонента — в консоль: користувачу він ні до чого, а для
    // діагностики живого застосунку це єдиний слід
    console.error(`ErrorBoundary${this.props.label ? ` [${this.props.label}]` : ''}`, error, info);
  }

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;

    const message = (
      <>
        <p className="text-[13.5px] text-ink-soft">
          Не вдалося побудувати {this.props.label ?? 'цей блок'} — сталася помилка обробки даних.
          Решта сторінки працює.
        </p>
        <p className="num mt-1 break-all text-[12px] text-ink-faint">{error.message}</p>
        <button
          type="button"
          onClick={() => this.setState({ error: null })}
          className="mt-2 rounded-md border border-line px-2.5 py-1 text-[12.5px] text-ink-soft transition-colors hover:border-azure hover:text-azure"
        >
          Спробувати ще раз
        </button>
      </>
    );

    if (this.props.bare) return <div className="py-2">{message}</div>;
    return <section className="rounded-xl border border-line bg-card p-5">{message}</section>;
  }
}
