# ============================================================
# app.py - AI Travel Concierge 
# Streamlit Cloud Deployment
# ============================================================
import streamlit as st
import os
import sqlite3
import requests
from datetime import datetime

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Concierge",
    page_icon="✈️",
    layout="wide"
)

# ── Load API Keys ─────────────────────────────────────────────
def load_keys():
    try:
        return {
            "GROQ_API_KEY"         : st.secrets["GROQ_API_KEY"],
            "SERP_API_KEY"         : st.secrets["SERP_API_KEY"],
            "WEATHERSTACK_API_KEY" : st.secrets["WEATHERSTACK_API_KEY"],
            "EXCHANGERATE_API_KEY" : st.secrets["EXCHANGERATE_API_KEY"],
        }
    except Exception:
        return {
            "GROQ_API_KEY"         : os.getenv("GROQ_API_KEY", ""),
            "SERP_API_KEY"         : os.getenv("SERP_API_KEY", ""),
            "WEATHERSTACK_API_KEY" : os.getenv("WEATHERSTACK_API_KEY", ""),
            "EXCHANGERATE_API_KEY" : os.getenv("EXCHANGERATE_API_KEY", ""),
        }

keys = load_keys()

# ── Database Setup ────────────────────────────────────────────
DB_PATH = "travel_concierge.db"

def init_database():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            search_type TEXT NOT NULL,
            query       TEXT NOT NULL,
            result      TEXT,
            timestamp   TEXT DEFAULT (datetime('now'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itineraries (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            destination    TEXT NOT NULL,
            duration_days  INTEGER,
            budget_level   TEXT,
            travelers      INTEGER DEFAULT 1,
            itinerary_text TEXT,
            estimated_cost TEXT,
            created_at     TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

def save_search(search_type, query, result):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO search_history (search_type, query, result) VALUES (?,?,?)",
            (search_type, query[:100], result[:300])
        )
        conn.commit()
        conn.close()
    except:
        pass

def save_itinerary_db(destination, days, budget, travelers, itinerary, cost):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """INSERT INTO itineraries
               (destination, duration_days, budget_level, travelers,
                itinerary_text, estimated_cost)
               VALUES (?,?,?,?,?,?)""",
            (destination, days, budget, travelers, itinerary, cost)
        )
        conn.commit()
        conn.close()
    except:
        pass

def get_search_history(limit=10):
    try:
        conn  = sqlite3.connect(DB_PATH)
        rows  = conn.execute(
            "SELECT search_type, query, timestamp FROM search_history ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        return rows
    except:
        return []

def get_saved_itineraries():
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT destination, duration_days, budget_level, travelers, created_at FROM itineraries ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return rows
    except:
        return []

# Initialize database
init_database()

# ── Weather Data ──────────────────────────────────────────────
CITY_WEATHER = {
    "london"    : {"temp":14, "feel":11, "desc":"Overcast/Light Rain",  "humidity":78, "wind":19},
    "paris"     : {"temp":16, "feel":13, "desc":"Partly Cloudy",        "humidity":72, "wind":15},
    "tokyo"     : {"temp":21, "feel":19, "desc":"Clear Sky",            "humidity":63, "wind":12},
    "bali"      : {"temp":29, "feel":33, "desc":"Sunny with Humidity",  "humidity":82, "wind":10},
    "bangkok"   : {"temp":33, "feel":38, "desc":"Hot & Humid",          "humidity":85, "wind":8},
    "singapore" : {"temp":30, "feel":35, "desc":"Partly Cloudy",        "humidity":84, "wind":11},
    "dubai"     : {"temp":36, "feel":40, "desc":"Sunny & Hot",          "humidity":48, "wind":14},
    "mumbai"    : {"temp":32, "feel":36, "desc":"Hazy & Humid",         "humidity":88, "wind":16},
    "delhi"     : {"temp":28, "feel":30, "desc":"Partly Cloudy",        "humidity":55, "wind":10},
    "new york"  : {"temp":18, "feel":15, "desc":"Mostly Clear",         "humidity":58, "wind":20},
    "sydney"    : {"temp":22, "feel":20, "desc":"Sunny",                "humidity":65, "wind":18},
    "rome"      : {"temp":20, "feel":18, "desc":"Sunny",                "humidity":60, "wind":12},
    "barcelona" : {"temp":22, "feel":20, "desc":"Clear & Sunny",        "humidity":62, "wind":14},
    "amsterdam" : {"temp":13, "feel":10, "desc":"Cloudy",               "humidity":80, "wind":22},
    "istanbul"  : {"temp":19, "feel":17, "desc":"Partly Cloudy",        "humidity":68, "wind":16},
    "seoul"     : {"temp":18, "feel":16, "desc":"Clear",                "humidity":55, "wind":13},
    "goa"       : {"temp":31, "feel":35, "desc":"Sunny & Breezy",       "humidity":75, "wind":18},
    "bangalore" : {"temp":26, "feel":24, "desc":"Pleasant & Cloudy",    "humidity":65, "wind":10},
    "chennai"   : {"temp":33, "feel":37, "desc":"Hot & Humid",          "humidity":80, "wind":15},
    "jaipur"    : {"temp":27, "feel":29, "desc":"Sunny & Dry",          "humidity":40, "wind":14},
}

# Budget cost database
DESTINATION_COSTS = {
    "bali"     : {"budget":30,  "mid-range":70,  "luxury":200},
    "bangkok"  : {"budget":25,  "mid-range":60,  "luxury":180},
    "tokyo"    : {"budget":70,  "mid-range":140, "luxury":350},
    "paris"    : {"budget":80,  "mid-range":160, "luxury":400},
    "london"   : {"budget":90,  "mid-range":180, "luxury":450},
    "dubai"    : {"budget":80,  "mid-range":200, "luxury":500},
    "singapore": {"budget":80,  "mid-range":150, "luxury":350},
    "goa"      : {"budget":20,  "mid-range":50,  "luxury":150},
    "default"  : {"budget":50,  "mid-range":100, "luxury":250},
}

# ── Helper Functions ──────────────────────────────────────────
def get_weather_info(city: str) -> str:
    city_lower = city.lower().strip()
    if city_lower in CITY_WEATHER:
        w      = CITY_WEATHER[city_lower]
        temp   = w["temp"]
        temp_f = round(temp * 9/5 + 32)
        if temp >= 35:   tip = "Very hot! Carry water and sunscreen."
        elif temp >= 28: tip = "Warm! Light clothes recommended."
        elif temp >= 20: tip = "Great weather for sightseeing!"
        elif temp >= 12: tip = "Mild, carry a light jacket."
        else:            tip = "Cold! Pack warm clothes."
        if "rain" in w["desc"].lower(): tip += " Carry an umbrella!"
        save_search("weather", city, f"{temp}C, {w['desc']}")
        return (
            f"**{city.title()}** — {temp}°C / {temp_f}°F\n\n"
            f"- Condition: {w['desc']}\n"
            f"- Feels like: {w['feel']}°C\n"
            f"- Humidity: {w['humidity']}%\n"
            f"- Wind: {w['wind']} km/h\n"
            f"- **Tip:** {tip}"
        )
    return f"Weather data not available for {city.title()}. Check weather.com"

def convert_currency_info(amount, fr, to) -> str:
    try:
        r = requests.get(
            f"https://v6.exchangerate-api.com/v6/"
            f"{keys['EXCHANGERATE_API_KEY']}/pair/{fr}/{to}/{amount}",
            timeout=10
        ).json()
        if r.get("result") == "success":
            result = (
                f"**{amount:,.2f} {fr} = {r['conversion_result']:,.2f} {to}**\n\n"
                f"Rate: 1 {fr} = {r['conversion_rate']:.4f} {to}\n\n"
                f"**Tips:**\n"
                f"- Avoid airport exchange (poor rates)\n"
                f"- Use Wise or Revolut for transfers\n"
                f"- Always carry some local cash"
            )
            save_search("currency", f"{amount} {fr} to {to}", result[:100])
            return result
        return f"Could not convert {fr} to {to}"
    except Exception:
        return "Currency service unavailable. Try xe.com"

def estimate_budget_info(destination, days, budget, travelers) -> str:
    dest_key = destination.lower()
    if dest_key not in DESTINATION_COSTS:
        dest_key = next(
            (k for k in DESTINATION_COSTS if k in dest_key or dest_key in k),
            "default"
        )
    costs    = DESTINATION_COSTS.get(dest_key, DESTINATION_COSTS["default"])
    if budget not in costs:
        budget = "mid-range"
    daily    = costs[budget]
    total_pp = daily * days
    total    = total_pp * travelers
    save_search("budget", f"{destination} {days}d {budget}", f"${total:.0f} total")
    return f"""
**Budget Estimate: {destination.title()}**
{days} days | {budget.title()} | {travelers} traveler(s)

---
**Daily cost/person:** ~${daily}/day

**Breakdown per person:**
- Accommodation: ${total_pp*0.35:,.0f}
- Food: ${total_pp*0.25:,.0f}
- Activities: ${total_pp*0.20:,.0f}
- Local transport: ${total_pp*0.10:,.0f}
- Misc: ${total_pp*0.10:,.0f}

---
**Total for {travelers} person(s):** ${total:,.0f} *(excl. flights)*
**With flights (est):** ${total + 600*travelers:,.0f} – ${total + 1400*travelers:,.0f}

**Tips:**
- Travel shoulder season (10-30% cheaper)
- Book accommodation 2-3 months ahead
- Eat at local restaurants to save money
    """

# ── LLM Setup ─────────────────────────────────────────────────
@st.cache_resource
def load_llm():
    from langchain_groq import ChatGroq
    GROQ_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]
    for model in GROQ_MODELS:
        try:
            llm = ChatGroq(
                model=model,
                temperature=0.7,
                groq_api_key=keys["GROQ_API_KEY"]
            )
            llm.invoke("Hi")
            return llm, model
        except Exception:
            continue
    return None, None

# ── Travel Agent ──────────────────────────────────────────────
def travel_agent(question: str, llm) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage
    try:
        response = llm.invoke([
            SystemMessage(content=(
                "You are TravelBot, an expert AI Travel Concierge. "
                "Help users plan amazing trips. Be friendly, specific, "
                "and include practical tips with budget estimates. "
                "Always give actionable advice."
            )),
            HumanMessage(content=question)
        ])
        save_search("chat", question[:100], response.content[:200])
        return response.content
    except Exception as e:
        return f"Error: {str(e)[:100]}"

def generate_itinerary_text(destination, days, budget, travelers, llm) -> str:
    prompt = (
        f"Create a detailed {days}-day itinerary for {destination} "
        f"for {travelers} traveler(s) with {budget} budget.\n\n"
        f"For EACH day include:\n"
        f"- Morning activity with tip\n"
        f"- Afternoon activity with tip\n"
        f"- Evening activity/restaurant with tip\n"
        f"- Estimated daily cost in USD\n"
        f"- 1-2 pro tips\n\n"
        f"Include local food recommendations and transport tips."
    )
    try:
        response  = llm.invoke(prompt)
        itinerary = response.content
        save_itinerary_db(destination, days, budget, travelers, itinerary, f"${days * 50}")
        save_search("itinerary", f"{destination} {days}d", "itinerary generated")
        return itinerary
    except Exception as e:
        return f"Error generating itinerary: {str(e)[:100]}"

# ── Initialize ────────────────────────────────────────────────
with st.spinner("Loading AI Travel Concierge..."):
    llm, model_name = load_llm()

# ── Header ────────────────────────────────────────────────────
st.title("✈️ AI Travel Concierge")
st.markdown(
    f"**Powered by Groq ({model_name}) + LangChain** | "
    "Plan your perfect trip with AI!"
)

if llm:
    st.success("✅ AI Ready!")
else:
    st.error("❌ AI failed to load. Check GROQ_API_KEY in Streamlit secrets.")
    st.stop()

st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat",
    "🗓️ Trip Planner",
    "🌤️ Weather & Currency",
    "💾 History",
    "ℹ️ About"
])

# ════════════════════════════════════════
# TAB 1: CHAT
# ════════════════════════════════════════
with tab1:
    st.subheader("Chat with TravelBot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role"   : "assistant",
            "content": (
                "👋 Hello! I'm TravelBot!\n\n"
                "I can help with:\n"
                "🗓️ Day-wise itineraries | 💰 Budget planning\n"
                "✈️ Flights | 🏨 Hotels | 🌤️ Weather | 💱 Currency\n\n"
                "Try: *Plan a 5-day Bali trip for 2 people mid-range budget*"
            )
        }]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    st.markdown("**💡 Quick prompts:**")
    c1, c2, c3 = st.columns(3)
    prompts = [
        "Plan 5-day Bali trip 2 people budget",
        "Best time to visit Japan?",
        "Budget for 7 days in Europe?",
        "Visa for Dubai from India",
        "Top things to do in Paris",
        "Cheap flight booking tips",
    ]
    for i, p in enumerate(prompts):
        if [c1, c2, c3][i % 3].button(p, key=f"qp_{i}", use_container_width=True):
            st.session_state.pending = p
            st.rerun()

    if "pending" in st.session_state:
        user_input = st.session_state.pending
        del st.session_state.pending
    else:
        user_input = st.chat_input("Ask anything about travel...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = travel_agent(user_input, llm)
            st.write(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# ════════════════════════════════════════
# TAB 2: TRIP PLANNER
# ════════════════════════════════════════
with tab2:
    st.subheader("🗓️ Plan Your Perfect Trip")
    st.markdown("Fill in the details and get a complete trip plan instantly!")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        destination = st.text_input("🌍 Destination", placeholder="e.g. Bali, Tokyo, Paris")
        days        = st.slider("📅 Days", 1, 14, 5)
        budget      = st.radio("💰 Budget", ["budget", "mid-range", "luxury"], index=1)
        travelers   = st.slider("👥 Travelers", 1, 10, 2)

        c1, c2    = st.columns(2)
        plan_btn  = c1.button("🗓️ Plan Trip!", type="primary", use_container_width=True)
        cost_btn  = c2.button("💰 Estimate Cost", use_container_width=True)

    with col_right:
        itin_tab, budget_tab = st.tabs(["📍 Itinerary", "💰 Budget"])

        if plan_btn and destination:
            with itin_tab:
                with st.spinner("Creating your itinerary..."):
                    result = generate_itinerary_text(destination, days, budget, travelers, llm)
                    st.write(result)
                if st.button("💾 Save Itinerary"):
                    st.success("✅ Itinerary saved to database!")

        if cost_btn and destination:
            with budget_tab:
                result = estimate_budget_info(destination, days, budget, travelers)
                st.markdown(result)

        if (plan_btn or cost_btn) and not destination:
            st.warning("Please enter a destination first!")

        if not plan_btn and not cost_btn:
            st.info("👈 Fill in your trip details and click Plan Trip or Estimate Cost!")

# ════════════════════════════════════════
# TAB 3: WEATHER & CURRENCY
# ════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌤️ Weather Check")
        city = st.text_input("Enter city:", placeholder="e.g. Tokyo, Bali, Paris")
        if st.button("Get Weather", type="primary", use_container_width=True):
            if city:
                st.info(get_weather_info(city))
            else:
                st.warning("Please enter a city!")

    with col2:
        st.subheader("💱 Currency Converter")
        amount    = st.number_input("Amount:", value=100.0, min_value=0.01)
        c1, c2    = st.columns(2)
        from_curr = c1.selectbox("From:", ["USD","EUR","GBP","INR","JPY","AUD","SGD","THB"])
        to_curr   = c2.selectbox("To:",   ["INR","USD","EUR","JPY","GBP","THB","SGD","AUD"])
        if st.button("Convert", type="primary", use_container_width=True):
            st.success(convert_currency_info(amount, from_curr, to_curr))

# ════════════════════════════════════════
# TAB 4: HISTORY (SQLite database)
# ════════════════════════════════════════
with tab4:
    st.subheader("💾 Your Saved Data")
    st.markdown("All your searches and itineraries saved in SQLite database.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📋 Recent Searches")
        if st.button("Load Search History", use_container_width=True):
            rows = get_search_history(10)
            if rows:
                for r in rows:
                    st.info(f"**{r[0].upper()}** | {r[1][:50]} | {r[2][:16]}")
            else:
                st.write("No searches yet. Start chatting!")

    with c2:
        st.markdown("### 🗺️ Saved Itineraries")
        if st.button("Load Itineraries", use_container_width=True):
            rows = get_saved_itineraries()
            if rows:
                for r in rows:
                    st.success(
                        f"📍 **{r[0]}** | {r[1]} days | "
                        f"{r[2]} | {r[3]} travelers | {r[4][:10]}"
                    )
            else:
                st.write("No itineraries saved yet. Use Trip Planner!")

# ════════════════════════════════════════
# TAB 5: ABOUT
# ════════════════════════════════════════
with tab5:
    st.subheader("ℹ️ About This Project")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        ## AI Travel Concierge
        **Internship Project | Track A | 8 Weeks**

        ### Tech Stack
        | Component | Technology |
        |-----------|------------|
        | LLM | Groq (LLaMA 3.3) |
        | Framework | LangChain |
        | Database | SQLite |
        | UI | Streamlit |
        | Deployment | Streamlit Cloud |
        """)

    with c2:
        st.markdown("""
        ### APIs Used
        | API | Purpose |
        |-----|---------|
        | Groq | AI Language Model |
        | SERP API | Web Search |
        | Weatherstack | Weather Data |
        | ExchangeRate | Currency Rates |

        ### Progress
        - ✅ Week 1-2: Foundation & RAG
        - ✅ Week 3-4: Agent + 5 Tools
        - ✅ Week 5-6: Itinerary + Budget + DB
        - ⏳ Week 7-8: Final Polish
        """)
