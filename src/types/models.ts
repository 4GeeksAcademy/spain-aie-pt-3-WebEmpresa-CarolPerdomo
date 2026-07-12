export type PaisResidencia = "Espana" | "Estados Unidos" | "Otro";

export type SectorInteres =
  | "Tecnologia"
  | "Retail"
  | "Servicios Financieros"
  | "Consultoria"
  | "Otro";

export type NivelIngles = "Basico" | "Intermedio" | "Avanzado" | "Nativo";

export type Disponibilidad = "Inmediata" | "1 mes" | "2-3 meses" | "Solo explorando";

export interface TalentoRegistro {
  id: string;
  nombreCompleto: string;
  email: string;
  telefono: string;
  paisResidencia: PaisResidencia;
  aniosExperiencia: number;
  sectorInteres: SectorInteres;
  nivelIngles: NivelIngles;
  disponibilidad: Disponibilidad;
  linkedinUrl?: string;
  comentariosAdicionales?: string;
  aceptaPoliticaDatos: boolean;
  fechaRegistroISO: string;
}

export interface ServicioNexova {
  codigo: "headhunting" | "outsourcing" | "formacion";
  nombre: string;
  descripcion: string;
}

export interface SedeNexova {
  ciudad: "Valencia" | "Miami";
  pais: "ES" | "US";
  telefono: string;
  emailContacto: string;
}

export interface EmpresaNexova {
  nombre: "Nexova";
  fundacion: number;
  empleadosAprox: number;
  facturacionAnualUSD: number;
  sectoresCliente: ReadonlyArray<"Tecnologia" | "Retail" | "Servicios Financieros">;
  servicios: ReadonlyArray<ServicioNexova>;
  sedes: ReadonlyArray<SedeNexova>;
}

export const serviciosNexova: ReadonlyArray<ServicioNexova> = [
  {
    codigo: "headhunting",
    nombre: "Headhunting Ejecutivo",
    descripcion: "Busqueda y seleccion de perfiles ejecutivos y mandos medios."
  },
  {
    codigo: "outsourcing",
    nombre: "Outsourcing de Atencion al Cliente",
    descripcion: "Equipos especializados para empresas tecnologicas."
  },
  {
    codigo: "formacion",
    nombre: "Formacion Corporativa",
    descripcion: "Programas de soft skills y liderazgo para empresas."
  }
] as const;

export const empresaNexova: EmpresaNexova = {
  nombre: "Nexova",
  fundacion: 2011,
  empleadosAprox: 120,
  facturacionAnualUSD: 8_000_000,
  sectoresCliente: ["Tecnologia", "Retail", "Servicios Financieros"],
  servicios: serviciosNexova,
  sedes: [
    {
      ciudad: "Valencia",
      pais: "ES",
      telefono: "+34 960 123 456",
      emailContacto: "contacto@nexova.com"
    },
    {
      ciudad: "Miami",
      pais: "US",
      telefono: "+1 305 555 0191",
      emailContacto: "contacto@nexova.com"
    }
  ]
};

export const registrosEjemplo: ReadonlyArray<TalentoRegistro> = [
  {
    id: "cand-001",
    nombreCompleto: "Ana Martinez Lopez",
    email: "ana.martinez@example.com",
    telefono: "+34 612 345 678",
    paisResidencia: "Espana",
    aniosExperiencia: 6,
    sectorInteres: "Tecnologia",
    nivelIngles: "Avanzado",
    disponibilidad: "1 mes",
    linkedinUrl: "https://www.linkedin.com/in/ana-martinez-lopez",
    comentariosAdicionales: "Experiencia liderando equipos de atencion al cliente.",
    aceptaPoliticaDatos: true,
    fechaRegistroISO: "2026-07-01"
  },
  {
    id: "cand-002",
    nombreCompleto: "Luis Fernandez Gomez",
    email: "luis.fernandez@example.com",
    telefono: "+1 305 444 2233",
    paisResidencia: "Estados Unidos",
    aniosExperiencia: 10,
    sectorInteres: "Servicios Financieros",
    nivelIngles: "Nativo",
    disponibilidad: "Inmediata",
    aceptaPoliticaDatos: true,
    fechaRegistroISO: "2026-07-03"
  }
] as const;

export function getApellidos(nombreCompleto: string): string {
  const partes = nombreCompleto.trim().split(/\s+/);
  if (partes.length < 2) {
    return "";
  }
  return partes.slice(1).join(" ");
}

export function isSectorObjetivo(sector: SectorInteres): boolean {
  return (
    sector === "Tecnologia" ||
    sector === "Retail" ||
    sector === "Servicios Financieros"
  );
}

export function getNombreDisponibilidad(valor: Disponibilidad): string {
  return valor;
}
