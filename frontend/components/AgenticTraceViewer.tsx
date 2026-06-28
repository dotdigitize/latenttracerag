export default function AgenticTraceViewer({ result }: { result: any }) {
  const steps = result?.trace?.steps || [];
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Agentic Trace Viewer</h2>
      <div className="mt-3 space-y-2">
        {steps.map((step: any) => (
          <div key={step.step_index} className="rounded border border-stone-200 p-3 text-sm">
            <div className="text-stone-700">{step.thought || step.decoded_trace || 'Compact retrieval action'}</div>
            {step.action && <pre className="mt-2 overflow-auto rounded bg-stone-100 p-2 text-xs">{JSON.stringify(step.action, null, 2)}</pre>}
          </div>
        ))}
      </div>
    </section>
  );
}
