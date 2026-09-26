const navigation = [
  { label: "Servicios", href: "#servicios" },
  { label: "Talento", href: "#talento" },
  { label: "Contacto", href: "#contacto" },
];

export function SiteHeader() {
  return (
    <header className="relative z-10 border-b border-white/20">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8 lg:px-12">
        <a
          href="#inicio"
          aria-label="Nexova Solutions, inicio"
          className="font-display text-2xl text-white focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-leaf"
        >
          Nexova<span className="text-leaf">.</span>
        </a>
        <nav aria-label="Navegación principal">
          <ul className="flex items-center gap-3 text-xs font-medium sm:gap-7 sm:text-sm">
            {navigation.map((item) => (
              <li key={item.href}>
                <a className="text-white/90 transition-colors hover:text-leaf focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-leaf" href={item.href}>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}