export default function EmbeddingDiagnosticsPanel({ diagnostics }: { diagnostics: any }) {
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Embedding Diagnostics</h2>
      <pre className="mt-3 overflow-auto rounded bg-stone-100 p-3 text-xs">{JSON.stringify(diagnostics || {}, null, 2)}</pre>
    </section>
  );
}
