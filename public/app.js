const form = document.querySelector("#worksheet-form");
const categorySelect = document.querySelector("#category");
const worksheet = document.querySelector("#worksheet");
const actions = document.querySelector("#worksheet-actions");
const statusText = document.querySelector("#status");
const generateButton = document.querySelector("#generate-button");
const answersButton = document.querySelector("#answers-button");
const answerKey = document.querySelector("#answer-key");

function addQuestion(list, question) {
  const item = document.createElement("li");
  item.textContent = question.prompt;
  list.append(item);
}

function addAnswer(list, question) {
  const item = document.createElement("li");
  item.textContent = `${question.answer} (${question.prompt.replace(/\s*=\s*$/, "")})`;
  list.append(item);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  generateButton.disabled = true;
  statusText.textContent = "Generating your worksheet…";
  try {
    const response = await fetch("/api/worksheet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category: categorySelect.value }),
    });
    if (!response.ok) throw new Error("The worksheet could not be generated. Please try again.");
    const data = await response.json();
    const mainList = document.querySelector("#main-questions");
    const mixedList = document.querySelector("#mixed-questions");
    const answersList = document.querySelector("#answers-list");
    mainList.replaceChildren();
    mixedList.replaceChildren();
    answersList.replaceChildren();
    data.single.forEach((question) => addQuestion(mainList, question));
    data.mixed.forEach((question) => addQuestion(mixedList, question));
    [...data.single, ...data.mixed].forEach((question) => addAnswer(answersList, question));
    document.querySelector("#main-heading").textContent = categorySelect.selectedOptions[0].text;
    answerKey.hidden = true;
    answersButton.textContent = "Show answers";
    answersButton.setAttribute("aria-expanded", "false");
    worksheet.hidden = false;
    actions.hidden = false;
    statusText.textContent = "Your new 30-question worksheet is ready.";
  } catch (error) {
    statusText.textContent = error.message;
  } finally {
    generateButton.disabled = false;
  }
});

document.querySelector("#print-button").addEventListener("click", () => window.print());
answersButton.addEventListener("click", () => {
  answerKey.hidden = !answerKey.hidden;
  const expanded = !answerKey.hidden;
  answersButton.textContent = expanded ? "Hide answers" : "Show answers";
  answersButton.setAttribute("aria-expanded", String(expanded));
});
