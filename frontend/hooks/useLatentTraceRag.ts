import { useCallback, useEffect, useState } from 'react';

export type QueryMode = 'naive' | 'agentic' | 'latent_trace';

export interface ApiState {
  documents: any[];
  health: any;
  latestLatency: any;
  latestReport: any;
  diagnostics: any;
  failures: any[];
  loading: boolean;
  error: string | null;
  queryResult: any;
}

async function getJson(path: string) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json();
}

export function useLatentTraceRag() {
  const [state, setState] = useState<ApiState>({
    documents: [],
    health: null,
    latestLatency: null,
    latestReport: null,
    diagnostics: null,
    failures: [],
    loading: false,
    error: null,
    queryResult: null
  });

  const refresh = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const [health, documents, latestLatency, latestReport, diagnostics, failures] = await Promise.all([
        getJson('/health'),
        getJson('/api/documents'),
        getJson('/api/latency/latest'),
        getJson('/api/reports/latest'),
        getJson('/api/diagnostics/embeddings'),
        getJson('/api/failures')
      ]);
      setState((current) => ({ ...current, health, documents, latestLatency, latestReport, diagnostics, failures, loading: false }));
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error instanceof Error ? error.message : 'Request failed' }));
    }
  }, []);

  const runQuery = useCallback(async (queryText: string, mode: QueryMode, topK: number, maxRetrievalSteps: number) => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query_text: queryText, mode, top_k: topK, max_retrieval_steps: maxRetrievalSteps })
      });
      if (!response.ok) throw new Error(`Query returned ${response.status}`);
      const queryResult = await response.json();
      setState((current) => ({ ...current, queryResult, latestLatency: queryResult.trace.latency_by_stage, loading: false }));
      return queryResult;
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error instanceof Error ? error.message : 'Query failed' }));
      return null;
    }
  }, []);

  const runEvaluation = useCallback(async (mode: QueryMode) => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await fetch(`/api/evals/run?mode=${mode}`, { method: 'POST' });
      if (!response.ok) throw new Error(`Evaluation returned ${response.status}`);
      const latestReport = { summary: await response.json() };
      setState((current) => ({ ...current, latestReport, loading: false }));
      return latestReport;
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error instanceof Error ? error.message : 'Evaluation failed' }));
      return null;
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { state, refresh, runQuery, runEvaluation };
}
