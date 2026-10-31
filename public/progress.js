const authForm = document.querySelector("#auth-form");
const authStatus = document.querySelector("#auth-status");
const accountPanel = document.querySelector("#account-panel");
const progressSection = document.querySelector("#progress-section");
const savePanel = document.querySelector("#save-panel");
const historyList = document.querySelector("#practice-history");
const historyEmpty = document.querySelector("#history-empty");
const saveForm = document.querySelector("#progress-form");
const saveStatus = document.querySelector("#save-status");
const saveButton = document.querySelector("#save-score-button");
const recordCategory = document.querySelector("#record-category");
const worksheetCategory = document.querySelector("#category");

for (const option of worksheetCategory.options) {
  recordCategory.add(new Option(option.textContent, option.value));
}

const categoryLabels = new Map(
  [...document.querySelectorAll("#category option")].map((option) => [option.value, option.textContent]),
);

let supabase;
let signedInUser = null;
let currentPractice = null;

function localDate() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 10);
}

function setAuthStatus(message, isError = false) {
  authStatus.textContent = message;
  authStatus.classList.toggle("error", isError);
}

function setSaveStatus(message, isError = false) {
  saveStatus.textContent = message;
  saveStatus.classList.toggle("error", isError);
}

function renderAccount() {
  const isSignedIn = Boolean(signedInUser);
  authForm.hidden = isSignedIn;
  accountPanel.hidden = !isSignedIn;
  progressSection.hidden = !isSignedIn;
  savePanel.hidden = !isSignedIn || !currentPractice;

  if (isSignedIn) {
    document.querySelector("#signed-in-email").textContent = `Signed in as ${signedInUser.email}`;
  }

  if (currentPractice) {
    recordCategory.value = currentPractice.category;
    document.querySelector("#record-topic").textContent =
      `Choose the main topic to record for this ${currentPractice.totalQuestions}-question worksheet. It defaults to ${currentPractice.label}.`;
  }
}

async function loadHistory() {
  if (!signedInUser || !supabase) return;

  const { data, error } = await supabase
    .from("practice_sessions")
    .select("id, topic, practice_date, score, total_questions")
    .order("practice_date", { ascending: false })
    .order("created_at", { ascending: false })
    .limit(30);

  if (error) {
    historyList.replaceChildren();
    historyEmpty.hidden = false;
    historyEmpty.textContent = `Could not load your history: ${error.message}`;
    return;
  }

  historyList.replaceChildren();
  historyEmpty.hidden = data.length > 0;
  historyEmpty.textContent = "Your saved results will appear here.";

  for (const record of data) {
    const item = document.createElement("li");
    const topic = document.createElement("span");
    const result = document.createElement("span");
    topic.className = "history-topic";
    topic.textContent = `${record.practice_date} · ${categoryLabels.get(record.topic) ?? record.topic}`;
    result.className = "history-result";
    result.textContent = `${record.score} / ${record.total_questions}`;
    item.append(topic, result);
    historyList.append(item);
  }
}

async function start() {
  document.querySelector("#practice-date").value = localDate();

  try {
    const { createClient } = await import("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/+esm");
    const response = await fetch("/api/config");
    if (!response.ok) throw new Error("Progress tracking is not configured yet.");
    const config = await response.json();
    if (!config.supabaseUrl || !config.supabasePublishableKey) {
      throw new Error("Progress tracking is not configured yet.");
    }

    supabase = createClient(config.supabaseUrl, config.supabasePublishableKey);

    supabase.auth.onAuthStateChange((_event, session) => {
      signedInUser = session?.user ?? null;
      renderAccount();
      setTimeout(() => loadHistory(), 0);
    });

    const { data, error } = await supabase.auth.getSession();
    if (error) throw error;
    signedInUser = data.session?.user ?? null;
    renderAccount();
    await loadHistory();
  } catch (error) {
    setAuthStatus(error.message, true);
  }
}

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!supabase) return;

  const email = document.querySelector("#auth-email").value.trim();
  const password = document.querySelector("#auth-password").value;
  const signInButton = document.querySelector("#sign-in-button");
  signInButton.disabled = true;
  setAuthStatus("Signing in…");

  try {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    setAuthStatus("");
  } catch (error) {
    setAuthStatus(error.message, true);
  } finally {
    signInButton.disabled = false;
  }
});

document.querySelector("#sign-up-button").addEventListener("click", async () => {
  if (!supabase) return;

  const email = document.querySelector("#auth-email").value.trim();
  const password = document.querySelector("#auth-password").value;
  if (!authForm.reportValidity()) return;

  const signUpButton = document.querySelector("#sign-up-button");
  signUpButton.disabled = true;
  setAuthStatus("Creating your account…");

  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: window.location.origin },
    });
    if (error) throw error;
    setAuthStatus(data.session ? "Account created and signed in." : "Check your email to confirm your account.");
  } catch (error) {
    setAuthStatus(error.message, true);
  } finally {
    signUpButton.disabled = false;
  }
});

document.querySelector("#sign-out-button").addEventListener("click", async () => {
  if (!supabase) return;
  const { error } = await supabase.auth.signOut();
  setAuthStatus(error ? error.message : "You have signed out.", Boolean(error));
});

document.addEventListener("worksheet:generated", (event) => {
  currentPractice = event.detail;
  renderAccount();
  setSaveStatus("");
});

saveForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!signedInUser || !currentPractice || !supabase) return;

  const score = Number(document.querySelector("#practice-score").value);
  const practiceDate = document.querySelector("#practice-date").value;
  if (!Number.isInteger(score) || score < 0 || score > currentPractice.totalQuestions) {
    setSaveStatus(`Enter a whole-number score from 0 to ${currentPractice.totalQuestions}.`, true);
    return;
  }

  saveButton.disabled = true;
  setSaveStatus("Saving your result…");
  try {
    const { error } = await supabase.from("practice_sessions").insert({
      user_id: signedInUser.id,
      topic: recordCategory.value,
      practice_date: practiceDate,
      score,
      total_questions: currentPractice.totalQuestions,
    });
    if (error) throw error;

    document.querySelector("#practice-score").value = "";
    document.querySelector("#practice-date").value = localDate();
    setSaveStatus("Result saved.");
    await loadHistory();
  } catch (error) {
    setSaveStatus(error.message, true);
  } finally {
    saveButton.disabled = false;
  }
});

start();
