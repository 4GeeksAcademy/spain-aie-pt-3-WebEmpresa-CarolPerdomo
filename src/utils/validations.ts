import {
  Disponibilidad,
  NivelIngles,
  PaisResidencia,
  SectorInteres,
  TalentoRegistro
} from "../types/models";

export interface ValidationError {
  field: keyof TalentoRegistro | "general";
  message: string;
}

export interface ValidationResult<T> {
  isValid: boolean;
  data: T;
  errors: ValidationError[];
}

const MENSAJES_ERROR = {
  nombreCompleto: "El nombre debe contener al menos nombre y apellido",
  email: "Ingresa un email valido (ejemplo: nombre@empresa.com)",
  telefono: "El telefono debe incluir codigo de pais (ejemplo: +34 612 345 678)",
  paisResidencia: "Selecciona tu pais de residencia",
  aniosExperiencia: "Los anios de experiencia deben estar entre 0 y 50",
  sectorInteres: "Selecciona el sector de tu interes",
  nivelIngles: "Indica tu nivel de ingles",
  disponibilidad: "Selecciona tu disponibilidad",
  linkedinUrl: "Si incluyes LinkedIn, debe ser una URL valida",
  comentariosAdicionales: "Los comentarios no pueden exceder 500 caracteres",
  aceptaPoliticaDatos:
    "Debes aceptar la politica de tratamiento de datos para continuar",
  fechaRegistroISO: "La fecha de registro debe ser una fecha valida en formato ISO",
  formularioEmpresas:
    "Eres una empresa buscando talento? Escribenos a contacto@nexova.com"
} as const;

const PAISES: ReadonlyArray<PaisResidencia> = ["Espana", "Estados Unidos", "Otro"];
const SECTORES: ReadonlyArray<SectorInteres> = [
  "Tecnologia",
  "Retail",
  "Servicios Financieros",
  "Consultoria",
  "Otro"
];
const NIVELES_INGLES: ReadonlyArray<NivelIngles> = [
  "Basico",
  "Intermedio",
  "Avanzado",
  "Nativo"
];
const DISPONIBILIDADES: ReadonlyArray<Disponibilidad> = [
  "Inmediata",
  "1 mes",
  "2-3 meses",
  "Solo explorando"
];

function isEmailValido(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
}

function isTelefonoValido(telefono: string): boolean {
  return /^\+\d{1,3}\s[\d\s-]{6,20}$/.test(telefono.trim());
}

function isHttpUrl(url: string): boolean {
  return /^https?:\/\//i.test(url.trim());
}

function isIsoDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return false;
  }
  const date = new Date(`${value}T00:00:00Z`);
  return Number.isFinite(date.getTime());
}

export function validarFormularioSoloProfesionales(
  esEmpresaSolicitandoServicio: boolean
): ValidationResult<boolean> {
  const errors: ValidationError[] = [];
  if (esEmpresaSolicitandoServicio) {
    errors.push({
      field: "general",
      message: MENSAJES_ERROR.formularioEmpresas
    });
  }

  return {
    isValid: errors.length === 0,
    data: !esEmpresaSolicitandoServicio,
    errors
  };
}

export function validarTalentoRegistro(
  registro: TalentoRegistro
): ValidationResult<TalentoRegistro> {
  const errors: ValidationError[] = [];

  if (registro.nombreCompleto.trim().split(/\s+/).length < 2) {
    errors.push({ field: "nombreCompleto", message: MENSAJES_ERROR.nombreCompleto });
  }

  if (!isEmailValido(registro.email)) {
    errors.push({ field: "email", message: MENSAJES_ERROR.email });
  }

  if (!isTelefonoValido(registro.telefono)) {
    errors.push({ field: "telefono", message: MENSAJES_ERROR.telefono });
  }

  if (!PAISES.includes(registro.paisResidencia)) {
    errors.push({
      field: "paisResidencia",
      message: MENSAJES_ERROR.paisResidencia
    });
  }

  if (registro.aniosExperiencia < 0 || registro.aniosExperiencia > 50) {
    errors.push({
      field: "aniosExperiencia",
      message: MENSAJES_ERROR.aniosExperiencia
    });
  }

  if (!SECTORES.includes(registro.sectorInteres)) {
    errors.push({ field: "sectorInteres", message: MENSAJES_ERROR.sectorInteres });
  }

  if (!NIVELES_INGLES.includes(registro.nivelIngles)) {
    errors.push({ field: "nivelIngles", message: MENSAJES_ERROR.nivelIngles });
  }

  if (!DISPONIBILIDADES.includes(registro.disponibilidad)) {
    errors.push({ field: "disponibilidad", message: MENSAJES_ERROR.disponibilidad });
  }

  if (registro.linkedinUrl && !isHttpUrl(registro.linkedinUrl)) {
    errors.push({ field: "linkedinUrl", message: MENSAJES_ERROR.linkedinUrl });
  }

  if (
    registro.comentariosAdicionales &&
    registro.comentariosAdicionales.length > 500
  ) {
    errors.push({
      field: "comentariosAdicionales",
      message: MENSAJES_ERROR.comentariosAdicionales
    });
  }

  if (!registro.aceptaPoliticaDatos) {
    errors.push({
      field: "aceptaPoliticaDatos",
      message: MENSAJES_ERROR.aceptaPoliticaDatos
    });
  }

  if (!isIsoDate(registro.fechaRegistroISO)) {
    errors.push({ field: "fechaRegistroISO", message: MENSAJES_ERROR.fechaRegistroISO });
  }

  return {
    isValid: errors.length === 0,
    data: registro,
    errors
  };
}

export function validarLoteRegistros(
  registros: ReadonlyArray<TalentoRegistro>
): ValidationResult<ReadonlyArray<TalentoRegistro>> {
  const allErrors: ValidationError[] = [];

  registros.forEach((registro) => {
    const result = validarTalentoRegistro(registro);
    allErrors.push(...result.errors);
  });

  return {
    isValid: allErrors.length === 0,
    data: registros,
    errors: allErrors
  };
}
