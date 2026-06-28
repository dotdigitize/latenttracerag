import type { QueryMode } from '../hooks/useLatentTraceRag';

export default function EvaluationRunner({ runEvaluation, loading, report }: { runEvaluation: (mode: QueryMode) => Promise<any>; loading: boolean; report: any }) {
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Evaluation Runner</h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {(['naive', 'agentic', 'latent_trace'] as QueryMode[]).map((mode) => (
          <button key={mode} className="rounded border border-stone-400 px-3 py-2 text-sm hover:bg-stone-100" disabled={loading} onClick={() => runEvaluation(mode)}>{mode}</button>
        ))}
      </div>
      <pre className="mt-3 max-h-56 overflow-auto rounded bg-stone-100 p-3 text-xs">{JSON.stringify(report?.summary || {}, null, 2)}</pre>
    </section>
  );
}
