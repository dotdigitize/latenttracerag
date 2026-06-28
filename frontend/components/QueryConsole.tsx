import { useState } from 'react';
import type { QueryMode } from '../hooks/useLatentTraceRag';

export default function QueryConsole({ runQuery, loading }: { runQuery: (q: string, m: QueryMode, k: number, s: number) => Promise<any>; loading: boolean }) {
  const [query, setQuery] = useState('What limits apply to the CloudForm Analytics provisional approval?');
  const [mode, setMode] = useState<QueryMode>('latent_trace');
  const [topK, setTopK] = useState(3);
  const [steps, setSteps] = useState(4);
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Query Console</h2>
      <textarea className="mt-3 h-24 w-full rounded border border-stone-300 p-3" value={query} onChange={(event) => setQuery(event.target.value)} />
      <div className="mt-3 grid gap-3 sm:grid-cols-4">
        <select className="rounded border border-stone-300 p-2" value={mode} onChange={(event) => setMode(event.target.value as QueryMode)}>
          <option value="naive">Naive</option>
          <option value="agentic">Agentic</option>
          <option value="latent_trace">Latent Trace</option>
        </select>
        <input className="rounded border border-stone-300 p-2" type="number" min={1} max={10} value={topK} onChange={(event) => setTopK(Number(event.target.value))} />
        <input className="rounded border border-stone-300 p-2" type="number" min={1} max={8} value={steps} onChange={(event) => setSteps(Number(event.target.value))} />
        <button className="rounded bg-slate-900 px-3 py-2 text-white hover:bg-slate-700" onClick={() => runQuery(query, mode, topK, steps)} disabled={loading}>Run</button>
      </div>
    </section>
  );
}
