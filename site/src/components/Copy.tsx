import { useState } from "react";
import { track, type CopyKind } from "../telemetry";

function IconCopy() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="9" y="9" width="12" height="12" rx="2" />
      <path d="M5 15V5a2 2 0 0 1 2-2h10" />
    </svg>
  );
}

function useCopy(text: string, kind: CopyKind, item: string) {
  const [done, setDone] = useState(false);
  return {
    done,
    copy: () => {
      navigator.clipboard.writeText(text).then(() => {
        setDone(true);
        setTimeout(() => setDone(false), 1600);
        track(kind, item);
      });
    },
  };
}

export function CopyButton(props: { text: string; kind: CopyKind; item: string }) {
  const { done, copy } = useCopy(props.text, props.kind, props.item);
  return (
    <button className={done ? "copybtn done" : "copybtn"} onClick={copy} aria-live="polite">
      <IconCopy /> {done ? "скопійовано" : "копіювати"}
    </button>
  );
}

export function CopyRow(props: { text: string; kind: CopyKind; item: string }) {
  return (
    <div className="copyrow">
      <code>{props.text}</code>
      <CopyButton {...props} />
    </div>
  );
}

export function CopyBlock(props: { text: string; kind: CopyKind; item: string }) {
  return (
    <div className="copyrow block">
      <pre>{props.text}</pre>
      <CopyButton {...props} />
    </div>
  );
}
