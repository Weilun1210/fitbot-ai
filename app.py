"""FitBox Streamlit front end for the Dialogflow ES agent.

The website provides an accessible question builder and embeds Dialogflow
Messenger. Dialogflow and the PythonAnywhere webhook remain responsible for
answering questions from megaGymDataset.csv.
"""

from textwrap import dedent

import streamlit as st
import streamlit.components.v1 as components


AGENT_ID = "8ff14895-4120-431e-b4ef-015ed78ce0cc"

st.set_page_config(
    page_title="FitBox AI Assistant",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      #MainMenu, header, footer, [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
      }
      [data-testid="stAppViewContainer"] { background: #eef1e8; }
      [data-testid="stMain"] {
        overflow: hidden !important;
      }
      [data-testid="stMainBlockContainer"] {
        max-width: none;
        width: 100%;
        height: 100vh;
        min-height: 100vh;
        margin-inline: auto;
        padding: 0;
        overflow: hidden;
      }
      [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
        height: 100vh !important;
        min-height: 100vh !important;
        gap: 0 !important;
      }
      [data-testid="stElementContainer"]:has(iframe[title="st.iframe"]) {
        height: 100vh !important;
        min-height: 100vh !important;
        max-height: 100vh !important;
        flex: 0 0 100vh !important;
      }
      iframe[title="st.iframe"] {
        display: block;
        width: 100% !important;
        height: 100vh !important;
        border-radius: 0;
        box-shadow: none;
      }
      @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding: 0; }
        iframe[title="st.iframe"] { border-radius: 0; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

page = dedent(
    """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap" rel="stylesheet" />
        <script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>
        <style>
          :root {
            --ink: #151a12;
            --muted: #687064;
            --lime: #b8f22e;
            --lime-dark: #6f930d;
            --paper: #fbfcf7;
            --line: #dfe4d8;
            --drawer-width: 430px;
            --card-shadow: 0 8px 24px rgba(25, 31, 18, .08);
          }
          * { box-sizing: border-box; }
          html, body {
            margin: 0;
            min-height: 100%;
            overflow: hidden;
            background: #eef1e8;
            color: var(--ink);
            font-family: "DM Sans", system-ui, sans-serif;
            font-size: 18px;
          }
          button, select, input { font: inherit; }
          button:focus-visible, select:focus-visible, input:focus-visible {
            outline: 3px solid rgba(111, 147, 13, .34);
            outline-offset: 2px;
          }
          .shell {
            height: 100vh;
            width: 100%;
            margin-inline: auto;
            display: grid;
            grid-template-rows: auto minmax(0, 1fr);
            overflow: hidden;
            background: var(--paper);
            border: 0;
            border-radius: 0;
          }
          .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            padding: 15px 28px;
            background: #171b14;
            color: white;
          }
          .brand { display: flex; align-items: center; gap: 16px; min-width: 0; }
          .mark {
            width: 56px;
            height: 56px;
            flex: 0 0 56px;
            display: grid;
            place-items: center;
            border-radius: 15px;
            background: var(--lime);
            color: #11150e;
            font-size: 32px;
          }
          h1 { margin: 0; font: 800 26px/1.2 "Manrope", sans-serif; }
          .subtitle { margin-top: 5px; color: #b9c0b4; font-size: 16px; }
          .status {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #dce3d7;
            font-size: 16px;
            white-space: nowrap;
          }
          .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--lime);
            box-shadow: 0 0 0 4px rgba(184,242,46,.12);
          }
          .workspace {
            position: relative;
            display: flex;
            min-width: 0;
            min-height: 0;
            overflow: hidden;
            background: #f4f6ef;
          }
          .drawer {
            position: relative;
            z-index: 4;
            flex: 0 0 0;
            width: 0;
            max-width: 0;
            min-width: 0;
            overflow: hidden;
            opacity: 0;
            pointer-events: none;
            transform: translateX(-102%);
            background: #fbfcf7;
            border-right: 1px solid var(--line);
            box-shadow: 18px 0 40px rgba(18, 22, 15, .16);
            transition: flex-basis .24s ease, width .24s ease, max-width .24s ease, opacity .18s ease, transform .24s ease;
          }
          .workspace.drawer-open .drawer {
            flex-basis: var(--drawer-width);
            width: var(--drawer-width);
            max-width: var(--drawer-width);
            opacity: 1;
            pointer-events: auto;
            transform: translateX(0);
          }
          .drawer-inner {
            width: var(--drawer-width);
            height: 100%;
            overflow-y: auto;
            padding: 86px 28px 32px;
            scrollbar-width: thin;
            scrollbar-color: #c9d0c1 transparent;
          }
          .drawer-toggle {
            position: absolute;
            top: 72px;
            left: 12px;
            z-index: 6;
            width: 54px;
            height: 54px;
            display: grid;
            place-items: center;
            border: 1px solid #c8d0c0;
            border-radius: 14px;
            background: #171b14;
            color: var(--lime);
            box-shadow: 0 8px 18px rgba(21, 26, 18, .15);
            font-size: 35px;
            line-height: 1;
            cursor: pointer;
            transition: left .24s ease, top .24s ease, background .16s ease, color .16s ease;
          }
          .drawer-toggle:hover { background: #252c20; }
          .workspace.drawer-open .drawer-toggle {
            top: 15px;
            left: calc(var(--drawer-width) - 70px);
          }
          .drawer-title { margin: 0; font: 800 28px/1.2 "Manrope", sans-serif; }
          .drawer-lead { margin: 11px 0 26px; color: var(--muted); font-size: 17px; line-height: 1.55; }
          .field { margin-top: 21px; }
          .field label {
            display: block;
            margin-bottom: 8px;
            font-size: 16px;
            font-weight: 700;
            color: #323a2d;
          }
          .field select, .field input {
            width: 100%;
            min-height: 54px;
            border: 1px solid #cad2c3;
            border-radius: 12px;
            background: white;
            color: var(--ink);
            padding: 13px 15px;
            font-size: 17px;
          }
          .field input::placeholder { color: #858d80; }
          .step[hidden], .flow-section[hidden] { display: none !important; }
          .prompt-card {
            margin-top: 21px;
            padding: 19px;
            border: 1px solid #d5dfc7;
            border-radius: 14px;
            background: #f3f8e8;
          }
          .prompt-label {
            color: var(--lime-dark);
            font: 800 14px/1.2 "Manrope", sans-serif;
            letter-spacing: .09em;
            text-transform: uppercase;
          }
          .prompt-preview {
            min-height: 48px;
            margin: 9px 0 13px;
            color: #252d20;
            font-size: 17px;
            line-height: 1.45;
            overflow-wrap: anywhere;
          }
          .use-question {
            width: 100%;
            min-height: 52px;
            border: 0;
            border-radius: 11px;
            background: #171b14;
            color: white;
            font-weight: 700;
            font-size: 17px;
            cursor: pointer;
          }
          .use-question:hover:not(:disabled) { background: #2a3224; }
          .use-question:disabled { opacity: .45; cursor: not-allowed; }
          .examples {
            margin-top: 26px;
            padding-top: 21px;
            border-top: 1px solid var(--line);
          }
          .examples h3 { margin: 0 0 14px; font-size: 17px; }
          .example-list { display: grid; gap: 11px; }
          .example {
            width: 100%;
            border: 1px solid #d1d8ca;
            border-radius: 11px;
            padding: 13px 14px;
            background: white;
            color: #333b2e;
            text-align: left;
            font-size: 16px;
            line-height: 1.35;
            cursor: pointer;
          }
          .example:hover { border-color: #91b91e; background: #f4fadf; }
          .backdrop {
            display: none;
            position: absolute;
            inset: 0;
            z-index: 3;
            border: 0;
            background: rgba(15, 18, 13, .46);
            opacity: 0;
            pointer-events: none;
            transition: opacity .2s ease;
          }
          .chat-stage {
            position: relative;
            flex: 1 1 0;
            width: 100%;
            margin-inline: auto;
            min-width: 0;
            min-height: 0;
            overflow: hidden;
            background:
              radial-gradient(circle at 15% 10%, rgba(184,242,46,.09), transparent 27%),
              #f4f6ef;
          }
          .loading {
            position: absolute;
            inset: 0;
            display: grid;
            place-items: center;
            color: var(--muted);
            font-size: 17px;
          }
          df-messenger {
            --df-messenger-bot-message: #ffffff;
            --df-messenger-button-titlebar-color: #171b14;
            --df-messenger-button-titlebar-font-color: #ffffff;
            --df-messenger-chat-background-color: #f4f6ef;
            --df-messenger-font-color: #151a12;
            --df-messenger-input-box-color: #ffffff;
            --df-messenger-input-font-color: #151a12;
            --df-messenger-input-placeholder-font-color: #788071;
            --df-messenger-minimized-chat-close-icon-color: #ffffff;
            --df-messenger-send-icon: #6f930d;
            --df-messenger-user-message: #b8f22e;
            --df-messenger-chip-color: #f8faef;
            --df-messenger-chip-border-color: #cfd8c3;
            --df-messenger-focus-color: #6f930d;
            z-index: 2;
          }
          .toast {
            position: absolute;
            left: 50%;
            bottom: 16px;
            z-index: 8;
            transform: translate(-50%, 12px);
            opacity: 0;
            pointer-events: none;
            width: max-content;
            max-width: calc(100% - 32px);
            padding: 13px 18px;
            border-radius: 10px;
            background: #171b14;
            color: white;
            text-align: center;
            font-size: 16px;
            transition: .2s ease;
          }
          .toast.show { opacity: 1; transform: translate(-50%, 0); }
          @media (max-width: 760px) {
            .shell { height: 100vh; border-radius: 0; }
            .topbar { padding: 12px 16px; }
            .mark { width: 48px; height: 48px; flex-basis: 48px; font-size: 27px; }
            h1 { font-size: 22px; }
            .subtitle { font-size: 14px; }
            .status { display: none; }
            .drawer {
              position: absolute;
              inset: 0 auto 0 0;
              flex: 0 0 auto;
              width: min(88vw, var(--drawer-width));
              max-width: calc(100% - 42px);
              opacity: 0;
              transform: translateX(-102%);
              border-right: 1px solid var(--line);
              box-shadow: 18px 0 40px rgba(18, 22, 15, .18);
            }
            .workspace.drawer-open .drawer {
              flex-basis: auto;
              width: min(88vw, var(--drawer-width));
              max-width: calc(100% - 42px);
              opacity: 1;
              transform: translateX(0);
            }
            .drawer-inner { width: min(88vw, var(--drawer-width)); max-width: calc(100vw - 42px); }
            .workspace.drawer-open .drawer-toggle {
              left: min(calc(88vw - 52px), calc(var(--drawer-width) - 52px));
            }
            .backdrop { display: block; }
            .workspace.drawer-open .backdrop { opacity: .46; pointer-events: auto; }
          }
          @media (max-width: 390px) {
            .topbar { padding-right: 10px; }
            .subtitle { max-width: 225px; }
            .drawer-inner { padding-left: 16px; padding-right: 16px; }
          }
          @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
          }
        </style>
      </head>
      <body>
        <main class="shell">
          <header class="topbar">
            <div class="brand">
              <div class="mark" aria-hidden="true">💪</div>
              <div>
                <h1>FitBox AI Assistant</h1>
                <div class="subtitle">Personalised exercise discovery</div>
              </div>
            </div>
            <div class="status"><span class="dot" aria-hidden="true"></span> Dialogflow ES online</div>
          </header>

          <div class="workspace" id="workspace">
            <button class="drawer-toggle" id="drawer-toggle" type="button" aria-controls="question-guide" aria-expanded="false" aria-label="Open question guide">
              <span aria-hidden="true">›</span>
            </button>
            <button class="backdrop" id="backdrop" type="button" aria-label="Close question guide"></button>

            <aside class="drawer" id="question-guide" aria-label="AI question guide" aria-hidden="true">
              <div class="drawer-inner">
                <h2 class="drawer-title">Build a question</h2>
                <p class="drawer-lead">Choose what you want to find. FitBox will prepare a question for you.</p>

                <div class="field">
                  <label for="question-category">What would you like to ask?</label>
                  <select id="question-category">
                    <option value="">Choose a category</option>
                    <option value="personalised">Personalised recommendation</option>
                    <option value="body_part">Search by body part</option>
                    <option value="equipment">Search by equipment</option>
                    <option value="fitness_level">Search by fitness level</option>
                    <option value="exercise_type">Search by exercise type</option>
                    <option value="exercise_details">Exercise details</option>
                  </select>
                </div>

                <section class="flow-section" id="personalised-flow" hidden aria-label="Personalised recommendation options">
                  <div class="field step" id="step-level">
                    <label for="personal-level">1. Fitness level</label>
                    <select id="personal-level">
                      <option value="">Choose a level</option><option value="Any">Any level</option>
                      <option value="Beginner">Beginner</option><option value="Intermediate">Intermediate</option><option value="Expert">Expert</option>
                    </select>
                  </div>
                  <div class="field step" id="step-body" hidden>
                    <label for="personal-body">2. Body part</label>
                    <select id="personal-body">
                      <option value="">Choose a body part</option><option value="Any">Any body part</option>
                      <option>Abdominals</option><option>Abductors</option><option>Adductors</option><option>Biceps</option><option>Calves</option>
                      <option>Chest</option><option>Forearms</option><option>Glutes</option><option>Hamstrings</option><option>Lats</option>
                      <option>Lower Back</option><option>Middle Back</option><option>Neck</option><option>Quadriceps</option><option>Shoulders</option>
                      <option>Traps</option><option>Triceps</option>
                    </select>
                  </div>
                  <div class="field step" id="step-equipment" hidden>
                    <label for="personal-equipment">3. Equipment</label>
                    <select id="personal-equipment">
                      <option value="">Choose equipment</option><option value="Any">Any equipment</option>
                      <option>Bands</option><option>Barbell</option><option>Body Only</option><option>Cable</option><option>Dumbbell</option>
                      <option>E-Z Curl Bar</option><option>Exercise Ball</option><option>Foam Roll</option><option>Kettlebells</option>
                      <option>Machine</option><option>Medicine Ball</option><option>None</option><option>Other</option>
                    </select>
                  </div>
                  <div class="field step" id="step-type" hidden>
                    <label for="personal-type">4. Exercise type</label>
                    <select id="personal-type">
                      <option value="">Choose an exercise type</option><option value="Any">Any type</option>
                      <option>Cardio</option><option>Olympic Weightlifting</option><option>Plyometrics</option><option>Powerlifting</option>
                      <option>Strength</option><option>Stretching</option><option>Strongman</option>
                    </select>
                  </div>
                </section>

                <section class="flow-section" id="body_part-flow" hidden>
                  <div class="field"><label for="single-body">Body part</label><select id="single-body">
                    <option value="">Choose a body part</option><option>Abdominals</option><option>Abductors</option><option>Adductors</option>
                    <option>Biceps</option><option>Calves</option><option>Chest</option><option>Forearms</option><option>Glutes</option>
                    <option>Hamstrings</option><option>Lats</option><option>Lower Back</option><option>Middle Back</option><option>Neck</option>
                    <option>Quadriceps</option><option>Shoulders</option><option>Traps</option><option>Triceps</option>
                  </select></div>
                </section>
                <section class="flow-section" id="equipment-flow" hidden>
                  <div class="field"><label for="single-equipment">Equipment</label><select id="single-equipment">
                    <option value="">Choose equipment</option><option>Bands</option><option>Barbell</option><option>Body Only</option>
                    <option>Cable</option><option>Dumbbell</option><option>E-Z Curl Bar</option><option>Exercise Ball</option>
                    <option>Foam Roll</option><option>Kettlebells</option><option>Machine</option><option>Medicine Ball</option><option>None</option><option>Other</option>
                  </select></div>
                </section>
                <section class="flow-section" id="fitness_level-flow" hidden>
                  <div class="field"><label for="single-level">Fitness level</label><select id="single-level">
                    <option value="">Choose a level</option><option>Beginner</option><option>Intermediate</option><option>Expert</option>
                  </select></div>
                </section>
                <section class="flow-section" id="exercise_type-flow" hidden>
                  <div class="field"><label for="single-type">Exercise type</label><select id="single-type">
                    <option value="">Choose an exercise type</option><option>Cardio</option><option>Olympic Weightlifting</option>
                    <option>Plyometrics</option><option>Powerlifting</option><option>Strength</option><option>Stretching</option><option>Strongman</option>
                  </select></div>
                </section>
                <section class="flow-section" id="exercise_details-flow" hidden>
                  <div class="field"><label for="exercise-name">Exercise name</label>
                    <input id="exercise-name" type="text" autocomplete="off" placeholder="e.g. Partner plank band row" />
                  </div>
                </section>

                <div class="prompt-card" id="prompt-card" hidden>
                  <div class="prompt-label">Your question</div>
                  <div class="prompt-preview" id="prompt-preview" aria-live="polite"></div>
                  <button class="use-question" id="use-question" type="button" disabled>Use this question</button>
                </div>

                <section class="examples" aria-labelledby="examples-title">
                  <h3 id="examples-title">Example questions</h3>
                  <div class="example-list">
                    <button class="example" type="button" data-prompt="Give me beginner chest exercises">Give me beginner chest exercises</button>
                    <button class="example" type="button" data-prompt="Show me exercises using dumbbells">Show me exercises using dumbbells</button>
                    <button class="example" type="button" data-prompt="Show me strength exercises">Show me strength exercises</button>
                    <button class="example" type="button" data-prompt="Tell me about Partner plank band row">Tell me about Partner plank band row</button>
                  </div>
                </section>
              </div>
            </aside>

            <section class="chat-stage" id="chat-stage" aria-label="FitBox chat">
              <div class="loading" id="loading" role="status">Loading FitBox assistant…</div>
              <df-messenger intent="WELCOME" chat-title="FitBox Assistant" agent-id="__AGENT_ID__" language-code="en" expand></df-messenger>
              <div class="toast" id="toast" role="status" aria-live="polite">Question added — press Enter to send</div>
            </section>
          </div>
        </main>

        <script>
          const workspace = document.getElementById("workspace");
          const drawer = document.getElementById("question-guide");
          const drawerToggle = document.getElementById("drawer-toggle");
          const toggleGlyph = drawerToggle.querySelector("span");
          const backdrop = document.getElementById("backdrop");
          const category = document.getElementById("question-category");
          const messenger = document.querySelector("df-messenger");
          const stage = document.getElementById("chat-stage");
          const loading = document.getElementById("loading");
          const toast = document.getElementById("toast");
          const promptCard = document.getElementById("prompt-card");
          const promptPreview = document.getElementById("prompt-preview");
          const useQuestion = document.getElementById("use-question");
          const personalLevel = document.getElementById("personal-level");
          const personalBody = document.getElementById("personal-body");
          const personalEquipment = document.getElementById("personal-equipment");
          const personalType = document.getElementById("personal-type");
          const stepBody = document.getElementById("step-body");
          const stepEquipment = document.getElementById("step-equipment");
          const stepType = document.getElementById("step-type");
          const singleBody = document.getElementById("single-body");
          const singleEquipment = document.getElementById("single-equipment");
          const singleLevel = document.getElementById("single-level");
          const singleType = document.getElementById("single-type");
          const exerciseName = document.getElementById("exercise-name");
          let currentPrompt = "";
          let toastTimer;

          function isMobile() { return window.matchMedia("(max-width: 760px)").matches; }
          function setDrawer(open, returnFocus = false) {
            workspace.classList.toggle("drawer-open", open);
            drawerToggle.setAttribute("aria-expanded", String(open));
            drawerToggle.setAttribute("aria-label", open ? "Close question guide" : "Open question guide");
            drawer.setAttribute("aria-hidden", String(!open));
            toggleGlyph.textContent = open ? "‹" : "›";
            if (open) window.setTimeout(() => category.focus(), 260);
            else if (returnFocus) drawerToggle.focus();
          }
          drawerToggle.addEventListener("click", () => setDrawer(!workspace.classList.contains("drawer-open")));
          backdrop.addEventListener("click", () => setDrawer(false, true));
          document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && workspace.classList.contains("drawer-open")) setDrawer(false, true);
          });

          function showToast(message) {
            toast.textContent = message;
            toast.classList.add("show");
            window.clearTimeout(toastTimer);
            toastTimer = window.setTimeout(() => toast.classList.remove("show"), 1900);
          }
          function findChat() { return messenger.shadowRoot?.querySelector("df-messenger-chat"); }
          function findInput() {
            const userInput = findChat()?.shadowRoot?.querySelector("df-messenger-user-input");
            return userInput?.shadowRoot?.querySelector('input[aria-label="Talk to Agent"], input');
          }
          function setPrompt(value) {
            const input = findInput();
            if (!input) { showToast("Chat is still loading — try again in a moment"); return false; }
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
            if (setter) setter.call(input, value); else input.value = value;
            input.dispatchEvent(new InputEvent("input", { bubbles: true, composed: true, data: value, inputType: "insertText" }));
            input.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
            input.focus();
            showToast("Question added — press Enter to send");
            return true;
          }
          function updatePrompt(value) {
            currentPrompt = value.trim();
            promptPreview.textContent = currentPrompt || "Complete the choices above to build a question.";
            promptCard.hidden = !category.value;
            useQuestion.disabled = !currentPrompt;
          }
          function equipmentPhrase(value) {
            const phrases = {
              "Bands": "using bands", "Barbell": "using a barbell", "Body Only": "using bodyweight",
              "Cable": "using cables", "Dumbbell": "using dumbbells", "E-Z Curl Bar": "using an E-Z curl bar",
              "Exercise Ball": "using an exercise ball", "Foam Roll": "using a foam roll", "Kettlebells": "using kettlebells",
              "Machine": "using a machine", "Medicine Ball": "using a medicine ball", "None": "with no equipment",
              "Other": "using other equipment"
            };
            return phrases[value] || `using ${value.toLowerCase()}`;
          }
          function buildPersonalisedPrompt() {
            const values = [personalLevel.value, personalBody.value, personalEquipment.value, personalType.value];
            if (values.some((value) => !value)) { updatePrompt(""); return; }
            const words = ["Recommend"];
            if (personalLevel.value !== "Any") words.push(personalLevel.value.toLowerCase());
            if (personalType.value !== "Any") words.push(personalType.value.toLowerCase());
            words.push("exercises");
            let prompt = words.join(" ");
            if (personalBody.value !== "Any") prompt += ` for ${personalBody.value.toLowerCase()}`;
            if (personalEquipment.value !== "Any") prompt += ` ${equipmentPhrase(personalEquipment.value)}`;
            updatePrompt(prompt);
          }
          function resetFlowValues() {
            [personalLevel, personalBody, personalEquipment, personalType, singleBody, singleEquipment, singleLevel, singleType]
              .forEach((select) => { select.value = ""; });
            exerciseName.value = "";
            stepBody.hidden = true; stepEquipment.hidden = true; stepType.hidden = true;
            updatePrompt("");
          }
          category.addEventListener("change", () => {
            document.querySelectorAll(".flow-section").forEach((section) => { section.hidden = true; });
            resetFlowValues();
            if (category.value) {
              document.getElementById(`${category.value}-flow`).hidden = false;
              promptCard.hidden = false;
            }
          });
          personalLevel.addEventListener("change", () => {
            personalBody.value = ""; personalEquipment.value = ""; personalType.value = "";
            stepBody.hidden = !personalLevel.value; stepEquipment.hidden = true; stepType.hidden = true; updatePrompt("");
          });
          personalBody.addEventListener("change", () => {
            personalEquipment.value = ""; personalType.value = "";
            stepEquipment.hidden = !personalBody.value; stepType.hidden = true; updatePrompt("");
          });
          personalEquipment.addEventListener("change", () => {
            personalType.value = ""; stepType.hidden = !personalEquipment.value; updatePrompt("");
          });
          personalType.addEventListener("change", buildPersonalisedPrompt);
          singleBody.addEventListener("change", () => updatePrompt(singleBody.value ? `Show me exercises for ${singleBody.value.toLowerCase()}` : ""));
          singleEquipment.addEventListener("change", () => updatePrompt(singleEquipment.value ? `Show me exercises ${equipmentPhrase(singleEquipment.value)}` : ""));
          singleLevel.addEventListener("change", () => updatePrompt(singleLevel.value ? `Show me ${singleLevel.value.toLowerCase()} exercises` : ""));
          singleType.addEventListener("change", () => updatePrompt(singleType.value ? `Show me ${singleType.value.toLowerCase()} exercises` : ""));
          exerciseName.addEventListener("input", () => {
            const name = exerciseName.value.trim(); updatePrompt(name ? `Tell me about ${name}` : "");
          });
          useQuestion.addEventListener("click", () => {
            if (currentPrompt && setPrompt(currentPrompt) && isMobile()) setDrawer(false);
          });
          document.querySelectorAll(".example").forEach((button) => {
            button.addEventListener("click", () => { if (setPrompt(button.dataset.prompt) && isMobile()) setDrawer(false); });
          });

          function nestedRoots(root) {
            if (!root) return [];
            const roots = [root];
            root.querySelectorAll("*").forEach((element) => { if (element.shadowRoot) roots.push(...nestedRoots(element.shadowRoot)); });
            return roots;
          }
          function ensureShadowStyle(root, id, css) {
            if (!root || root.querySelector(`#${id}`)) return;
            const style = document.createElement("style");
            style.id = id;
            style.textContent = css;
            root.appendChild(style);
          }
          function findMessageList() {
            for (const root of nestedRoots(findChat()?.shadowRoot)) {
              const list = root.querySelector("#messageList");
              if (list) return list;
            }
            return null;
          }
          function themeChatContent() {
            nestedRoots(findChat()?.shadowRoot).forEach((nestedRoot) => {
              nestedRoot.querySelectorAll(".user-message").forEach((bubble) => {
                bubble.style.setProperty("background", "#b8f22e", "important");
                bubble.style.setProperty("background-color", "#b8f22e", "important");
                bubble.style.setProperty("color", "#151a12", "important");
                bubble.querySelectorAll("*").forEach((child) => child.style.setProperty("color", "#151a12", "important"));
              });
              if (nestedRoot.querySelector("#messageList")) {
                ensureShadowStyle(nestedRoot, "fitbox-message-theme", `
                  .message-list-wrapper {
                    flex: 1 1 0% !important;
                    height: auto !important;
                    min-height: 0 !important;
                    max-height: none !important;
                    overflow: hidden !important;
                  }
                  #messageList {
                    flex: 1 1 auto !important;
                    height: 100% !important;
                    max-height: none !important;
                    min-height: 0 !important;
                    overflow-x: hidden !important;
                    overflow-y: auto !important;
                    scrollbar-gutter: stable;
                    overscroll-behavior: contain;
                    scroll-behavior: smooth;
                    padding: 24px !important;
                  }
                  #messageList .message {
                    font-size: 18px !important;
                  }
                  #messageList .message.bot-message {
                    max-width: min(800px, calc(100% - 32px)) !important;
                    margin-right: 28px !important;
                    padding: 17px 22px !important;
                    border: 1px solid #dfe4d8;
                    border-radius: 16px !important;
                    box-shadow: 0 5px 16px rgba(25, 31, 18, .06);
                    line-height: 1.5 !important;
                  }
                  #messageList .animation:has(.user-message),
                  #messageList df-message:has(.user-message) {
                    display: block !important;
                    width: 100% !important;
                  }
                  #messageList .message.user-message {
                    display: block !important;
                    width: fit-content !important;
                    max-width: min(800px, calc(100% - 32px)) !important;
                    margin-left: auto !important;
                    margin-right: 8px !important;
                    padding: 16px 22px !important;
                    border-radius: 16px !important;
                  }
                  #messageList df-card {
                    align-self: flex-start;
                    display: block;
                    width: min(720px, calc(100% - 12px));
                    max-width: calc(100% - 12px);
                  }
                  @media (max-width: 520px) {
                    #messageList { padding: 12px !important; }
                    #messageList df-card { width: 100%; max-width: 100%; }
                    #messageList .message.bot-message { max-width: calc(100% - 8px) !important; margin-left: 8px !important; margin-right: 8px !important; }
                    #messageList .message.user-message { max-width: calc(100% - 8px) !important; margin-left: auto !important; margin-right: 4px !important; }
                  }
                `);
              }
              if (nestedRoot.host?.localName === "df-card") {
                ensureShadowStyle(nestedRoot, "fitbox-card-theme", `
                  .card-wrapper {
                    overflow: hidden;
                    margin-top: 12px !important;
                    border: 1px solid #d7dfcc !important;
                    border-left: 4px solid #b8f22e !important;
                    border-radius: 14px !important;
                    box-shadow: 0 8px 24px rgba(25, 31, 18, .08) !important;
                  }
                `);
              }
              if (nestedRoot.host?.localName === "df-description") {
                ensureShadowStyle(nestedRoot, "fitbox-description-theme", `
                  #descriptionWrapper {
                    padding: 21px 23px !important;
                    background: #ffffff !important;
                    border-radius: 0 !important;
                    font-family: "DM Sans", system-ui, sans-serif !important;
                  }
                  .title {
                    color: #151a12 !important;
                    font: 800 21px/1.35 "Manrope", system-ui, sans-serif !important;
                  }
                  .description-line {
                    color: #4d5748 !important;
                    font-size: 17px !important;
                    line-height: 1.45 !important;
                    padding-top: 6px !important;
                  }
                `);
              }
              if (nestedRoot.host?.localName === "df-accordion") {
                ensureShadowStyle(nestedRoot, "fitbox-accordion-theme", `
                  #dfAccordionWrapper {
                    padding: 19px 23px !important;
                    background: #f7faef !important;
                    border-top: 1px solid #dfe7d4;
                    border-radius: 0 !important;
                    color: #151a12 !important;
                    font-family: "DM Sans", system-ui, sans-serif !important;
                  }
                  #dfAccordionWrapper #title { color: #151a12 !important; font-size: 18px !important; font-weight: 700 !important; }
                  #dfAccordionWrapper #subtitle { color: #687064 !important; font-size: 16px !important; }
                  #dfAccordionWrapper #expandIcon { color: #6f930d !important; }
                  #dfAccordionWrapper #text { color: #384233 !important; font-size: 17px !important; line-height: 1.6 !important; }
                `);
              }
              if (nestedRoot.host?.localName === "df-messenger-user-input") {
                ensureShadowStyle(nestedRoot, "fitbox-input-theme", `
                  input, textarea { font-size: 18px !important; }
                  .input-container { min-height: 66px !important; }
                `);
              }
            });
          }
          let messageObserver = null;
          let observedMessageList = null;
          function scrollToLatest(delay = 0) {
            window.setTimeout(() => {
              window.requestAnimationFrame(() => {
                const list = findMessageList();
                if (list) list.scrollTop = list.scrollHeight;
                const shell = findChat()?.shadowRoot?.querySelector(".chat-wrapper");
                if (shell) shell.scrollTop = 0;
              });
            }, delay);
          }
          function observeMessageList() {
            const list = findMessageList();
            if (!list || list === observedMessageList) return;
            messageObserver?.disconnect();
            observedMessageList = list;
            messageObserver = new MutationObserver(() => {
              themeChatContent();
              scrollToLatest(40);
            });
            messageObserver.observe(list, { childList: true, subtree: true });
            scrollToLatest();
          }
          function fitChatToPanel() {
            const root = messenger.shadowRoot;
            const chat = findChat();
            const panel = chat?.shadowRoot?.querySelector(".chat-wrapper");
            const messengerWrapper = root?.querySelector(".df-messenger-wrapper");
            if (!root || !messengerWrapper || !chat || !panel) return false;
            const openButton = root.querySelector("#widgetIcon");
            if (openButton?.getAttribute("aria-expanded") !== "true" && messenger.dataset.autoOpened !== "true") {
              messenger.dataset.autoOpened = "true"; openButton.click(); return false;
            }
            if (openButton) openButton.style.setProperty("display", "none", "important");
            messenger.style.setProperty("position", "absolute", "important");
            messenger.style.setProperty("inset", "0", "important");
            messenger.style.setProperty("width", "100%", "important");
            messenger.style.setProperty("height", "100%", "important");
            messengerWrapper.style.setProperty("position", "absolute", "important");
            messengerWrapper.style.setProperty("inset", "0", "important");
            messengerWrapper.style.setProperty("width", "100%", "important");
            messengerWrapper.style.setProperty("height", "100%", "important");
            messengerWrapper.style.setProperty("overflow", "hidden", "important");
            chat.style.setProperty("position", "absolute", "important");
            chat.style.setProperty("inset", "0", "important");
            chat.style.setProperty("width", "auto", "important");
            chat.style.setProperty("height", "auto", "important");
            chat.style.setProperty("max-height", "none", "important");
            chat.style.setProperty("border-radius", "0", "important");
            chat.style.setProperty("overflow", "hidden", "important");
            chat.style.setProperty("box-shadow", "none", "important");
            panel.classList.remove("chat-min");
            panel.style.setProperty("position", "absolute", "important");
            panel.style.setProperty("inset", "0", "important");
            panel.style.setProperty("width", "100%", "important");
            panel.style.setProperty("min-width", "0", "important");
            panel.style.setProperty("max-width", "none", "important");
            panel.style.setProperty("height", "100%", "important");
            panel.style.setProperty("min-height", "0", "important");
            panel.style.setProperty("max-height", "none", "important");
            panel.style.setProperty("display", "flex", "important");
            panel.style.setProperty("flex-direction", "column", "important");
            panel.style.setProperty("border-radius", "0", "important");
            panel.style.setProperty("overflow", "hidden", "important");
            panel.style.setProperty("box-shadow", "none", "important");
            panel.scrollTop = 0;
            if (panel.dataset.fitboxScrollPinned !== "true") {
              panel.dataset.fitboxScrollPinned = "true";
              panel.addEventListener("scroll", () => {
                if (panel.scrollTop !== 0) panel.scrollTop = 0;
              }, { passive: true });
            }
            const messageWrapper = panel.querySelector(".message-list-wrapper");
            if (messageWrapper) {
              messageWrapper.style.setProperty("flex", "1 1 0%", "important");
              messageWrapper.style.setProperty("height", "auto", "important");
              messageWrapper.style.setProperty("min-height", "0", "important");
              messageWrapper.style.setProperty("max-height", "none", "important");
              messageWrapper.style.setProperty("overflow", "hidden", "important");
            }
            const inputShell = panel.querySelector("df-messenger-user-input");
            if (inputShell) {
              inputShell.style.setProperty("flex", "0 0 auto", "important");
              inputShell.style.setProperty("position", "relative", "important");
              inputShell.style.setProperty("inset", "auto", "important");
              inputShell.style.setProperty("width", "100%", "important");
            }
            root.querySelectorAll("df-messenger-chat-bubble").forEach((node) => node.style.setProperty("display", "none", "important"));
            themeChatContent(); observeMessageList(); loading.style.display = "none"; return true;
          }
          let attempts = 0;
          const fitTimer = window.setInterval(() => { attempts += 1; fitChatToPanel(); if (attempts > 80) window.clearInterval(fitTimer); }, 125);
          window.setInterval(() => { themeChatContent(); observeMessageList(); }, 700);
          window.addEventListener("dfMessengerLoaded", () => { fitChatToPanel(); scrollToLatest(120); });
          messenger.addEventListener("df-messenger-loaded", () => { fitChatToPanel(); scrollToLatest(120); });
          messenger.addEventListener("df-user-input-entered", () => scrollToLatest(80));
          messenger.addEventListener("df-response-received", () => scrollToLatest(220));
          window.addEventListener("resize", fitChatToPanel);
          new ResizeObserver(fitChatToPanel).observe(stage);
        </script>
      </body>
    </html>
    """
).replace("__AGENT_ID__", AGENT_ID)

components.html(page, height=900, scrolling=False)
