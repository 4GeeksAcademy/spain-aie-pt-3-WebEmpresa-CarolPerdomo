const navigation = [
  { label: "Resumen", href: "#resumen" },
  { label: "Operaciones", href: "#operaciones" },
  { label: "Prioridades", href: "#prioridades" },
];

export function Sidebar() {
  return (
    <aside className="border-b border-line bg-pine text-white lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col lg:border-b-0 lg:border-r">
      <div className="flex items-center justify-between px-5 py-5 lg:block lg:px-7 lg:py-8">
        <a href="#resumen" className="font-display text-2xl focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-leaf">
          Nexova<span className="text-leaf">.</span>
        </a>
        <p className="hidden pt-2 text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-white/55 lg:block">
          Espacio interno
        </p>
        <span className="border border-white/25 px-2 py-1 text-[0.6rem] font-semibold uppercase tracking-widest text-leaf lg:hidden">
          Interno
        </span>
      </div>
      <nav aria-label="Navegación interna" className="px-3 pb-3 lg:px-4 lg:py-8">
        <p className="hidden px-3 pb-3 text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-white/45 lg:block">
          Dirección
        </p>
        <ul className="flex gap-1 overflow-x-auto lg:flex-col">
          {navigation.map((item, index) => (
            <li key={item.href} className="shrink-0">
              <a
                href={item.href}
                aria-current={index === 0 ? "page" : undefined}
                className={`block border-l-2 px-3 py-2.5 text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-leaf lg:px-4 ${
                  index === 0
                    ? "border-leaf bg-white/10 font-semibold text-white"
                    : "border-transparent text-white/70 hover:bg-white/5 hover:text-white"
                }`}
              >
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
      <div className="hidden border-t border-white/15 px-7 py-5 text-xs leading-5 text-white/55 lg:mt-auto lg:block">
        <p>Contexto de empresa</p>
        <p>Valencia · Miami</p>
      </div>
    </aside>
  );
}