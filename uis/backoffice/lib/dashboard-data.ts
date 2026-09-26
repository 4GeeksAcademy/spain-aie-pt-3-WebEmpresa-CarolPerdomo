export const companyMetrics = [
  { label: "Equipo", value: "120", detail: "personas en Nexova" },
  { label: "Facturación anual", value: "$8M", detail: "aproximadamente" },
  { label: "Líneas de negocio", value: "03", detail: "selección, soporte y formación" },
  { label: "Presencia", value: "02", detail: "Valencia y Miami" },
];

export const supportResolutionHours = 48;
export const supportSlaHours = 24;
export const supportSlaGapHours = Math.max(0, supportResolutionHours - supportSlaHours);

export const operationalAreas = [
  {
    department: "Selección",
    team: "40 consultores",
    issue: "Cribado de CV manual",
    signal: "Entre 30 y 80 CVs revisados por proceso",
    status: "Trabajo manual",
    tone: "neutral",
  },
  {
    department: "Atención al cliente",
    team: "30 agentes",
    issue: "Resolución media por encima del SLA",
    signal: `${supportResolutionHours} h de media · compromiso de ${supportSlaHours} h`,
    status: `+${supportSlaGapHours} h sobre SLA`,
    tone: "critical",
  },
  {
    department: "Ventas",
    team: "18 personas",
    issue: "Actualización irregular del CRM",
    signal: "Solo el 40% del equipo actualiza HubSpot con regularidad",
    status: "Seguimiento débil",
    tone: "attention",
  },
  {
    department: "Formación",
    team: "12 personas",
    issue: "Catálogo e inscripciones manuales",
    signal: "PDF trimestral · inscripciones en Google Forms y hojas de cálculo",
    status: "Sin plataforma",
    tone: "neutral",
  },
  {
    department: "Recursos Humanos",
    team: "4 personas",
    issue: "Gestión interna por correo y hojas de cálculo",
    signal: "Onboarding, ausencias y consultas sin portal centralizado",
    status: "Sin portal",
    tone: "neutral",
  },
  {
    department: "Tecnología",
    team: "6 personas",
    issue: "Herramientas desconectadas",
    signal: "Sin telemetría ni logging centralizado; despliegues manuales",
    status: "Visibilidad limitada",
    tone: "attention",
  },
];

export const departments = ["Todas", ...operationalAreas.map((area) => area.department)];