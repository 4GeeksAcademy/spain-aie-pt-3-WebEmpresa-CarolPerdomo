type SectionHeadingProps = {
  eyebrow: string;
  title: string;
  description: string;
};

export function SectionHeading({ eyebrow, title, description }: SectionHeadingProps) {
  return (
    <header>
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-coral">{eyebrow}</p>
      <h2 className="mt-4 max-w-2xl font-display text-4xl leading-tight text-ink sm:text-5xl">
        {title}
      </h2>
      <p className="mt-4 max-w-2xl text-base leading-7 text-ink/70">{description}</p>
    </header>
  );
}