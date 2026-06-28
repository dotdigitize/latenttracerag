export default function CorpusPanel({ documents }: { documents: any[] }) {
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Corpus Browser</h2>
      <div className="mt-3 max-h-80 overflow-auto">
        {documents.map((doc) => (
          <div key={doc.id} className="border-b border-stone-200 py-2">
            <div className="font-medium">{doc.title}</div>
            <div className="text-xs text-stone-500">{doc.path} · {doc.content_length} chars</div>
          </div>
        ))}
      </div>
    </section>
  );
}
