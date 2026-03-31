# ✈️ AI Travel Concierge
### AI Agent | Track A | 8-Week Internship Project

## 🚀 Live Demo
👉 **[Click here to try the app](https://ai-tavel-concierge.streamlit.app/)**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
---


## 🌍 Project Overview

An intelligent AI-powered Travel Concierge built with LangChain and Google Gemini.
The agent can plan trips, search flights, recommend hotels, check weather,
convert currencies, and generate detailed day-by-day itineraries.

---

## 🏗️ Architecture

```
User Query
    ↓
Gradio UI (Chat / Trip Planner)
    ↓
LangChain ReAct Agent (Gemini 1.5 Flash)
    ↓
Tool Selector → [ Weather | Currency | Flights | Hotels | Itinerary | Budget ]
    ↓
API Calls (Weatherstack / ExchangeRate / SERP)
    ↓
SQLite Database (Save searches & itineraries)
    ↓
Response to User
```

---

## 🛠️ Tools & APIs

| Tool | API | Purpose |
|------|-----|---------|
| `get_weather` | Weatherstack API | Real-time weather for any city |
| `convert_currency` | ExchangeRate-API | Live currency conversion |
| `search_flights` | SERP API | Flight route search |
| `search_hotels` | SERP API | Hotel recommendations |
| `search_travel_info` | SERP API | General travel web search |
| `generate_itinerary` | Gemini LLM | Day-by-day trip planning |
| `estimate_budget` | Built-in DB | Trip cost estimation |

---

## 📦 Tech Stack

- **LLM**: Google Gemini 1.5 Flash (free tier)
- **Agent Framework**: LangChain (ReAct agent)
- **Database**: SQLite
- **UI**: Gradio
- **Platform**: Google Colab
- **Language**: Python 3.10+

---

## 🔑 Required API Keys

Get these free API keys before running:

1. **Google Gemini** → https://aistudio.google.com/app/apikey
2. **SERP API** → https://serpapi.com (100 free searches/month)
3. **Weatherstack** → https://weatherstack.com (1000 free calls/month)
4. **ExchangeRate-API** → https://www.exchangerate-api.com (1500 free calls/month)
5. **Groq** (optional) → https://console.groq.com

---

## 🚀 How to Run

### Google Colab (Recommended)

1. Open the notebook in Google Colab
2. Click the 🔑 **Secrets** icon in the left sidebar
3. Add all 5 API keys as secrets
4. Run cells from top to bottom (Shift+Enter)
5. Click the Gradio public link to use the app

### Notebooks in Order:
```
📓 Week1_2  → Foundation & RAG chatbot
📓 Week3_4  → Agent + API tools
📓 Week5_6  → Itinerary, Budget & Database
📓 Week7_8  → Final app, testing & polish
```

---

## 📅 Development Timeline

| Week | Milestone | Status |
|------|-----------|--------|
| 1-2 | Foundation: RAG chatbot + Gradio UI | ✅ |
| 3-4 | Agent + 5 API tools | ✅ |
| 5-6 | Itinerary generator + SQLite DB | ✅ |
| 7-8 | Testing, polish, final demo | ✅ |

---

## 💬 Example Conversations

```
User: Plan a 5-day Bali trip for 2 people with mid-range budget
Bot:  [Generates complete day-by-day itinerary with activities, food & tips]

User: What's the weather in Tokyo right now?
Bot:  🌍 Tokyo: 18°C, Clear, Humidity: 65%, Wind: 12km/h

User: Convert 1000 USD to Japanese Yen
Bot:  💱 1,000 USD = 149,500 JPY (Rate: 149.50)

User: How much will a 7-day Paris trip cost?
Bot:  💰 Budget: $1,120/person | Mid-range: $2,240 | Luxury: $5,600
```

---

## 🎯 Assessment Criteria (Track A)

| Criteria | Points | Status |
|----------|--------|--------|
| Core Functionality (Agent + 2+ tools + DB) | 40 | ✅ |
| User Interface (Clean Gradio app) | 20 | ✅ |
| Deployment (Working app link) | 15 | ✅ |
| Documentation (README + setup) | 15 | ✅ |
| Presentation (Demo video) | 10 | 🎬 Record! |
| **Total** | **100** | |

---


## 🗂️ Project Structure
```
ai-travel-concierge/
│
├── app.py              # Main Streamlit app (UI)
├── agent.py            # LangChain agent (brain)
├── tools.py            # API tools (weather, flights, hotels)
├── rag_pipeline.py     # RAG knowledge base
├── database.py         # SQLite database
│
├── notebooks/
│   ├── Week1_8.ipynb
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 👨‍💻 Author

- **Project**: AI Travel Concierge
- **Track**: Track A (Essential)
- **Duration**: 8 Weeks
- **Platform**: Google Colab

---

*Built with  using LangChain + Google Gemini*

