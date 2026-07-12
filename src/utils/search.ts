export function linearSearchIndex<T>(
  items: ReadonlyArray<T>,
  predicate: (item: T) => boolean
): number {
  for (let index = 0; index < items.length; index += 1) {
    const current = items[index];
    if (current !== undefined && predicate(current)) {
      return index;
    }
  }
  return -1;
}

export function linearSearch<T>(
  items: ReadonlyArray<T>,
  predicate: (item: T) => boolean
): T | null {
  const index = linearSearchIndex(items, predicate);
  if (index === -1) {
    return null;
  }
  return items[index] ?? null;
}

export function binarySearchIndex<T>(
  items: ReadonlyArray<T>,
  compareItemToTarget: (item: T) => number
): number {
  if (items.length === 0) {
    return -1;
  }

  let low = 0;
  let high = items.length - 1;

  while (low <= high) {
    const middle = Math.floor((low + high) / 2);
    const current = items[middle];
    if (current === undefined) {
      return -1;
    }
    const comparison = compareItemToTarget(current);

    if (comparison === 0) {
      return middle;
    }

    if (comparison < 0) {
      low = middle + 1;
    } else {
      high = middle - 1;
    }
  }

  return -1;
}

export function binarySearch<T>(
  items: ReadonlyArray<T>,
  compareItemToTarget: (item: T) => number
): T | null {
  const index = binarySearchIndex(items, compareItemToTarget);
  if (index === -1) {
    return null;
  }
  return items[index] ?? null;
}

export function binarySearchByNumberKey<T>(
  items: ReadonlyArray<T>,
  selector: (item: T) => number,
  target: number
): T | null {
  return binarySearch(items, (item) => selector(item) - target);
}

export function binarySearchByStringKey<T>(
  items: ReadonlyArray<T>,
  selector: (item: T) => string,
  target: string
): T | null {
  return binarySearch(items, (item) => selector(item).localeCompare(target));
}
