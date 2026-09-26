import Image from "next/image";
import { SectionHeading } from "@/components/section-heading";
import { ServiceCard } from "@/components/service-card";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

const services = [
  {
    number: "01",
    title: "Headhunting ejecutivo",
    description:
      "Encontramos perfiles de mandos medios y directivos con experiencia, criterio y afinidad con la cultura de tu empresa.",
    detail: "Búsqueda personalizada · Garantía de reemplazo",
  },
  {
    number: "02",
    title: "Equipos de soporte",
    description:
      "Equipos de atención especializados que representan tu marca, con formación continua y supervisión dedicada.",
    detail: "Tecnología, retail y servicios financieros",
  },
  {
    number: "03",
    title: "Formación corporativa",
    description:
      "Programas de liderazgo, comunicación y gestión de equipos diseñados alrededor de los retos reales de tu organización.",
    detail: "Modalidad presencial y online",
  },
];

const proofPoints = [
  { value: "12", label: "Años de experiencia en el mercado latinoamericano" },
  { value: "+500", label: "Procesos de selección" },
  { value: "2", label: "Sedes: Valencia y Miami" },
  { value: "120", label: "Personas en el equipo" },
];

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "Nexova",
  description: "Consultora de recursos humanos y adquisición de talento",
  url: "https://nexova.com",
  foundingDate: "2011",
  address: [
    {
      "@type": "PostalAddress",
      addressCountry: "ES",
      addressLocality: "Valencia",
      addressRegion: "Comunidad Valenciana",
    },
    {
      "@type": "PostalAddress",
      addressCountry: "US",
      addressLocality: "Miami",
      addressRegion: "Florida",
    },
  ],
  contactPoint: {
    "@type": "ContactPoint",
    telephone: "+34-960-123-456",
    contactType: "customer service",
    availableLanguage: ["Spanish", "English"],
  },
  sameAs: [
    "https://linkedin.com/company/nexova",
    "https://instagram.com/nexova",
  ],
};

export default function Home() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }}
      />

      <main>
        <section
          id="inicio"
          aria-labelledby="hero-title"
          className="relative isolate flex min-h-[82svh] flex-col overflow-hidden bg-pine text-white"
        >
          <Image
            src="https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=2200&q=85"
            alt="Profesionales colaboran alrededor de una mesa en una sesión de trabajo"
            fill
            priority
            sizes="100vw"
            className="-z-20 object-cover"
          />
          <div aria-hidden="true" className="absolute inset-0 -z-10 bg-ink/65" />
          <SiteHeader />

          <div className="mx-auto flex w-full max-w-7xl flex-1 items-center px-5 pb-20 pt-20 sm:px-8 lg:px-12">
            <div className="max-w-4xl">
              <p className="mb-6 text-xs font-semibold uppercase tracking-[0.18em] text-leaf sm:text-sm">
                Nexova Solutions · Valencia + Miami
              </p>
              <h1
                id="hero-title"
                className="max-w-4xl font-display text-5xl leading-[1.04] sm:text-6xl lg:text-7xl"
              >
                Construimos equipos excepcionales para empresas en crecimiento.
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-7 text-white/85 sm:text-lg sm:leading-8">
                Consultora de recursos humanos y adquisición de talento con más
                de 10 años ayudando a empresas de tecnología, retail y servicios
                financieros a encontrar y desarrollar el mejor talento.
              </p>
              <div className="mt-9 flex flex-wrap items-center gap-4">
                <a
                  href="#talento"
                  className="inline-flex min-h-12 items-center justify-center bg-leaf px-6 py-3 text-sm font-semibold text-ink transition-colors hover:bg-white focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-leaf"
                >
                  Únete a nuestro banco de talento
                </a>
                <a
                  href="#servicios"
                  className="inline-flex min-h-12 items-center justify-center border border-white/60 px-6 py-3 text-sm font-semibold text-white transition-colors hover:border-white hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-white"
                >
                  Explorar servicios
                </a>
              </div>
              <p className="mt-8 text-sm text-white/75">
                Headhunting · Soporte externalizado · Formación corporativa
              </p>
            </div>
          </div>
        </section>

        <section id="servicios" className="bg-paper px-5 py-20 sm:px-8 lg:px-12 lg:py-28">
          <div className="mx-auto max-w-7xl">
            <SectionHeading
              eyebrow="Lo que hacemos"
              title="Talento preparado para mover tu negocio."
              description="Acompañamos a empresas medianas a contratar mejor, cuidar cada experiencia de cliente y desarrollar equipos capaces de crecer."
            />
            <div className="mt-12 grid gap-px border border-line bg-line md:grid-cols-3">
              {services.map((service) => (
                <ServiceCard key={service.number} {...service} />
              ))}
            </div>
          </div>
        </section>

        <section className="bg-pine px-5 py-20 text-white sm:px-8 lg:px-12 lg:py-24">
          <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.8fr_1.2fr] lg:items-end">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-leaf">
                Por qué Nexova
              </p>
              <h2 className="mt-5 max-w-xl font-display text-4xl leading-tight sm:text-5xl">
                Experiencia humana. Operación que responde.
              </h2>
              <p className="mt-5 max-w-lg text-base leading-7 text-white/75">
                Somos una empresa establecida que se digitaliza: conocemos el
                trabajo de talento desde dentro. Desde hace doce años construimos
                experiencia en el mercado latinoamericano y la convertimos en
                equipos y procesos más sólidos.
              </p>
            </div>
            <dl className="grid grid-cols-2 border-l border-white/20">
              {proofPoints.map((point) => (
                <div key={point.label} className="border-b border-white/20 px-5 py-6 sm:px-8">
                  <dt className="font-display text-4xl text-leaf sm:text-5xl">{point.value}</dt>
                  <dd className="mt-2 max-w-40 text-sm leading-5 text-white/75">{point.label}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        <section id="talento" className="bg-[#e8e5db] px-5 py-20 sm:px-8 lg:px-12 lg:py-24">
          <div className="mx-auto grid max-w-7xl gap-8 md:grid-cols-[1fr_auto] md:items-center">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-pine">
                Tu siguiente oportunidad
              </p>
              <h2 className="mt-4 max-w-2xl font-display text-4xl leading-tight sm:text-5xl">
                El talento también elige dónde crecer.
              </h2>
              <p className="mt-4 max-w-2xl leading-7 text-ink/75">
                ¿Te interesa explorar oportunidades profesionales con Nexova?
                Nuestro equipo de selección puede orientarte.
              </p>
            </div>
            <a
              href="mailto:contacto@nexova.com?subject=Oportunidades%20profesionales"
              className="inline-flex min-h-12 items-center justify-center bg-coral px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-pine focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-pine"
            >
              Contactar selección
            </a>
          </div>
        </section>

        <section id="contacto" className="bg-white px-5 py-20 sm:px-8 lg:px-12 lg:py-24">
          <div className="mx-auto grid max-w-7xl gap-10 md:grid-cols-[0.8fr_1.2fr]">
            <SectionHeading
              eyebrow="Hablemos"
              title="El equipo adecuado cambia lo que es posible."
              description="Cuéntanos qué necesita tu organización. Diseñaremos contigo el siguiente paso."
            />
            <div className="grid gap-8 border-t border-line pt-6 sm:grid-cols-2 md:border-t-0 md:pt-0">
              <address className="not-italic">
                <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-pine">
                  Valencia
                </h3>
                <p className="mt-3 text-sm text-ink/70">Comunidad Valenciana, España</p>
                <a className="mt-2 inline-block font-medium hover:text-coral" href="tel:+34960123456">
                  +34 960 123 456
                </a>
              </address>
              <address className="not-italic">
                <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-pine">
                  Miami
                </h3>
                <p className="mt-3 text-sm text-ink/70">Florida, Estados Unidos</p>
                <a className="mt-2 inline-block font-medium hover:text-coral" href="tel:+13055550191">
                  +1 305 555 0191
                </a>
              </address>
              <a className="text-sm font-medium underline decoration-line underline-offset-4 hover:text-coral sm:col-span-2" href="mailto:contacto@nexova.com">
                contacto@nexova.com
              </a>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
