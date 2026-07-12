export type SortDirection = "asc" | "desc";

export interface SortCriterion<T> {
  selector: (item: T) => string | number | boolean | Date;
  direction?: SortDirection;
}

export function filterByPredicate<T>(
  items: ReadonlyArray<T>,
  predicate: (item: T) => boolean
): T[] {
  if (items.length === 0) {
    return [];
  }
  return items.filter(predicate);
}

export function filterByCriteria<T extends Record<string, unknown>>(
  items: ReadonlyArray<T>,
  criteria: Partial<T>
): T[] {
  if (items.length === 0) {
    return [];
  }

  const entries = Object.entries(criteria) as Array<[keyof T, T[keyof T]]>;
  if (entries.length === 0) {
    return [...items];
  }

  return items.filter((item) =>
    entries.every(([key, expected]) => item[key] === expected)
  );
}

export function sortByCriterion<T>(
  items: ReadonlyArray<T>,
  criterion: SortCriterion<T>
): T[] {
  return sortByCriteria(items, [criterion]);
}

export function sortByCriteria<T>(
  items: ReadonlyArray<T>,
  criteria: ReadonlyArray<SortCriterion<T>>
): T[] {
  if (items.length <= 1 || criteria.length === 0) {
    return [...items];
  }

  const normalized = criteria.map((criterion) => ({
    ...criterion,
    direction: criterion.direction ?? "asc"
  }));

  return [...items].sort((a, b) => {
    for (const criterion of normalized) {
      const left = criterion.selector(a);
      const right = criterion.selector(b);
      const directionFactor = criterion.direction === "asc" ? 1 : -1;

      if (left < right) {
        return -1 * directionFactor;
      }
      if (left > right) {
        return 1 * directionFactor;
      }
    }
    return 0;
  });
}

export function groupBy<T, TKey extends PropertyKey>(
  items: ReadonlyArray<T>,
  keySelector: (item: T) => TKey
): Record<TKey, T[]> {
  return items.reduce((acc, item) => {
    const key = keySelector(item);
    const group = acc[key] ?? [];
    group.push(item);
    acc[key] = group;
    return acc;
  }, {} as Record<TKey, T[]>);
}
