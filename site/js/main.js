import { flashFoundPath, renderBoard } from "./board.js";
import { toDisplay } from "./display.js";
import { attachInput } from "./input.js";
import { loadState, saveState, todayKeyJerusalem } from "./state.js";

const boardEl = document.getElementById("board");
const currentEl = document.getElementById("current");
const statusEl = document.getElementById("status");
const difficultyEl = document.getElementById("difficulty");
const progressEl = document.getElementById("progress");
const puzzleDateEl = document.getElementById("puzzle-date");
const foundCountEl = document.getElementById("found-count");
const foundListEl = document.getElementById("found-list");
const foundEmptyEl = document.getElementById("found-empty");
const answersPanelEl = document.getElementById("answers-panel");
const answersSummaryEl = document.getElementById("answers-summary");
const answersEl = document.getElementById("answers");
const submitButton = document.getElementById("submit");
const clearButton = document.getElementById("clear");
const revealButton = document.getElementById("reveal");

const difficultyLabels = {
  easy: "קל",
  medium: "בינוני",
  hard: "קשה",
};

const wordCollator = new Intl.Collator("he");
const dateKey = todayKeyJerusalem();

let puzzle = null;
let answerSet = new Set();
let state = loadState(dateKey);
let inputController = null;

function setStatus(message) {
  statusEl.textContent = message;
}

function setCurrentSelection(word = "") {
  currentEl.textContent = word || "\u00a0";
}

function formatDate(dateText) {
  const [year, month, day] = dateText.split("-");
  if (!year || !month || !day) {
    return dateText;
  }
  return `${day}.${month}.${year}`;
}

function compareWords(left, right) {
  return left.length - right.length || wordCollator.compare(toDisplay(left), toDisplay(right));
}

function markFirstPlayed() {
  if (!state.firstPlayedAt) {
    state.firstPlayedAt = new Date().toISOString();
  }
}

function persistState() {
  saveState(dateKey, state);
}

function syncStoredFoundWords() {
  const filtered = [...new Set(state.found.filter((word) => answerSet.has(word)))];
  if (filtered.length !== state.found.length) {
    state.found = filtered;
    persistState();
  } else {
    state.found = filtered;
  }
}

function renderFoundWords() {
  foundListEl.replaceChildren();
  const sortedFound = [...state.found].sort(compareWords);

  foundEmptyEl.classList.toggle("is-hidden", sortedFound.length > 0);
  for (const word of sortedFound) {
    const item = document.createElement("li");
    item.className = "word-chip";
    item.textContent = toDisplay(word);
    foundListEl.append(item);
  }
}

function renderAnswers() {
  const sortedAnswers = [...answerSet].sort(compareWords);
  const groups = new Map();

  for (const word of sortedAnswers) {
    const length = word.length;
    if (!groups.has(length)) {
      groups.set(length, []);
    }
    groups.get(length).push(word);
  }

  answersEl.replaceChildren();
  for (const [length, words] of groups) {
    const groupEl = document.createElement("section");
    groupEl.className = "answer-group";

    const titleEl = document.createElement("div");
    titleEl.className = "group-title";
    titleEl.textContent = `${length} אותיות`;
    groupEl.append(titleEl);

    const gridEl = document.createElement("div");
    gridEl.className = "answer-grid";
    for (const word of words) {
      const tag = document.createElement("span");
      tag.className = "answer-tag";
      if (state.found.includes(word)) {
        tag.classList.add("is-found");
      }
      tag.textContent = toDisplay(word);
      gridEl.append(tag);
    }

    groupEl.append(gridEl);
    answersEl.append(groupEl);
  }

  answersPanelEl.hidden = false;
  answersSummaryEl.textContent = `${answerSet.size} מילים`;
  revealButton.disabled = true;
  inputController?.setEnabled(false);
}

function updateProgress() {
  const total = puzzle?.counts?.total ?? answerSet.size ?? 0;
  progressEl.textContent = `${state.found.length} / ${total}`;
  foundCountEl.textContent = String(state.found.length);
  difficultyEl.textContent = difficultyLabels[puzzle?.difficulty] ?? "—";
  renderFoundWords();
}

function handleCommit(word, path) {
  if (!puzzle || state.revealed) {
    return;
  }

  if (word.length < 4) {
    setStatus("צריך לבחור לפחות 4 אותיות.");
    return;
  }

  if (state.found.includes(word)) {
    setStatus(`כבר נמצאה: ${toDisplay(word)}`);
    return;
  }

  if (!answerSet.has(word)) {
    setStatus(`${toDisplay(word)} אינה בתשובות של החידה.`);
    return;
  }

  markFirstPlayed();
  state.found = [...state.found, word];
  persistState();
  updateProgress();
  flashFoundPath(boardEl, path);
  setStatus(`נמצאה מילה: ${toDisplay(word)}`);

  if (state.found.length === answerSet.size) {
    setStatus("כל המילים נמצאו.");
  }
}

async function init() {
  puzzleDateEl.textContent = formatDate(dateKey);
  setCurrentSelection();
  submitButton.disabled = true;
  clearButton.disabled = true;

  try {
    const response = await fetch(`./puzzles/${dateKey}.json`, { cache: "no-store" });
    if (!response.ok) {
      if (response.status === 404) {
        console.warn(`Missing puzzle JSON for ${dateKey} under site/puzzles/.`);
      }
      throw new Error(`Puzzle fetch failed: ${response.status}`);
    }

    puzzle = await response.json();
    answerSet = new Set(Array.isArray(puzzle.answers) ? puzzle.answers : []);
    syncStoredFoundWords();

    renderBoard(
      boardEl,
      (Array.isArray(puzzle.grid) ? puzzle.grid : []).map((row) => [...row]),
    );

    inputController = attachInput(boardEl, {
      submitButton,
      clearButton,
      onSelectionChange(word) {
        setCurrentSelection(word);
      },
      onCommit(word, path) {
        handleCommit(word, path);
      },
    });

    updateProgress();

    if (state.revealed) {
      renderAnswers();
      setStatus("התשובות כבר נחשפו במכשיר הזה.");
    } else if (state.found.length > 0) {
      setStatus("ההתקדמות נשחזרה מהדפדפן.");
    } else {
      setStatus("גררו על הלוח או לחצו על אותיות כדי להרכיב מילים.");
    }
  } catch (error) {
    console.error(error);
    setStatus("לא נמצאה חידה לתאריך הזה.");
    difficultyEl.textContent = "—";
    progressEl.textContent = "0 / 0";
    revealButton.disabled = true;
    submitButton.disabled = true;
    clearButton.disabled = true;
  }
}

revealButton.addEventListener("click", () => {
  if (!puzzle || state.revealed) {
    return;
  }

  if (!window.confirm("להיכנע ולגלות את כל התשובות?")) {
    return;
  }

  markFirstPlayed();
  state.revealed = true;
  persistState();
  renderAnswers();
  setStatus("כל התשובות מוצגות.");
});

void init();
