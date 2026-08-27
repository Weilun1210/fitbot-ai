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
          .topbar-actions { display: flex; align-items: center; gap: 16px; }
          .clear-chat {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            min-height: 40px;
            padding: 8px 13px;
            border: 1px solid rgba(255, 255, 255, .2);
            border-radius: 10px;
            background: rgba(255, 255, 255, .07);
            color: #f5f8f2;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: background .16s ease, border-color .16s ease, transform .16s ease;
          }
          .clear-chat:hover {
            border-color: rgba(184, 242, 46, .6);
            background: rgba(184, 242, 46, .12);
            transform: translateY(-1px);
          }
          .clear-chat:disabled { opacity: .58; cursor: wait; transform: none; }
          .clear-icon { color: var(--lime); font-size: 20px; line-height: 1; }
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
          .flow-note {
            margin: 18px 0 0;
            padding: 14px 16px;
            border-left: 4px solid var(--lime);
            border-radius: 9px;
            background: #f3f8e8;
            color: #44503d;
            font-size: 16px;
            line-height: 1.45;
          }
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
          .chat-hero {
            position: absolute;
            top: 112px;
            left: 50%;
            z-index: 3;
            width: min(820px, calc(100% - 96px));
            padding: 18px 30px 24px;
            transform: translateX(-50%);
            text-align: center;
            pointer-events: none;
            isolation: isolate;
            transition: opacity .28s ease, transform .28s ease, visibility .28s ease;
          }
          .chat-hero::before,
          .chat-hero::after {
            content: "";
            position: absolute;
            z-index: -1;
            border-radius: 50%;
            border: 1px solid rgba(111, 147, 13, .2);
          }
          .chat-hero::before {
            width: 230px;
            height: 230px;
            top: -74px;
            left: 2%;
            background: radial-gradient(circle, rgba(184,242,46,.13), transparent 68%);
          }
          .chat-hero::after {
            width: 160px;
            height: 160px;
            right: 5%;
            bottom: -48px;
            border-style: dashed;
          }
          .hero-kicker {
            display: inline-flex;
            align-items: center;
            gap: 9px;
            margin-bottom: 15px;
            padding: 7px 13px;
            border: 1px solid rgba(111, 147, 13, .28);
            border-radius: 999px;
            background: rgba(255, 255, 255, .72);
            box-shadow: 0 6px 18px rgba(25, 31, 18, .06);
            color: #5f7e0b;
            font: 800 12px/1 "Manrope", sans-serif;
            letter-spacing: .16em;
            text-transform: uppercase;
          }
          .hero-kicker::before {
            content: "";
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--lime);
            box-shadow: 0 0 0 4px rgba(184,242,46,.18);
          }
          .hero-title {
            margin: 0;
            color: #171b14;
            font: 900 clamp(42px, 5.2vw, 76px)/.96 "Manrope", sans-serif;
            letter-spacing: -.055em;
            text-wrap: balance;
          }
          .hero-title span {
            display: block;
            margin-top: 7px;
            color: #6f930d;
            text-shadow: 0 8px 28px rgba(111, 147, 13, .16);
          }
          .hero-copy {
            max-width: 610px;
            margin: 19px auto 0;
            color: #5c6657;
            font-size: 18px;
            line-height: 1.5;
          }
          .hero-pills {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 9px;
            margin-top: 19px;
          }
          .hero-pill {
            padding: 7px 12px;
            border: 1px solid #d5ddca;
            border-radius: 999px;
            background: rgba(251, 253, 247, .82);
            color: #4d5848;
            font-size: 13px;
            font-weight: 700;
            box-shadow: 0 5px 14px rgba(25, 31, 18, .05);
          }
          .chat-stage.conversation-active .chat-hero {
            opacity: 0;
            visibility: hidden;
            transform: translate(-50%, -18px) scale(.98);
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
            .topbar-actions { gap: 8px; }
            .clear-chat { padding: 8px 10px; }
            .chat-hero { top: 94px; width: calc(100% - 44px); padding-inline: 10px; }
            .hero-title { font-size: clamp(34px, 10vw, 52px); }
            .hero-copy { max-width: 430px; margin-top: 14px; font-size: 16px; }
            .hero-pills { margin-top: 14px; }
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
            .chat-hero { top: 82px; width: calc(100% - 30px); }
            .hero-kicker { margin-bottom: 11px; font-size: 10px; }
            .hero-title { font-size: 32px; }
            .hero-copy { font-size: 14px; }
            .hero-pills { display: none; }
            .clear-label { display: none; }
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
            <div class="topbar-actions">
              <button class="clear-chat" id="clear-chat" type="button" aria-label="Clear chat and start again">
                <span class="clear-icon" aria-hidden="true">↻</span>
                <span class="clear-label">Clear chat</span>
              </button>
              <div class="status"><span class="dot" aria-hidden="true"></span> Dialogflow ES online</div>
            </div>
          </header>

          <div class="workspace" id="workspace">
            <button class="drawer-toggle" id="drawer-toggle" type="button" aria-controls="question-guide" aria-expanded="false" aria-label="Open question guide">
              <span aria-hidden="true">›</span>
            </button>
            <button class="backdrop" id="backdrop" type="button" aria-label="Close question guide"></button>

            <aside class="drawer" id="question-guide" aria-label="AI question guide" aria-hidden="true">
              <div class="drawer-inner">
                <h2 class="drawer-title">Build a question</h2>
                <p class="drawer-lead">Choose a supported question. FitBox will prepare the exact wording for you.</p>

                <div class="field">
                  <label for="question-category">What would you like to ask?</label>
                  <select id="question-category">
                    <option value="">Choose a category</option>
                    <option value="general_recommendation">General exercise recommendation</option>
                    <option value="body_part">Search by body part</option>
                    <option value="equipment">Search by equipment</option>
                    <option value="fitness_level">Search by fitness level</option>
                    <option value="exercise_type">Search by exercise type</option>
                    <option value="tested_combination">Tested combined recommendation</option>
                    <option value="exercise_details">Exercise details</option>
                  </select>
                </div>

                <section class="flow-section" id="general_recommendation-flow" hidden aria-label="General exercise recommendation">
                  <p class="flow-note">This uses the trained phrase “Recommend exercises”.</p>
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
                <section class="flow-section" id="tested_combination-flow" hidden>
                  <div class="field"><label for="tested-combination">Verified combination</label><select id="tested-combination">
                    <option value="">Choose a tested question</option>
                    <option value="Recommend beginner chest exercises using dumbbells">Beginner · Chest · Dumbbell</option>
                    <option value="Show me expert barbell strength exercises">Expert · Barbell · Strength</option>
                    <option value="Find intermediate stretching exercises for lower back">Intermediate · Lower Back · Stretching</option>
                    <option value="Recommend dumbbell exercises for shoulders">Shoulders · Dumbbell</option>
                    <option value="Suggest beginner bodyweight exercises">Beginner · Bodyweight</option>
                    <option value="Find intermediate strength exercises">Intermediate · Strength</option>
                  </select></div>
                </section>
                <section class="flow-section" id="exercise_details-flow" hidden>
                  <div class="field"><label for="exercise-name">Recognised exercise</label><select id="exercise-name">
                    <option value="">Choose an exercise</option>
                    <option>Partner plank band row</option>
                    <option>Crunch</option>
                    <option>Barbell Bench Press - Medium Grip</option>
                    <option>Dumbbell Bicep Curl</option>
                    <option>Pushups</option>
                    <option>Deadlift with Bands</option>
                    <option>Pullups</option>
                    <option>Barbell Full Squat</option>
                  </select></div>
                </section>

                <div class="prompt-card" id="prompt-card" hidden>
                  <div class="prompt-label">Your question</div>
                  <div class="prompt-preview" id="prompt-preview" aria-live="polite"></div>
                  <button class="use-question" id="use-question" type="button" disabled>Use this question</button>
                </div>

                <section class="examples" aria-labelledby="examples-title">
                  <h3 id="examples-title">Example questions</h3>
                  <div class="example-list">
                    <button class="example" type="button" data-prompt="How do I use FitBox?">How do I use FitBox?</button>
                    <button class="example" type="button" data-prompt="Show me beginner exercises">Show me beginner exercises</button>
                    <button class="example" type="button" data-prompt="Show me exercises using dumbbells">Show me exercises using dumbbells</button>
                    <button class="example" type="button" data-prompt="Show me strength exercises">Show me strength exercises</button>
                    <button class="example" type="button" data-prompt="Recommend beginner chest exercises using dumbbells">Recommend beginner chest exercises using dumbbells</button>
                    <button class="example" type="button" data-prompt="Tell me about Partner plank band row">Tell me about Partner plank band row</button>
                  </div>
                </section>
              </div>
            </aside>

            <section class="chat-stage" id="chat-stage" aria-label="FitBox chat">
              <div class="loading" id="loading" role="status">Loading FitBox assistant…</div>
              <section class="chat-hero" id="chat-hero" aria-label="FitBox introduction">
                <div class="hero-kicker">Your training companion</div>
                <h2 class="hero-title">Train smarter.<span>Move stronger.</span></h2>
                <p class="hero-copy">Tell FitBox what you want to train, your fitness level, or the equipment you have.</p>
                <div class="hero-pills" aria-hidden="true">
                  <span class="hero-pill">Fitness level</span>
                  <span class="hero-pill">Body part</span>
                  <span class="hero-pill">Equipment</span>
                  <span class="hero-pill">Training type</span>
                </div>
              </section>
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
          const clearChatButton = document.getElementById("clear-chat");
          const loading = document.getElementById("loading");
          const toast = document.getElementById("toast");
          const promptCard = document.getElementById("prompt-card");
          const promptPreview = document.getElementById("prompt-preview");
          const useQuestion = document.getElementById("use-question");
          const singleBody = document.getElementById("single-body");
          const singleEquipment = document.getElementById("single-equipment");
          const singleLevel = document.getElementById("single-level");
          const singleType = document.getElementById("single-type");
          const testedCombination = document.getElementById("tested-combination");
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
          function findSendControl() {
            const userInput = findChat()?.shadowRoot?.querySelector("df-messenger-user-input");
            const root = userInput?.shadowRoot;
            return root?.querySelector(
              'button[aria-label="Send"], [role="button"][aria-label="Send"], #sendIcon, .send-button'
            );
          }
          function setPrompt(value, notify = true) {
            const input = findInput();
            if (!input) { showToast("Chat is still loading — try again in a moment"); return false; }
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
            if (setter) setter.call(input, value); else input.value = value;
            input.dispatchEvent(new InputEvent("input", { bubbles: true, composed: true, data: value, inputType: "insertText" }));
            input.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
            input.focus();
            if (notify) showToast("Question added — press Enter to send");
            return true;
          }
          let detailSendLockedUntil = 0;
          function sendPrompt(value) {
            if (!value || Date.now() < detailSendLockedUntil) return false;
            if (!setPrompt(value, false)) return false;
            detailSendLockedUntil = Date.now() + 1000;
            window.requestAnimationFrame(() => {
              const sendControl = findSendControl();
              if (sendControl) sendControl.click();
              else {
                findInput()?.dispatchEvent(new KeyboardEvent("keydown", {
                  key: "Enter", code: "Enter", keyCode: 13, which: 13,
                  bubbles: true, composed: true,
                }));
              }
              showToast("Opening exercise details…");
              scrollToLatest(100);
            });
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
          function resetFlowValues() {
            [singleBody, singleEquipment, singleLevel, singleType, testedCombination, exerciseName]
              .forEach((select) => { select.value = ""; });
            updatePrompt("");
          }
          category.addEventListener("change", () => {
            document.querySelectorAll(".flow-section").forEach((section) => { section.hidden = true; });
            resetFlowValues();
            if (category.value) {
              document.getElementById(`${category.value}-flow`).hidden = false;
              promptCard.hidden = false;
              if (category.value === "general_recommendation") updatePrompt("Recommend exercises");
            }
          });
          singleBody.addEventListener("change", () => updatePrompt(singleBody.value ? `Show me exercises for ${singleBody.value.toLowerCase()}` : ""));
          singleEquipment.addEventListener("change", () => updatePrompt(singleEquipment.value ? `Show me exercises ${equipmentPhrase(singleEquipment.value)}` : ""));
          singleLevel.addEventListener("change", () => updatePrompt(singleLevel.value ? `Show me ${singleLevel.value.toLowerCase()} exercises` : ""));
          singleType.addEventListener("change", () => updatePrompt(singleType.value ? `Show me ${singleType.value.toLowerCase()} exercises` : ""));
          testedCombination.addEventListener("change", () => updatePrompt(testedCombination.value));
          exerciseName.addEventListener("change", () => {
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
          const recommendationPageMarker = "#fitbox-recommendation-page=";
          let recommendationPagerSequence = 0;
          function recommendationCards() {
            return nestedRoots(findChat()?.shadowRoot)
              .filter((root) => root.host?.localName === "df-card")
              .map((root) => root.host);
          }
          function cardText(card) {
            return String(card?.shadowRoot?.textContent || card?.textContent || "")
              .replace(/\\s+/g, " ").trim();
          }
          function stylePagerCard(card, navigation = false) {
            if (!card?.shadowRoot) return;
            ensureShadowStyle(card.shadowRoot, "fitbox-pager-card-theme", `
              .card-wrapper {
                display: ${navigation ? "flex" : "block"} !important;
                gap: 10px !important;
                overflow: visible !important;
                margin-top: 8px !important;
                padding: 0 !important;
                border: 0 !important;
                border-left: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
              }
            `);
            nestedRoots(card.shadowRoot).forEach((root) => {
              if (root.host?.localName !== "df-button") return;
              const text = String(root.textContent || root.host.textContent || "").replace(/\\s+/g, " ").trim();
              const isArrow = /^(Previous page|Next page)$/.test(text);
              root.host.style.setProperty("display", "block", "important");
              root.host.style.setProperty("width", isArrow ? "calc(50% - 5px)" : "100%", "important");
              root.host.style.setProperty("margin", "0", "important");
              ensureShadowStyle(root, "fitbox-pager-button-theme", `
                button, #button, .button {
                  width: 100% !important;
                  min-height: 50px !important;
                  border-radius: 12px !important;
                  border: 1px solid #91bd1c !important;
                  background: ${isArrow ? "#ffffff" : "#b8f22e"} !important;
                  color: #151a12 !important;
                  font: 800 16px/1.2 "DM Sans", system-ui, sans-serif !important;
                  box-shadow: 0 5px 15px rgba(25, 31, 18, .08) !important;
                }
                button:hover, #button:hover, .button:hover {
                  background: #c8ff45 !important;
                  transform: translateY(-1px);
                }
              `);
            });
          }
          function updateRecommendationGroup(group, page, activated) {
            const cards = recommendationCards().filter((card) => card.dataset.fitboxPagerGroup === group);
            const showCard = cards.find((card) => card.dataset.fitboxPagerRole === "show");
            const navCard = cards.find((card) => card.dataset.fitboxPagerRole === "navigation");
            cards.filter((card) => card.dataset.fitboxResultIndex).forEach((card) => {
              const index = Number(card.dataset.fitboxResultIndex);
              const visible = page === 1 ? index <= 3 : index >= 4;
              card.style.setProperty("display", visible ? "block" : "none", "important");
            });
            if (showCard) {
              showCard.dataset.fitboxPagerActivated = String(activated);
              showCard.dataset.fitboxPagerPage = String(page);
              showCard.style.setProperty("display", activated ? "none" : "block", "important");
              stylePagerCard(showCard, false);
            }
            if (navCard) {
              navCard.style.setProperty("display", activated ? "block" : "none", "important");
              stylePagerCard(navCard, true);
              nestedRoots(navCard.shadowRoot).forEach((root) => {
                if (root.host?.localName !== "df-button") return;
                const text = String(root.textContent || root.host.textContent || "").replace(/\\s+/g, " ").trim();
                const disabled = (page === 1 && text === "Previous page") || (page === 2 && text === "Next page");
                root.host.style.setProperty("opacity", disabled ? ".42" : "1", "important");
                root.host.style.setProperty("pointer-events", disabled ? "none" : "auto", "important");
                root.host.setAttribute("aria-disabled", String(disabled));
              });
            }
          }
          function discoverRecommendationPagers() {
            const cards = recommendationCards();
            cards.forEach((card) => {
              const match = cardText(card).match(/(?:^|\\s)([1-6])\\.\\s/);
              if (match) card.dataset.fitboxResultIndex = match[1];
            });
            cards.forEach((showCard, showIndex) => {
              if (!cardText(showCard).includes("Show more exercises")) return;
              const navCard = cards.slice(showIndex + 1).find((card) => {
                const text = cardText(card);
                return text.includes("Previous page") && text.includes("Next page");
              });
              if (!navCard) return;
              const results = [];
              for (let index = showIndex - 1; index >= 0; index -= 1) {
                const card = cards[index];
                if (!card.dataset.fitboxResultIndex) {
                  if (results.length) break;
                  continue;
                }
                results.unshift(card);
                if (card.dataset.fitboxResultIndex === "1") break;
              }
              if (results.length < 4) return;
              const group = showCard.dataset.fitboxPagerGroup || `fitbox-pager-${++recommendationPagerSequence}`;
              showCard.dataset.fitboxPagerGroup = group;
              showCard.dataset.fitboxPagerRole = "show";
              navCard.dataset.fitboxPagerGroup = group;
              navCard.dataset.fitboxPagerRole = "navigation";
              results.forEach((card) => { card.dataset.fitboxPagerGroup = group; });
              const activated = showCard.dataset.fitboxPagerActivated === "true";
              const page = Number(showCard.dataset.fitboxPagerPage || "1");
              updateRecommendationGroup(group, page, activated);
            });
          }
          function setRecommendationPage(page, event) {
            discoverRecommendationPagers();
            const pathCard = event?.composedPath?.().find((node) => node?.localName === "df-card");
            let group = pathCard?.dataset?.fitboxPagerGroup;
            if (!group) {
              const latest = recommendationCards().filter((card) => card.dataset.fitboxPagerRole === "show").at(-1);
              group = latest?.dataset.fitboxPagerGroup;
            }
            if (!group) return false;
            event?.preventDefault();
            event?.stopImmediatePropagation();
            updateRecommendationGroup(group, page, true);
            showToast(page === 1 ? "Showing exercises 1–3" : "Showing exercises 4–6");
            scrollToLatest(80);
            return true;
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
                    padding: 20px 23px !important;
                    background: linear-gradient(180deg, #fbfdf7 0%, #f5f9ec 100%) !important;
                    border-top: 1px solid #dfe7d4;
                    border-radius: 0 !important;
                    color: #151a12 !important;
                    font-family: "DM Sans", system-ui, sans-serif !important;
                  }
                  #dfAccordionWrapper #title {
                    color: #151a12 !important;
                    font-size: 19px !important;
                    font-weight: 800 !important;
                    letter-spacing: -.01em !important;
                  }
                  #dfAccordionWrapper #subtitle {
                    margin-top: 4px !important;
                    color: #66705f !important;
                    font-size: 16px !important;
                  }
                  #dfAccordionWrapper #expandIcon {
                    color: #6f930d !important;
                    filter: drop-shadow(0 2px 3px rgba(111, 147, 13, .18));
                  }
                  #dfAccordionWrapper #text {
                    margin-top: 14px !important;
                    padding: 15px 18px !important;
                    border: 1px solid #d6dfca !important;
                    border-left: 4px solid #b8f22e !important;
                    border-radius: 12px !important;
                    background: rgba(255, 255, 255, .92) !important;
                    box-shadow: 0 6px 18px rgba(25, 31, 18, .06) !important;
                    color: #34402f !important;
                    font-size: 17px !important;
                    font-weight: 600 !important;
                    line-height: 1.85 !important;
                    white-space: pre-line !important;
                  }
                `);
              }
              if (nestedRoot.host?.localName === "df-button") {
                nestedRoot.host.style.setProperty("display", "block", "important");
                nestedRoot.host.style.setProperty("margin", "0 22px 20px", "important");
                ensureShadowStyle(nestedRoot, "fitbox-detail-button-theme", `
                  button, #button, .button {
                    width: 100% !important;
                    min-height: 48px !important;
                    padding: 12px 18px !important;
                    border: 1px solid #91bd1c !important;
                    border-radius: 11px !important;
                    background: #b8f22e !important;
                    color: #151a12 !important;
                    box-shadow: 0 5px 14px rgba(111, 147, 13, .16) !important;
                    font: 800 16px/1.2 "DM Sans", system-ui, sans-serif !important;
                    cursor: pointer !important;
                    transition: transform .16s ease, background .16s ease, box-shadow .16s ease !important;
                  }
                  button:hover, #button:hover, .button:hover {
                    background: #c8ff45 !important;
                    box-shadow: 0 7px 18px rgba(111, 147, 13, .22) !important;
                    transform: translateY(-1px);
                  }
                  button:focus-visible, #button:focus-visible, .button:focus-visible {
                    outline: 3px solid rgba(111, 147, 13, .34) !important;
                    outline-offset: 2px !important;
                  }
                  button:disabled, #button:disabled, .button:disabled {
                    opacity: .55 !important;
                    cursor: wait !important;
                    transform: none !important;
                  }
                `);
              }
              if (nestedRoot.host?.localName === "df-messenger-user-input") {
                ensureShadowStyle(nestedRoot, "fitbox-input-theme", `
                  input, textarea { font-size: 18px !important; }
                  .input-container { min-height: 66px !important; }
                `);
              }
            });
            discoverRecommendationPagers();
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
              if (list.querySelector(".user-message")) stage.classList.add("conversation-active");
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
          const detailMarker = "#fitbox-view-details=";
          function sendDetailsFromMarker(link, event) {
            link = String(link || "");
            const marker = detailMarker;
            const markerIndex = link.indexOf(marker);
            if (markerIndex < 0) return false;
            event?.preventDefault();
            event?.stopImmediatePropagation();
            const encodedTitle = link.slice(markerIndex + marker.length);
            let title = "";
            try { title = decodeURIComponent(encodedTitle).trim(); }
            catch (_error) { return false; }
            if (!title) return false;
            return sendPrompt(`Tell me about ${title}`);
          }
          document.addEventListener("click", (event) => {
            const markerNode = event.composedPath().find((node) => {
              if (!node || typeof node.getAttribute !== "function") return false;
              const link = String(node.getAttribute("href") || node.getAttribute("link") || "");
              return link.includes(detailMarker) || link.includes(recommendationPageMarker);
            });
            if (!markerNode) return;
            const link = markerNode.getAttribute("href") || markerNode.getAttribute("link");
            if (String(link).includes(recommendationPageMarker)) {
              const page = Number(String(link).split(recommendationPageMarker)[1] || "1");
              setRecommendationPage(page === 2 ? 2 : 1, event);
            } else sendDetailsFromMarker(link, event);
          }, true);
          messenger.addEventListener("df-button-clicked", (event) => {
            const element = event.detail?.element || event.detail || {};
            const link = String(element.link || "");
            if (link.includes(recommendationPageMarker)) {
              const page = Number(link.split(recommendationPageMarker)[1] || "1");
              setRecommendationPage(page === 2 ? 2 : 1, event);
            } else sendDetailsFromMarker(link, event);
          });
          clearChatButton.addEventListener("click", () => {
            clearChatButton.disabled = true;
            clearChatButton.querySelector(".clear-label").textContent = "Clearing…";
            window.parent.location.reload();
          });
          messenger.addEventListener("df-user-input-entered", () => {
            stage.classList.add("conversation-active");
            scrollToLatest(80);
          });
          messenger.addEventListener("df-response-received", () => scrollToLatest(220));
          window.addEventListener("resize", fitChatToPanel);
          new ResizeObserver(fitChatToPanel).observe(stage);
        </script>
      </body>
    </html>
    """
).replace("__AGENT_ID__", AGENT_ID)

components.html(page, height=900, scrolling=False)
