"""FitBox Streamlit front end for the existing Dialogflow ES agent.

The page keeps Dialogflow as the single chatbot engine, so the Welcome Intent,
gym information intents, workout intents, and the PythonAnywhere dataset webhook
all remain available from one public Streamlit page.
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
      [data-testid="stAppViewContainer"] {
        background: #eef1e8;
      }
      [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding: 1.1rem 1rem 1rem;
      }
      iframe[title="st.iframe"] {
        border-radius: 26px;
        box-shadow: 0 24px 70px rgba(25, 31, 18, .13);
      }
      @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding: .35rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

page = dedent(
    f"""
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
          :root {{
            --ink: #151a12;
            --muted: #687064;
            --lime: #b8f22e;
            --lime-dark: #6f930d;
            --paper: #fbfcf7;
            --line: #dfe4d8;
          }}
          * {{ box-sizing: border-box; }}
          html, body {{
            margin: 0;
            min-height: 100%;
            overflow: hidden;
            background: #eef1e8;
            color: var(--ink);
            font-family: "DM Sans", system-ui, sans-serif;
          }}
          .shell {{
            height: 640px;
            display: grid;
            grid-template-rows: auto auto minmax(0, 1fr);
            overflow: hidden;
            background: var(--paper);
            border: 1px solid rgba(21, 26, 18, .08);
            border-radius: 26px;
          }}
          .topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            padding: 18px 24px;
            background: #171b14;
            color: white;
          }}
          .brand {{ display: flex; align-items: center; gap: 13px; }}
          .mark {{
            width: 44px;
            height: 44px;
            display: grid;
            place-items: center;
            border-radius: 13px;
            background: var(--lime);
            color: #11150e;
            font: 800 14px/1 "Manrope", sans-serif;
            letter-spacing: -.02em;
          }}
          h1 {{ margin: 0; font: 800 19px/1.2 "Manrope", sans-serif; }}
          .subtitle {{ margin-top: 3px; color: #b9c0b4; font-size: 12px; }}
          .status {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #dce3d7;
            font-size: 12px;
          }}
          .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--lime); box-shadow: 0 0 0 4px rgba(184,242,46,.12); }}
          .guide {{
            padding: 15px 20px 13px;
            border-bottom: 1px solid var(--line);
            background: linear-gradient(105deg, #f8faef 0%, #fbfcf7 60%);
          }}
          .guide-row {{ display: flex; align-items: center; justify-content: space-between; gap: 14px; }}
          .guide-copy strong {{ display: block; font-size: 14px; }}
          .guide-copy span {{ display: block; margin-top: 3px; color: var(--muted); font-size: 12px; }}
          .chips {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
          .chip {{
            appearance: none;
            border: 1px solid #cfd6c7;
            border-radius: 999px;
            padding: 8px 11px;
            background: white;
            color: #333a2f;
            font: 600 11px/1.2 "DM Sans", sans-serif;
            cursor: pointer;
            transition: .16s ease;
          }}
          .chip:hover, .chip:focus-visible {{
            border-color: #9dc91f;
            background: #f3fadf;
            transform: translateY(-1px);
            outline: none;
          }}
          .chat-stage {{
            position: relative;
            min-height: 0;
            overflow: hidden;
            background:
              radial-gradient(circle at 15% 10%, rgba(184,242,46,.09), transparent 27%),
              #f4f6ef;
          }}
          .loading {{
            position: absolute;
            inset: 0;
            display: grid;
            place-items: center;
            color: var(--muted);
            font-size: 13px;
          }}
          df-messenger {{
            --df-messenger-bot-message: #ffffff;
            --df-messenger-button-titlebar-color: #171b14;
            --df-messenger-button-titlebar-font-color: #ffffff;
            --df-messenger-chat-background-color: #f4f6ef;
            --df-messenger-font-color: #1f251b;
            --df-messenger-input-box-color: #ffffff;
            --df-messenger-input-font-color: #151a12;
            --df-messenger-input-placeholder-font-color: #788071;
            --df-messenger-minimized-chat-close-icon-color: #ffffff;
            --df-messenger-send-icon: #6f930d;
            --df-messenger-user-message: #171b14;
            z-index: 2;
          }}
          .toast {{
            position: absolute;
            left: 50%;
            bottom: 16px;
            z-index: 5;
            transform: translate(-50%, 12px);
            opacity: 0;
            pointer-events: none;
            padding: 9px 13px;
            border-radius: 10px;
            background: #171b14;
            color: white;
            font-size: 12px;
            transition: .2s ease;
          }}
          .toast.show {{ opacity: 1; transform: translate(-50%, 0); }}
          @media (max-width: 760px) {{
            .shell {{ height: 640px; border-radius: 18px; }}
            .topbar {{ padding: 15px; }}
            .status {{ display: none; }}
            .guide {{ padding: 12px; }}
            .guide-row {{ align-items: flex-start; flex-direction: column; }}
            .chips {{ justify-content: flex-start; }}
            .chip {{ padding: 7px 9px; }}
          }}
        </style>
      </head>
      <body>
        <main class="shell">
          <header class="topbar">
            <div class="brand">
              <div class="mark">FB</div>
              <div>
                <h1>FitBox AI Assistant</h1>
                <div class="subtitle">Gym guidance and personalised exercise discovery</div>
              </div>
            </div>
            <div class="status"><span class="dot"></span> Dialogflow ES online</div>
          </header>

          <section class="guide" aria-label="Suggested questions">
            <div class="guide-row">
              <div class="guide-copy">
                <strong>Not sure what to ask?</strong>
                <span>Choose a suggestion, then press Enter in the chat box.</span>
              </div>
              <div class="chips">
                <button class="chip" data-prompt="How do I get started?">How do I get started?</button>
                <button class="chip" data-prompt="What can FitBox help me with?">What can FitBox help with?</button>
                <button class="chip" data-prompt="Give me beginner chest exercises">Beginner chest exercises</button>
                <button class="chip" data-prompt="Show me exercises using dumbbells">Dumbbell exercises</button>
              </div>
            </div>
          </section>

          <section class="chat-stage" id="chat-stage">
            <div class="loading" id="loading">Loading FitBox assistant…</div>
            <df-messenger
              intent="WELCOME"
              chat-title="FitBox Assistant"
              agent-id="{AGENT_ID}"
              language-code="en"
              expand>
            </df-messenger>
            <div class="toast" id="toast">Suggestion added — press Enter to send</div>
          </section>
        </main>

        <script>
          const messenger = document.querySelector("df-messenger");
          const stage = document.getElementById("chat-stage");
          const loading = document.getElementById("loading");
          const toast = document.getElementById("toast");

          function findChat() {{
            return messenger.shadowRoot?.querySelector("df-messenger-chat");
          }}

          function findInput() {{
            const chat = findChat();
            const userInput = chat?.shadowRoot?.querySelector("df-messenger-user-input");
            return userInput?.shadowRoot?.querySelector('input[aria-label="Talk to Agent"], input');
          }}

          function fitChatToPanel() {{
            const root = messenger.shadowRoot;
            const chat = findChat();
            const panel = chat?.shadowRoot?.querySelector(".chat-wrapper");
            if (!root || !chat || !panel) return false;

            const openButton = root.querySelector("#widgetIcon");
            if (openButton?.getAttribute("aria-expanded") !== "true" &&
                messenger.dataset.autoOpened !== "true") {{
              messenger.dataset.autoOpened = "true";
              openButton.click();
              return false;
            }}

            messenger.style.setProperty("position", "absolute", "important");
            messenger.style.setProperty("inset", "0", "important");
            messenger.style.setProperty("width", "100%", "important");
            messenger.style.setProperty("height", "100%", "important");

            chat.style.setProperty("position", "absolute", "important");
            chat.style.setProperty("inset", "12px", "important");
            chat.style.setProperty("width", "auto", "important");
            chat.style.setProperty("height", "auto", "important");
            chat.style.setProperty("max-height", "none", "important");
            chat.style.setProperty("border-radius", "18px", "important");
            chat.style.setProperty("overflow", "hidden", "important");
            chat.style.setProperty("box-shadow", "0 12px 32px rgba(25,31,18,.10)", "important");

            panel.classList.remove("chat-min");
            const stageRect = stage.getBoundingClientRect();
            panel.style.setProperty("position", "fixed", "important");
            panel.style.setProperty("inset", "auto", "important");
            panel.style.setProperty("top", `${{stageRect.top + 12}}px`, "important");
            panel.style.setProperty("left", `${{stageRect.left + 12}}px`, "important");
            panel.style.setProperty("right", `${{innerWidth - stageRect.right + 12}}px`, "important");
            panel.style.setProperty("bottom", `${{innerHeight - stageRect.bottom + 12}}px`, "important");
            panel.style.setProperty("width", "auto", "important");
            panel.style.setProperty("min-width", "0", "important");
            panel.style.setProperty("max-width", "none", "important");
            panel.style.setProperty("height", "auto", "important");
            panel.style.setProperty("min-height", "0", "important");
            panel.style.setProperty("max-height", "none", "important");
            panel.style.setProperty("border-radius", "18px", "important");
            panel.style.setProperty("overflow", "hidden", "important");
            panel.style.setProperty("box-shadow", "0 12px 32px rgba(25,31,18,.10)", "important");

            root.querySelectorAll("df-messenger-chat-bubble").forEach((node) => {{
              node.style.setProperty("display", "none", "important");
            }});
            loading.style.display = "none";
            return true;
          }}

          function setPrompt(value) {{
            const input = findInput();
            if (!input) {{
              toast.textContent = "Chat is still loading — try again in a moment";
              toast.classList.add("show");
              setTimeout(() => toast.classList.remove("show"), 1800);
              return;
            }}
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
            if (setter) setter.call(input, value);
            else input.value = value;
            input.dispatchEvent(new InputEvent("input", {{
              bubbles: true,
              composed: true,
              data: value,
              inputType: "insertText"
            }}));
            input.dispatchEvent(new Event("change", {{ bubbles: true, composed: true }}));
            input.focus();
            toast.textContent = "Suggestion added — press Enter to send";
            toast.classList.add("show");
            setTimeout(() => toast.classList.remove("show"), 1800);
          }}

          document.querySelectorAll(".chip").forEach((button) => {{
            button.addEventListener("click", () => setPrompt(button.dataset.prompt));
          }});

          let attempts = 0;
          const timer = setInterval(() => {{
            attempts += 1;
            fitChatToPanel();
            if (attempts > 80) clearInterval(timer);
          }}, 125);
          window.addEventListener("dfMessengerLoaded", fitChatToPanel);
          new ResizeObserver(fitChatToPanel).observe(stage);
        </script>
      </body>
    </html>
    """
)

components.html(page, height=660, scrolling=False)
