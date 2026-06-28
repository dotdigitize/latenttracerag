export default function RetrievalTrace({ result }: { result: any }) {
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Retrieval Trace</h2>
      {result ? (
        <div className="mt-3 space-y-3">
          <p className="text-sm">{result.answer}</p>
          {result.trace.steps.map((step: any) => (
            <div key={step.step_index} className="rounded border border-stone-200 p-3 text-sm">
              <div className="font-medium">Step {step.step_index}</div>
              <div className="text-stone-600">{step.subquery}</div>
              <div className="mt-1 text-xs text-stone-500">Chunks: {step.retrieved_chunk_ids.join(', ') || 'none'}</div>
            </div>
          ))}
        </div>
      ) : <p className="mt-3 text-sm text-stone-500">No query has been run yet.</p>}
    </section>
  );
}
