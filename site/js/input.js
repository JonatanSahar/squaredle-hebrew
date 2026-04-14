import { isAdjacent, pathHasCell, sameCell } from "./adjacency.js";
import {
  cellFromElement,
  cellFromPoint,
  setBoardDisabled,
  setSelectedPath,
} from "./board.js";

const DRAG_THRESHOLD = 10;
const DOUBLE_TAP_MS = 420;

export function attachInput(
  boardEl,
  {
    onCommit,
    onSelectionChange,
    submitButton = null,
    clearButton = null,
  } = {},
) {
  let enabled = true;
  let path = [];
  let session = null;
  let lastTap = { key: null, at: 0 };

  function syncButtons() {
    const hasSelection = path.length > 0;
    if (submitButton) {
      submitButton.disabled = !enabled || !hasSelection;
    }
    if (clearButton) {
      clearButton.disabled = !enabled || !hasSelection;
    }
  }

  function emitSelection() {
    const word = path.map((cell) => cell.letter).join("");
    onSelectionChange?.(word, [...path]);
    syncButtons();
  }

  function setPath(nextPath) {
    path = nextPath;
    setSelectedPath(boardEl, path);
    emitSelection();
  }

  function clearPath() {
    setPath([]);
  }

  function startPath(cell) {
    if (!cell) {
      clearPath();
      return;
    }
    setPath([cell]);
  }

  function appendCell(cell) {
    if (!cell) {
      return false;
    }

    if (!path.length) {
      setPath([cell]);
      return true;
    }

    const last = path[path.length - 1];
    if (sameCell(last, cell) || pathHasCell(path, cell) || !isAdjacent(last, cell)) {
      return false;
    }

    setPath([...path, cell]);
    return true;
  }

  function commit(source) {
    const word = path.map((cell) => cell.letter).join("");
    const committedPath = [...path];
    clearPath();

    if (word) {
      onCommit?.(word, committedPath, source);
    }
  }

  function resetPointerSession() {
    session = null;
  }

  function handleTap(cell) {
    if (!cell) {
      return;
    }

    const key = `${cell.row}:${cell.col}`;
    const last = path[path.length - 1];
    const now = Date.now();

    if (
      sameCell(last, cell) &&
      path.length >= 4 &&
      lastTap.key === key &&
      now - lastTap.at <= DOUBLE_TAP_MS
    ) {
      commit("double-tap");
      lastTap = { key: null, at: 0 };
      return;
    }

    if (!path.length) {
      startPath(cell);
    } else if (sameCell(last, cell)) {
      // Keep the current path; a repeated tap can become a double-tap commit.
    } else if (pathHasCell(path, cell) || !isAdjacent(last, cell)) {
      startPath(cell);
    } else {
      appendCell(cell);
    }

    lastTap = { key, at: now };
  }

  boardEl.addEventListener("pointerdown", (event) => {
    if (!enabled) {
      return;
    }

    const downCell = cellFromElement(event.target);
    if (!downCell) {
      return;
    }

    event.preventDefault();
    boardEl.setPointerCapture?.(event.pointerId);
    session = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      downCell,
      dragStarted: false,
    };
  });

  boardEl.addEventListener("pointermove", (event) => {
    if (!enabled || !session || event.pointerId !== session.pointerId) {
      return;
    }

    const hovered = cellFromPoint(boardEl, event.clientX, event.clientY);
    const distance = Math.hypot(event.clientX - session.startX, event.clientY - session.startY);

    if (!session.dragStarted) {
      const movedOffStart = hovered && !sameCell(hovered, session.downCell);
      if (distance < DRAG_THRESHOLD && !movedOffStart) {
        return;
      }

      session.dragStarted = true;
      startPath(session.downCell);
    }

    appendCell(hovered);
  });

  boardEl.addEventListener("pointerup", (event) => {
    if (!session || event.pointerId !== session.pointerId) {
      return;
    }

    boardEl.releasePointerCapture?.(event.pointerId);
    const activeSession = session;
    resetPointerSession();

    if (activeSession.dragStarted) {
      commit("swipe");
      return;
    }

    handleTap(activeSession.downCell);
  });

  boardEl.addEventListener("pointercancel", (event) => {
    if (!session || event.pointerId !== session.pointerId) {
      return;
    }

    boardEl.releasePointerCapture?.(event.pointerId);
    resetPointerSession();
  });

  submitButton?.addEventListener("click", () => {
    if (!enabled || !path.length) {
      return;
    }
    commit("submit");
  });

  clearButton?.addEventListener("click", () => {
    if (!enabled) {
      return;
    }
    clearPath();
  });

  syncButtons();

  return {
    clear() {
      clearPath();
    },
    setEnabled(nextEnabled) {
      enabled = Boolean(nextEnabled);
      setBoardDisabled(boardEl, !enabled);
      if (!enabled) {
        clearPath();
      } else {
        syncButtons();
      }
    },
  };
}
