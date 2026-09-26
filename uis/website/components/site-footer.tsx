export function SiteFooter() {
  return (
    <footer className="bg-ink px-5 py-7 text-white sm:px-8 lg:px-12">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 text-xs text-white/70 sm:flex-row sm:items-center sm:justify-between">
        <p>© 2025 Nexova. Todos los derechos reservados.</p>
        <nav aria-label="Redes sociales" className="flex gap-5">
          <a className="hover:text-leaf focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-leaf" href="https://linkedin.com/company/nexova" rel="noreferrer" target="_blank">LinkedIn</a>
          <a className="hover:text-leaf focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-leaf" href="https://instagram.com/nexova" rel="noreferrer" target="_blank">Instagram</a>
        </nav>
      </div>
    </footer>
  );
}