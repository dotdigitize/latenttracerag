export default function LatencyBreakdown({ latency }: { latency: any }) {
  const rows = latency ? Object.entries(latency) : [];
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Stage Wise Latency</h2>
      <table className="mt-3 w-full text-sm">
        <tbody>
          {rows.map(([key, value]) => <tr key={key} className="border-b border-stone-100"><td className="py-2">{key}</td><td className="py-2 text-right">{String(value)}</td></tr>)}
        </tbody>
      </table>
    </section>
  );
}
