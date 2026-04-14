export function sameCell(a, b) {
  return Boolean(a && b && a.row === b.row && a.col === b.col);
}

export function isAdjacent(a, b) {
  if (!a || !b || sameCell(a, b)) {
    return false;
  }

  const rowDelta = Math.abs(a.row - b.row);
  const colDelta = Math.abs(a.col - b.col);
  return rowDelta <= 1 && colDelta <= 1;
}

export function pathHasCell(path, cell) {
  return path.some((entry) => sameCell(entry, cell));
}
