import { TalentoRegistro } from "../types/models";

export function countByCategory<T, TKey extends PropertyKey>(
  items: ReadonlyArray<T>,
  keySelector: (item: T) => TKey
): Record<TKey, number> {
  return items.reduce((acc, item) => {
    const key = keySelector(item);
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {} as Record<TKey, number>);
}

export function sumBy<T>(
  items: ReadonlyArray<T>,
  valueSelector: (item: T) => number
): number {
  return items.reduce((acc, item) => acc + valueSelector(item), 0);
}

export function averageBy<T>(
  items: ReadonlyArray<T>,
  valueSelector: (item: T) => number
): number {
  if (items.length === 0) {
    return 0;
  }
  return sumBy(items, valueSelector) / items.length;
}

export function maxBy<T>(
  items: ReadonlyArray<T>,
  valueSelector: (item: T) => number
): T | null {
  if (items.length === 0) {
    return null;
  }

  return items.reduce((maxItem, currentItem) =>
    valueSelector(currentItem) > valueSelector(maxItem) ? currentItem : maxItem
  );
}

export function minBy<T>(
  items: ReadonlyArray<T>,
  valueSelector: (item: T) => number
): T | null {
  if (items.length === 0) {
    return null;
  }

  return items.reduce((minItem, currentItem) =>
    valueSelector(currentItem) < valueSelector(minItem) ? currentItem : minItem
  );
}

export interface ReporteTalento {
  totalRegistros: number;
  porSector: Record<TalentoRegistro["sectorInteres"], number>;
  porPais: Record<TalentoRegistro["paisResidencia"], number>;
  promedioAniosExperiencia: number;
  experienciaMaxima: TalentoRegistro | null;
  experienciaMinima: TalentoRegistro | null;
}

export function generarReporteTalento(
  registros: ReadonlyArray<TalentoRegistro>
): ReporteTalento {
  const porSector = countByCategory(registros, (item) => item.sectorInteres);
  const porPais = countByCategory(registros, (item) => item.paisResidencia);

  return {
    totalRegistros: registros.length,
    porSector,
    porPais,
    promedioAniosExperiencia: averageBy(registros, (item) => item.aniosExperiencia),
    experienciaMaxima: maxBy(registros, (item) => item.aniosExperiencia),
    experienciaMinima: minBy(registros, (item) => item.aniosExperiencia)
  };
}
