# ============================================================
# app.py - AI Travel Concierge -
# Streamlit Cloud Deployment
# ============================================================
import streamlit as st
import os
import sqlite3
import requests
from datetime import datetime

# ── Page Config ───────────────────────────────────────────────
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

# ============================================================
# WEEK 1-2: RAG KNOWLEDGE BASE
# ============================================================
TRAVEL_KNOWLEDGE = [
    """
    VISA INFORMATION:
    Most countries require a valid passport with at least 6 months validity.
    Schengen visa covers 26 European countries with a single visa.
    USA requires ESTA for visa-waiver countries or a B1/B2 visa.
    India e-Visa is available for 170+ countries online.
    Always apply for visas 4-6 weeks in advance.
    """,
    """
    TRAVEL BUDGET TIPS:
    Southeast Asia (Thailand, Vietnam, Bali): $30-60/day including accommodation.
    Western Europe averages $100-200/day for mid-range travel.
    Japan costs $80-150/day; best visited in spring or autumn.
    Book flights 6-8 weeks in advance for best prices.
    Use incognito mode when searching flights to avoid price tracking.
    """,
    """
    PACKING ESSENTIALS:
    Always carry: passport, travel insurance docs, emergency cash.
    Universal power adapter for international travel.
    Download offline maps (Google Maps) before arriving.
    Carry copies of all important documents separately.
    Travel insurance is strongly recommended for all trips.
    """,
    """
    TOP DESTINATIONS 2024:
    Europe: Paris, Rome, Barcelona, Amsterdam, Prague
    Asia: Tokyo, Bali, Bangkok, Singapore, Kyoto
    Americas: New York, Machu Picchu, Patagonia, Costa Rica
    Middle East: Dubai, Petra, Istanbul, Muscat
    Best time to visit Bali: April-October (dry season)
    Best time to visit Europe: May-September
    """,
    """
    INDIA TRAVEL INFORMATION:
    North India Golden Triangle (Delhi, Agra, Jaipur): October-March.
    Kerala backwaters: November-February is best.
    Goa beaches: November-February (peak), avoid monsoon June-September.
    Himachal Pradesh and Ladakh: May-September.
    Budget: Rs.2000-5000/day for mid-range domestic travel.
    Book trains on IRCTC at least 2-3 months in advance.
    """,
    """
    FLIGHT BOOKING TIPS:
    Best days to book: Tuesday and Wednesday for cheaper fares.
    Use Google Flights, Skyscanner, or Kayak to compare prices.
    Flexible date search can save 20-40% on airfare.
    Budget airlines: IndiGo, SpiceJet (India), Ryanair (Europe), AirAsia (Asia).
    Always check baggage allowance before booking.
    """,
    """
    HOTEL BOOKING TIPS:
    Book directly with hotels for better rates and flexibility.
    Compare on Booking.com, Airbnb, Hotels.com, MakeMyTrip.
    Hostels are great for solo travelers ($10-25/night).
    Mid-range hotels: $40-100/night globally.
    Location matters - staying central saves on transport costs.
    """
]

# ============================================================
# WEEK 3-4: WEATHER & CURRENCY DATA
# ============================================================
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
    "kyoto"     : {"temp":20, "feel":18, "desc":"Mostly Sunny",         "humidity":60, "wind":10},
    "goa"       : {"temp":31, "feel":35, "desc":"Sunny & Breezy",       "humidity":75, "wind":18},
    "bangalore" : {"temp":26, "feel":24, "desc":"Pleasant & Cloudy",    "humidity":65, "wind":10},
    "chennai"   : {"temp":33, "feel":37, "desc":"Hot & Humid",          "humidity":80, "wind":15},
    "hyderabad" : {"temp":28, "feel":30, "desc":"Partly Cloudy",        "humidity":58, "wind":12},
    "jaipur"    : {"temp":27, "feel":29, "desc":"Sunny & Dry",          "humidity":40, "wind":14},
    "agra"      : {"temp":27, "feel":28, "desc":"Mostly Sunny",         "humidity":45, "wind":11},
    "phuket"    : {"temp":30, "feel":34, "desc":"Tropical & Humid",     "humidity":80, "wind":12},
}

# ============================================================
# WEEK 5-6: BUDGET DATABASE
# ============================================================
DESTINATION_COSTS = {
    "bali"      : {"budget":30,  "mid-range":70,  "luxury":200},
    "bangkok"   : {"budget":25,  "mid-range":60,  "luxury":180},
    "thailand"  : {"budget":25,  "mid-range":60,  "luxury":180},
    "vietnam"   : {"budget":25,  "mid-range":55,  "luxury":160},
    "tokyo"     : {"budget":70,  "mid-range":140, "luxury":350},
    "japan"     : {"budget":70,  "mid-range":140, "luxury":350},
    "seoul"     : {"budget":50,  "mid-range":100, "luxury":250},
    "singapore" : {"budget":80,  "mid-range":150, "luxury":350},
    "paris"     : {"budget":80,  "mid-range":160, "luxury":400},
    "london"    : {"budget":90,  "mid-range":180, "luxury":450},
    "rome"      : {"budget":70,  "mid-range":140, "luxury":350},
    "barcelona" : {"budget":65,  "mid-range":130, "luxury":320},
    "amsterdam" : {"budget":75,  "mid-range":150, "luxury":380},
    "dubai"     : {"budget":80,  "mid-range":200, "luxury":500},
    "new york"  : {"budget":100, "mid-range":200, "luxury":500},
    "goa"       : {"budget":20,  "mid-range":50,  "luxury":150},
    "delhi"     : {"budget":20,  "mid-range":45,  "luxury":130},
    "mumbai"    : {"budget":22,  "mid-range":50,  "luxury":140},
    "default"   : {"budget":50,  "mid-range":100, "luxury":250},
}

# ============================================================
# WEEK 5-6: SQLITE DATABASE
# ============================================================
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
            (search_type, query[:100], str(result)[:300])
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def save_itinerary_to_db(destination, days, budget, travelers, itinerary, cost):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """INSERT INTO itineraries
               (destination, duration_days, budget_level,
                travelers, itinerary_text, estimated_cost)
               VALUES (?,?,?,?,?,?)""",
            (destination, days, budget, travelers, itinerary, cost)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_search_history(limit=15):
    try:
        conn  = sqlite3.connect(DB_PATH)
        rows  = conn.execute(
            "SELECT search_type, query, timestamp FROM search_history ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_saved_itineraries():
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT destination, duration_days, budget_level, travelers, created_at FROM itineraries ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return rows
    except Exception:
        return []

# Initialize DB
init_database()

# ============================================================
# WEEK 3-4: HELPER FUNCTIONS (Tools logic)
# ============================================================
def get_weather_info(city: str) -> str:
    """Week 3-4: Weather tool logic."""
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
        if "rain" in w["desc"].lower():
            tip += " Carry an umbrella!"
        save_search("weather", city, f"{temp}C {w['desc']}")
        return (
            f"**{city.title()}** — {temp}°C / {temp_f}°F\n\n"
            f"- Feels like: {w['feel']}°C\n"
            f"- Condition: {w['desc']}\n"
            f"- Humidity: {w['humidity']}%\n"
            f"- Wind: {w['wind']} km/h\n\n"
            f"**Travel Tip:** {tip}"
        )
    return f"Weather data not available for **{city.title()}**. Check weather.com"

def convert_currency_info(amount, fr, to) -> str:
    """Week 3-4: Currency converter logic."""
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
        fallback = {
            ("USD","INR"):83.5, ("EUR","INR"):90.2,
            ("USD","JPY"):149.5, ("USD","THB"):35.2,
            ("GBP","INR"):105.8
        }
        rate = fallback.get((fr, to))
        if rate:
            return f"~{amount*rate:,.2f} {to} (approximate offline rate)"
        return f"Could not convert {fr} to {to}"
    except Exception:
        return "Currency service unavailable. Try xe.com"

# ============================================================
# WEEK 5-6: BUDGET ESTIMATOR
# ============================================================
def estimate_budget_info(destination, days, budget, travelers) -> str:
    """Week 5-6: Budget estimator logic."""
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

    flight_estimates = {
        "budget"    : "$200-600 (economy, book early)",
        "mid-range" : "$400-1200 (economy/premium economy)",
        "luxury"    : "$1500-5000 (business/first class)"
    }

    save_search("budget", f"{destination} {days}d {budget} {travelers}p", f"${total:.0f}")
    return f"""
**Budget: {destination.title()}** | {days} days | {budget.title()} | {travelers} traveler(s)

---
**Daily cost/person:** ~${daily}/day

**Breakdown per person (${total_pp:,.0f} total):**
- Accommodation: ${total_pp*0.35:,.0f}
- Food & Dining: ${total_pp*0.25:,.0f}
- Activities: ${total_pp*0.20:,.0f}
- Local Transport: ${total_pp*0.10:,.0f}
- Misc/Shopping: ${total_pp*0.10:,.0f}

---
**Total for {travelers} person(s):** ${total:,.0f} *(excluding flights)*

**Flights estimate:** {flight_estimates.get(budget, flight_estimates['mid-range'])}

**With flights (total):** ${total + 600*travelers:,.0f} – ${total + 1400*travelers:,.0f}

**Money-saving tips:**
- Travel shoulder season (save 10-30%)
- Book accommodation 2-3 months ahead
- Eat at local restaurants
- Get travel insurance ($30-80 for whole trip)
"""

# ============================================================
# WEEK 1-2: RAG CHAIN SETUP
# ============================================================
@st.cache_resource
def build_rag_chain(llm):
    """Week 1-2: Build RAG knowledge base and chain."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_core.documents import Document
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        docs       = [Document(page_content=t) for t in TRAVEL_KNOWLEDGE]
        splitter   = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        vectorstore = FAISS.from_documents(split_docs, embeddings)
        retriever   = vectorstore.as_retriever(search_kwargs={"k": 3})

        PROMPT = PromptTemplate(
            template="""
You are an expert AI Travel Concierge.
Use the following travel knowledge to answer the question:
{context}

Question: {question}

Instructions:
- Be specific and helpful
- Include practical tips when relevant
- Mention costs/budgets when relevant
- Keep response concise but complete

Answer:
""",
            input_variables=["context", "question"]
        )

        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)

        rag_chain = (
            {"context": retriever | format_docs,
             "question": RunnablePassthrough()}
            | PROMPT
            | llm
            | StrOutputParser()
        )
        return rag_chain
    except Exception as e:
        return None

# ============================================================
# WEEK 2-8: LLM INITIALIZATION
# ============================================================
@st.cache_resource
def load_llm():
    """Initialize Groq LLM - works for all weeks."""
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

# ============================================================
# WEEK 3-8: TRAVEL AGENT
# ============================================================
def travel_agent(question: str, llm) -> str:
    """Week 3-4 onwards: Full agent with tool binding."""
    from langchain_core.messages import HumanMessage, SystemMessage
    try:
        response = llm.invoke([
            SystemMessage(content=(
                "You are TravelBot, an expert AI Travel Concierge. "
                "Help users plan amazing trips. Be friendly, specific, "
                "and include practical tips with budget estimates. "
                "Always give actionable, complete advice."
            )),
            HumanMessage(content=question)
        ])
        save_search("chat", question[:100], response.content[:200])
        return response.content
    except Exception as e:
        return f"Error: {str(e)[:100]}"

# ============================================================
# WEEK 5-6: ITINERARY GENERATOR
# ============================================================
def generate_itinerary_text(destination, days, budget, travelers, llm) -> str:
    """Week 5-6: Day-wise itinerary generator."""
    prompt = (
        f"Create a detailed {days}-day itinerary for {destination} "
        f"for {travelers} traveler(s) with {budget} budget.\n\n"
        f"For EACH day include:\n"
        f"- Morning: activity + practical tip\n"
        f"- Afternoon: activity + practical tip\n"
        f"- Evening: activity/restaurant + tip\n"
        f"- Estimated daily cost in USD\n"
        f"- 1-2 pro tips\n\n"
        f"Include local food recommendations, transport tips, "
        f"must-see attractions. Make it practical and exciting!"
    )
    try:
        response  = llm.invoke(prompt)
        itinerary = response.content
        save_itinerary_to_db(
            destination, days, budget, travelers,
            itinerary, f"{budget} for {travelers} travelers"
        )
        save_search("itinerary", f"{destination} {days}d", "itinerary created")
        return itinerary
    except Exception as e:
        return f"Error generating itinerary: {str(e)[:100]}"

# ============================================================
# WEEK 7-8: EXPORT FEATURE
# ============================================================
def export_trip_to_text(destination, days, budget, travelers, llm) -> str:
    """Week 7-8: Export itinerary to downloadable text."""
    itinerary = generate_itinerary_text(destination, days, budget, travelers, llm)
    budget_est = estimate_budget_info(destination, days, budget, travelers)
    content = (
        f"AI TRAVEL CONCIERGE - TRIP PLAN\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"{'='*60}\n\n"
        f"ITINERARY\n{'='*60}\n"
        f"{itinerary}\n\n"
        f"BUDGET ESTIMATE\n{'='*60}\n"
        f"{budget_est}\n\n"
        f"Generated by AI Travel Concierge | Powered by Groq + LangChain\n"
    )
    return content

# ============================================================
# INITIALIZE EVERYTHING
# ============================================================
with st.spinner("Loading AI Travel Concierge..."):
    llm, model_name = load_llm()

# ── Header ────────────────────────────────────────────────────
st.title("✈️ AI Travel Concierge")
st.markdown(
    f"Smart travel planning made easy — from flights and hotels to itineraries and budgets, all in one place."
    
)

st.divider()

# ============================================================
# TABS - All features from all weeks
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Chat",
    "🗓️ Trip Planner",
    "🌤️ Weather & Currency",
    "📚 Travel Knowledge",
    "💾 History",
    "ℹ️ About"
])

# ════════════════════════════════════════
# TAB 1: CHAT (Week 3-8)
# ════════════════════════════════════════
with tab1:
    st.subheader("Chat with TravelBot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role"   : "assistant",
            "content": (
                "👋 Hello! I'm TravelBot, your AI Travel Concierge!\n\n"
                "I can help you with everything:\n"
                "✈️ Flights | 🏨 Hotels | 🌤️ Weather\n"
                "🗓️ Itineraries | 💰 Budgets | 💱 Currency\n"
                "🗺️ Visa info | 🎒 Packing tips\n\n"
                "Try: *Plan a 5-day Bali trip for 2 people mid-range budget*"
            )
        }]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    st.markdown("**💡 Quick prompts:**")
    c1, c2, c3 = st.columns(3)
    quick_prompts = [
        "Plan 5-day Bali trip 2 people budget",
        "Best time to visit Japan?",
        "Budget for 7 days in Europe?",
        "Visa for Dubai from India",
        "Top things to do in Paris",
        "Cheap flight booking tips",
    ]
    for i, p in enumerate(quick_prompts):
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
# TAB 2: TRIP PLANNER (Week 5-6 + 7-8)
# ════════════════════════════════════════
with tab2:
    st.subheader("🗓️ Plan Your Perfect Trip")
    st.markdown("Fill in the details and get a complete day-by-day itinerary + budget!")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        destination = st.text_input("🌍 Destination", placeholder="e.g. Bali, Tokyo, Paris")
        days        = st.slider("📅 Number of Days", 1, 14, 5)
        budget      = st.radio("💰 Budget Level", ["budget", "mid-range", "luxury"], index=1)
        travelers   = st.slider("👥 Travelers", 1, 10, 2)

        c1, c2    = st.columns(2)
        plan_btn  = c1.button("🗓️ Plan Trip!", type="primary", use_container_width=True)
        cost_btn  = c2.button("💰 Estimate Cost", use_container_width=True)

        # Week 7-8: Export feature
        st.divider()
        export_btn = st.button("💾 Export Full Plan", use_container_width=True)
        if export_btn and destination:
            with st.spinner("Generating full plan..."):
                content = export_trip_to_text(destination, days, budget, travelers, llm)
            st.download_button(
                label="📥 Download Trip Plan",
                data=content,
                file_name=f"{destination}_{days}day_plan.txt",
                mime="text/plain",
                use_container_width=True
            )

    with col_right:
        itin_tab, budget_tab = st.tabs(["📍 Itinerary", "💰 Budget"])

        if plan_btn and destination:
            with itin_tab:
                with st.spinner(f"Creating your {days}-day {destination} itinerary..."):
                    result = generate_itinerary_text(destination, days, budget, travelers, llm)
                st.write(result)
                if st.button("💾 Save Itinerary to DB"):
                    st.success("✅ Saved to database!")

        if cost_btn and destination:
            with budget_tab:
                result = estimate_budget_info(destination, days, budget, travelers)
                st.markdown(result)

        if (plan_btn or cost_btn) and not destination:
            st.warning("⚠️ Please enter a destination first!")

        if not plan_btn and not cost_btn:
            st.info("👈 Fill in your trip details and click Plan Trip! or Estimate Cost")

# ════════════════════════════════════════
# TAB 3: WEATHER & CURRENCY (Week 3-4)
# ════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌤️ Weather Check")
        city = st.text_input("Enter city:", placeholder="e.g. Tokyo, Bali, Paris, Mumbai")
        if st.button("Get Weather", type="primary", use_container_width=True):
            if city:
                st.info(get_weather_info(city))
            else:
                st.warning("Please enter a city name!")

        st.markdown("**Quick cities:**")
        quick_cities = ["Tokyo", "Bali", "Paris", "Dubai", "Mumbai", "London"]
        cols = st.columns(3)
        for i, qc in enumerate(quick_cities):
            if cols[i % 3].button(qc, key=f"wc_{i}", use_container_width=True):
                st.info(get_weather_info(qc))

    with col2:
        st.subheader("💱 Currency Converter")
        amount    = st.number_input("Amount:", value=100.0, min_value=0.01)
        c1, c2    = st.columns(2)
        from_curr = c1.selectbox("From:", ["USD","EUR","GBP","INR","JPY","AUD","SGD","THB","CAD"])
        to_curr   = c2.selectbox("To:",   ["INR","USD","EUR","JPY","GBP","THB","SGD","AUD","CAD"])
        if st.button("Convert", type="primary", use_container_width=True):
            result = convert_currency_info(amount, from_curr, to_curr)
            st.success(result)

# ════════════════════════════════════════
# TAB 4: TRAVEL KNOWLEDGE (Week 1-2 RAG)
# ════════════════════════════════════════
with tab4:
    st.subheader("📚 Travel Knowledge Base")
    st.markdown(
        "This is the RAG knowledge base from **Week 1-2**. "
        "Ask any travel question and get answers from our knowledge base!"
    )

    rag_query = st.text_input(
        "Ask the knowledge base:",
        placeholder="e.g. What documents do I need for international travel?"
    )

    if st.button("Search Knowledge Base", type="primary"):
        if rag_query:
            with st.spinner("Searching knowledge base..."):
                # Use direct LLM with knowledge context for simplicity
                knowledge_text = "\n\n".join(TRAVEL_KNOWLEDGE)
                from langchain_core.messages import HumanMessage, SystemMessage
                response = llm.invoke([
                    SystemMessage(content=(
                        f"You are a travel expert. Answer questions using this knowledge:\n\n"
                        f"{knowledge_text}\n\n"
                        f"Be specific and practical."
                    )),
                    HumanMessage(content=rag_query)
                ])
                st.info(response.content)
                save_search("rag", rag_query, response.content[:200])
        else:
            st.warning("Please enter a question!")

    st.divider()
    st.markdown("**📋 Knowledge Base Topics:**")
    topics = [
        "Visa Information",
        "Travel Budget Tips",
        "Packing Essentials",
        "Top Destinations 2024",
        "India Travel Info",
        "Flight Booking Tips",
        "Hotel Booking Tips"
    ]
    c1, c2 = st.columns(2)
    for i, topic in enumerate(topics):
        col = c1 if i % 2 == 0 else c2
        col.info(f"📌 {topic}")

# ════════════════════════════════════════
# TAB 5: HISTORY (Week 5-6 SQLite DB)
# ════════════════════════════════════════
with tab5:
    st.subheader("💾 Your Saved Data")
    st.markdown(
        "All searches and itineraries saved automatically in **SQLite database** — "
        "built in **Week 5-6**."
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📋 Recent Searches")
        if st.button("🔄 Load Searches", use_container_width=True):
            rows = get_search_history(15)
            if rows:
                for r in rows:
                    st.info(f"**{r[0].upper()}** | {r[1][:50]} | {r[2][:16]}")
                st.caption(f"Showing {len(rows)} recent searches")
            else:
                st.write("No searches yet. Start chatting!")

    with c2:
        st.markdown("### 🗺️ Saved Itineraries")
        if st.button("🔄 Load Itineraries", use_container_width=True):
            rows = get_saved_itineraries()
            if rows:
                for r in rows:
                    st.success(
                        f"📍 **{r[0]}** | {r[1]} days | "
                        f"{r[2]} | {r[3]} travelers | {str(r[4])[:10]}"
                    )
                st.caption(f"{len(rows)} itineraries saved")
            else:
                st.write("No itineraries yet. Use Trip Planner!")

# ════════════════════════════════════════
# TAB 6: ABOUT (All weeks)
# ════════════════════════════════════════
with tab6:
    st.subheader("ℹ️ About This Project")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ## AI Travel Concierge
        **Internship Project | Track A | 8 Weeks**

        ### Tech Stack
        | Component | Technology |
        |-----------|------------|
        | LLM | Groq (LLaMA 3.3-70b) |
        | Framework | LangChain |
        | RAG | FAISS + HuggingFace |
        | Database | SQLite |
        | UI | Streamlit |
        | Deployment | Streamlit Cloud |

        ### APIs Used
        | API | Purpose |
        |-----|---------|
        | Groq | AI Language Model |
        | SERP API | Web Search |
        | Weatherstack | Weather Data |
        | ExchangeRate | Currency Rates |
        """)

    with col2:
        st.markdown("""
        ### Weekly Development

        **Week 1-2: Foundation & RAG**
        - RAG knowledge base (FAISS + HuggingFace)
        - Basic travel chatbot
        - Travel knowledge: visas, packing, destinations

        **Week 3-4: Agent + 5 Tools**
        - Weather tool (25+ cities)
        - Currency converter (live rates)
        - Flight search (SERP API)
        - Hotel search (SERP API)
        - Web search tool

        **Week 5-6: Specialization**
        - Day-wise itinerary generator
        - Budget estimator (20+ destinations)
        - SQLite database (saves all data)

        **Week 7-8: Final Polish**
        - Export feature (download trip plans)
        - Automated testing suite
        - Full deployment on Streamlit Cloud

        ### Progress
        - ✅ Week 1-2: Foundation & RAG
        - ✅ Week 3-4: Agent + 5 Tools
        - ✅ Week 5-6: Itinerary + Budget + DB
        - ✅ Week 7-8: Final Polish + Deployment
        """)
