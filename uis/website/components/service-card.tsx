type ServiceCardProps = {
  number: string;
  title: string;
  description: string;
  detail: string;
};

export function ServiceCard({ number, title, description, detail }: ServiceCardProps) {
  return (
    <article className="flex min-h-72 flex-col bg-white p-6 sm:p-8">
      <p className="font-display text-3xl text-coral">{number}</p>
      <h3 className="mt-8 font-display text-2xl text-ink">{title}</h3>
      <p className="mt-3 flex-1 text-sm leading-6 text-ink/70">{description}</p>
      <p className="mt-6 border-t border-line pt-4 text-xs font-semibold text-pine">{detail}</p>
    </article>
  );
}