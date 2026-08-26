# FitBox AI Assistant

FitBox is a **Streamlit** interface connected to a **Dialogflow ES** agent and a
PythonAnywhere webhook. It helps users discover suitable exercises and view
structured exercise guidance.

## Live project

- Public website: <https://fitboxai.streamlit.app/>
- GitHub repository: <https://github.com/Weilun1210/fitbox-streamlit-assistant>
- Dialogflow ES Agent ID: `8ff14895-4120-431e-b4ef-015ed78ce0cc`
- Tested Streamlit version: `1.61.1`

## Capabilities

FitBox recommends exercises by fitness level, body part, equipment, exercise
type, or combinations of those filters. Exercise records come from
`megaGymDataset.csv`.

## Supported questions

- Exercise recommendations filtered by fitness level, body part, equipment,
  exercise type, or a strict combination of those fields.
- Details for a named exercise, including its description and metadata.
- Welcome, goodbye, and a concise fallback response.
- Native Dialogflow Messenger cards with an expandable instruction section.
- **View details** sends a visible `Tell me about {exercise}` user message,
  stays in the current page, then the assistant answers with the existing
  exercise-details card.

The interface includes a collapsible question guide. It can build a canonical
English question from 17 body parts, 13 equipment values, 3
fitness levels, and 7 exercise types. **Use this question** fills the Dialogflow
input; the user still presses Enter to send it.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The project pins Streamlit `1.61.1` so the tested embedded Messenger layout is
reproducible.

## Deploy on Streamlit Community Cloud

1. Sign in at <https://share.streamlit.io/> with GitHub.
2. Select **Create app** and choose this repository.
3. Select branch `main` and main file `app.py`.
4. Select **Deploy**.

No API key is stored in this repository. Dialogflow Messenger uses the enabled
FitBox integration, while recommendations and exercise details are returned by
the webhook.
