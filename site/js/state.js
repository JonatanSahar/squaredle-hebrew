export const STORAGE_PREFIX = "squaredle-he:v1";

export function createEmptyState() {
  return {
    found: [],
    revealed: false,
    firstPlayedAt: null,
  };
}

export function storageKey(dateKey) {
  return `${STORAGE_PREFIX}:${dateKey}`;
}

export function loadState(dateKey) {
  try {
    const raw = localStorage.getItem(storageKey(dateKey));
    if (!raw) {
      return createEmptyState();
    }

    const parsed = JSON.parse(raw);
    return {
      found: Array.isArray(parsed?.found) ? [...new Set(parsed.found.filter(Boolean))] : [],
      revealed: Boolean(parsed?.revealed),
      firstPlayedAt: typeof parsed?.firstPlayedAt === "string" ? parsed.firstPlayedAt : null,
    };
  } catch {
    return createEmptyState();
  }
}

export function saveState(dateKey, state) {
  const payload = {
    found: Array.isArray(state?.found) ? [...new Set(state.found)] : [],
    revealed: Boolean(state?.revealed),
    firstPlayedAt: state?.firstPlayedAt ?? null,
  };

  try {
    localStorage.setItem(storageKey(dateKey), JSON.stringify(payload));
  } catch {
    // Mobile browsers can evict or reject localStorage writes. v1 degrades silently.
  }
}

export function todayKeyJerusalem(now = new Date()) {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Jerusalem",
  });
  return formatter.format(now);
}
