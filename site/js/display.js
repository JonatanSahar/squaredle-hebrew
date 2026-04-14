export const FINAL_FORMS = Object.freeze({
  כ: "ך",
  מ: "ם",
  נ: "ן",
  פ: "ף",
  צ: "ץ",
});

export function toDisplay(word) {
  if (!word) {
    return word;
  }

  const last = word[word.length - 1];
  return `${word.slice(0, -1)}${FINAL_FORMS[last] ?? last}`;
}

export function toDisplayWords(words) {
  return words.map((word) => toDisplay(word));
}
