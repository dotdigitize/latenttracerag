const rows = [
  ['Naive', 'One retrieval pass', 'Lowest overhead'],
  ['Agentic', 'Verbose iterative retrieval', 'Highest audit detail'],
  ['Latent Trace', 'Compact structured actions', 'Reduced reasoning-token overhead']
];

export default function ModelComparisonPanel() {
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Model Comparison</h2>
      <div className="mt-3 space-y-2">
        {rows.map(([name, behavior, tradeoff]) => <div key={name} className="grid grid-cols-3 gap-2 rounded border border-stone-200 p-2 text-sm"><span className="font-medium">{name}</span><span>{behavior}</span><span className="text-stone-600">{tradeoff}</span></div>)}
      </div>
    </section>
  );
}
