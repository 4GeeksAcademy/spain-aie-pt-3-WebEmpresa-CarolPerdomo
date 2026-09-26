type MetricCardProps = {
  label: string;
  value: string;
  detail: string;
};

export function MetricCard({ label, value, detail }: MetricCardProps) {
  return (
    <article className="border border-line bg-white p-5 sm:p-6">
      <h2 className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">{label}</h2>
      <p className="mt-4 font-display text-4xl leading-none text-pine sm:text-5xl">{value}</p>
      <p className="mt-3 text-xs leading-5 text-muted">{detail}</p>
    </article>
  );
}