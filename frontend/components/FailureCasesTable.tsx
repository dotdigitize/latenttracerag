export default function FailureCasesTable({ failures }: { failures: any[] }) {
  return (
    <section className="rounded border border-stone-300 bg-white p-4">
      <h2 className="text-lg font-semibold">Failure Cases</h2>
      <table className="mt-3 w-full text-sm">
        <thead><tr className="text-left text-stone-500"><th className="py-2">Type</th><th className="py-2">Details</th></tr></thead>
        <tbody>{failures.map((item) => <tr key={item.id} className="border-t border-stone-100"><td className="py-2">{item.failure_type}</td><td className="py-2">{item.details}</td></tr>)}</tbody>
      </table>
    </section>
  );
}
