import Dashboard from './components/Dashboard';
import CorpusPanel from './components/CorpusPanel';
import QueryConsole from './components/QueryConsole';
import RetrievalTrace from './components/RetrievalTrace';
import AgenticTraceViewer from './components/AgenticTraceViewer';
import LatencyBreakdown from './components/LatencyBreakdown';
import EvaluationRunner from './components/EvaluationRunner';
import FailureCasesTable from './components/FailureCasesTable';
import EmbeddingDiagnosticsPanel from './components/EmbeddingDiagnosticsPanel';
import ModelComparisonPanel from './components/ModelComparisonPanel';
import { useLatentTraceRag } from './hooks/useLatentTraceRag';

export default function App() {
  const api = useLatentTraceRag();
  const { state } = api;

  return (
    <main className="min-h-screen">
      <header className="border-b border-stone-300 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal">LatentTraceRAG</h1>
            <p className="text-sm text-stone-600">Local retrieval evaluation, tracing, and diagnostics</p>
          </div>
          <button className="rounded border border-stone-400 px-3 py-2 text-sm hover:bg-stone-100" onClick={api.refresh}>Refresh</button>
        </div>
      </header>
      <div className="mx-auto grid max-w-7xl gap-4 px-6 py-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Dashboard state={state} />
        <ModelComparisonPanel />
        <QueryConsole runQuery={api.runQuery} loading={state.loading} />
        <RetrievalTrace result={state.queryResult} />
        <AgenticTraceViewer result={state.queryResult} />
        <LatencyBreakdown latency={state.latestLatency || state.queryResult?.trace?.latency_by_stage} />
        <EvaluationRunner runEvaluation={api.runEvaluation} loading={state.loading} report={state.latestReport} />
        <EmbeddingDiagnosticsPanel diagnostics={state.diagnostics} />
        <CorpusPanel documents={state.documents} />
        <FailureCasesTable failures={state.failures} />
      </div>
      {state.error && <div className="fixed bottom-4 right-4 rounded border border-red-300 bg-white px-4 py-3 text-sm text-red-700 shadow">{state.error}</div>}
    </main>
  );
}
