export function cellKey(row, col) {
  return `${row}:${col}`;
}

export function renderBoard(boardEl, grid) {
  boardEl.replaceChildren();
  const rows = grid.length;
  const cols = grid[0]?.length ?? 0;
  boardEl.dataset.rows = String(rows);
  boardEl.dataset.cols = String(cols);
  boardEl.style.setProperty("--cols", String(cols));
  boardEl.style.setProperty("--rows", String(rows));

  for (let row = 0; row < grid.length; row += 1) {
    for (let col = 0; col < grid[row].length; col += 1) {
      const cell = document.createElement("button");
      cell.type = "button";
      cell.className = "cell";
      cell.dataset.row = String(row);
      cell.dataset.col = String(col);
      cell.dataset.letter = grid[row][col];
      cell.setAttribute("aria-label", `שורה ${row + 1}, עמודה ${col + 1}, ${grid[row][col]}`);
      cell.textContent = grid[row][col];
      boardEl.append(cell);
    }
  }
}

export function cellFromElement(element) {
  const cell = element?.closest?.(".cell");
  if (!cell) {
    return null;
  }

  return {
    row: Number(cell.dataset.row),
    col: Number(cell.dataset.col),
    letter: cell.dataset.letter ?? cell.textContent ?? "",
    el: cell,
  };
}

export function cellFromPoint(boardEl, x, y, { innerRatio = 1 } = {}) {
  const raw = document.elementFromPoint(x, y);
  if (!raw || !boardEl.contains(raw)) {
    return null;
  }

  const cellEl = raw.closest?.(".cell");
  if (!cellEl) {
    return null;
  }

  if (innerRatio < 1) {
    const rect = cellEl.getBoundingClientRect();
    const inset = (1 - innerRatio) / 2;
    const minX = rect.left + rect.width * inset;
    const maxX = rect.right - rect.width * inset;
    const minY = rect.top + rect.height * inset;
    const maxY = rect.bottom - rect.height * inset;
    if (x < minX || x > maxX || y < minY || y > maxY) {
      return null;
    }
  }

  return cellFromElement(cellEl);
}

export function getCellElement(boardEl, row, col) {
  return boardEl.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
}

export function setSelectedPath(boardEl, path) {
  const selected = new Set(path.map((cell) => cellKey(cell.row, cell.col)));
  for (const cell of boardEl.querySelectorAll(".cell")) {
    const key = cellKey(Number(cell.dataset.row), Number(cell.dataset.col));
    cell.classList.toggle("is-selected", selected.has(key));
  }
}

export function clearSelectedPath(boardEl) {
  for (const cell of boardEl.querySelectorAll(".cell.is-selected")) {
    cell.classList.remove("is-selected");
  }
}

export function flashFoundPath(boardEl, path) {
  for (const cell of path) {
    const element = getCellElement(boardEl, cell.row, cell.col);
    if (!element) {
      continue;
    }

    element.classList.add("is-found", "is-flash");
    window.setTimeout(() => {
      element.classList.remove("is-flash");
    }, 520);
    window.setTimeout(() => {
      element.classList.remove("is-found");
    }, 760);
  }
}

export function setBoardDisabled(boardEl, disabled) {
  for (const cell of boardEl.querySelectorAll(".cell")) {
    cell.disabled = disabled;
  }
}
