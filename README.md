# FitBox Streamlit Assistant

FitBox is a gym chatbot interface built with **Streamlit** and connected to an existing **Dialogflow ES** agent.

## What this version fixes

- Opens directly as a chat interface.
- Uses the Dialogflow ES Welcome Intent, so messages such as `hi` keep the original welcome response.
- Keeps all existing Dialogflow intents: gym information, facilities, membership, classes, equipment, safety, exercises and workout recommendations.
- Keeps the existing Python webhook and MegaGym dataset workflow for exercise results.
- Provides suggested questions for first-time users. A suggestion fills the chat input and the user presses Enter to send it.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Sign in at <https://share.streamlit.io/> with GitHub.
2. Select **Create app**.
3. Choose repository `Weilun1210/fitbox-streamlit-assistant`.
4. Select branch `main` and main file `app.py`.
5. Select **Deploy**.

No API key is stored in this repository. The interface uses the enabled Dialogflow Messenger integration for the FitBox agent.

