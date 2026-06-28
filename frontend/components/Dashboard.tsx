export default function Dashboard({ state }: { state: any }) {
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Dashboard Overview</h2>
      <div className="mt-4 grid grid-cols-3 gap-3">
        <Metric label="Documents" value={state.documents.length} />
        <Metric label="Backend" value={state.health?.status || 'offline'} />
        <Metric label="External APIs" value={String(state.health?.external_apis_allowed ?? false)} />
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return <div className="rounded border border-stone-200 p-3"><div className="text-xs text-stone-500">{label}</div><div className="mt-1 text-xl font-semibold">{value}</div></div>;
}
