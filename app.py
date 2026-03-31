# ============================================================
# app.py - Streamlit Version (for Streamlit Cloud deployment)
# ============================================================
import streamlit as st
import os
import requests

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

# ── Initialize LLM ────────────────────────────────────────────
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

# ── Weather data ──────────────────────────────────────────────
CITY_WEATHER = {
    "london"   : {"temp":14, "feel":11, "desc":"Overcast/Light Rain", "humidity":78, "wind":19},
    "paris"    : {"temp":16, "feel":13, "desc":"Partly Cloudy",       "humidity":72, "wind":15},
    "tokyo"    : {"temp":21, "feel":19, "desc":"Clear Sky",           "humidity":63, "wind":12},
    "bali"     : {"temp":29, "feel":33, "desc":"Sunny with Humidity", "humidity":82, "wind":10},
    "bangkok"  : {"temp":33, "feel":38, "desc":"Hot & Humid",         "humidity":85, "wind":8},
    "singapore": {"temp":30, "feel":35, "desc":"Partly Cloudy",       "humidity":84, "wind":11},
    "dubai"    : {"temp":36, "feel":40, "desc":"Sunny & Hot",         "humidity":48, "wind":14},
    "mumbai"   : {"temp":32, "feel":36, "desc":"Hazy & Humid",        "humidity":88, "wind":16},
    "delhi"    : {"temp":28, "feel":30, "desc":"Partly Cloudy",       "humidity":55, "wind":10},
    "new york" : {"temp":18, "feel":15, "desc":"Mostly Clear",        "humidity":58, "wind":20},
    "sydney"   : {"temp":22, "feel":20, "desc":"Sunny",               "humidity":65, "wind":18},
    "rome"     : {"temp":20, "feel":18, "desc":"Sunny",               "humidity":60, "wind":12},
    "barcelona": {"temp":22, "feel":20, "desc":"Clear & Sunny",       "humidity":62, "wind":14},
    "goa"      : {"temp":31, "feel":35, "desc":"Sunny & Breezy",      "humidity":75, "wind":18},
    "bangalore": {"temp":26, "feel":24, "desc":"Pleasant & Cloudy",   "humidity":65, "wind":10},
}

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
        return (
            f"**{city.title()}** — {temp}°C / {temp_f}°F\n\n"
            f"- Condition: {w['desc']}\n"
            f"- Humidity: {w['humidity']}%\n"
            f"- Wind: {w['wind']} km/h\n"
            f"- Tip: {tip}"
        )
    return f"Weather data not available for {city.title()}."

def convert_currency_info(amount, fr, to) -> str:
    try:
        r = requests.get(
            f"https://v6.exchangerate-api.com/v6/"
            f"{keys['EXCHANGERATE_API_KEY']}/pair/{fr}/{to}/{amount}",
            timeout=10
        ).json()
        if r.get("result") == "success":
            return (
                f"**{amount:,.2f} {fr} = {r['conversion_result']:,.2f} {to}**\n\n"
                f"Rate: 1 {fr} = {r['conversion_rate']:.4f} {to}"
            )
        return f"Could not convert {fr} to {to}"
    except Exception:
        return "Currency service unavailable"

# ── Travel Agent ──────────────────────────────────────────────
def travel_agent(question: str, llm) -> str:
    """Main travel agent using LLM."""
    from langchain_core.messages import HumanMessage, SystemMessage
    try:
        system = (
            "You are TravelBot, an expert AI Travel Concierge. "
            "Help users plan amazing trips. Be friendly, specific, "
            "and include practical tips with budget estimates."
        )
        response = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=question)
        ])
        return response.content
    except Exception as e:
        return f"Error: {str(e)[:100]}"

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
    st.success(f"✅ AI Ready!")
else:
    st.error("❌ AI failed to load. Check GROQ_API_KEY in secrets.")
    st.stop()

st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chat",
    "🌤️ Weather & Currency",
    "🗓️ Trip Planner",
    "ℹ️ About"
])

# ════════════════════════════════════════
# TAB 1: CHAT
# ════════════════════════════════════════
with tab1:
    st.subheader("Chat with TravelBot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role"   : "assistant",
                "content": (
                    "👋 Hello! I'm TravelBot!\n\n"
                    "Ask me anything about:\n"
                    "✈️ Flights | 🏨 Hotels | 🌤️ Weather\n"
                    "💱 Currency | 🗓️ Itineraries | 💰 Budgets\n\n"
                    "Try: *Plan a 5-day Bali trip for 2 people*"
                )
            }
        ]

    # Show chat messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Quick prompt buttons
    st.markdown("**💡 Quick prompts:**")
    col1, col2, col3 = st.columns(3)
    quick_prompts = [
        "Plan 5-day Bali trip for 2 people mid-range budget",
        "What's the best time to visit Japan?",
        "Budget for 7 days in Europe?",
        "Visa requirements for Dubai from India",
        "Top things to do in Paris",
        "Cheap flights tips for international travel",
    ]
    for i, prompt in enumerate(quick_prompts):
        col = [col1, col2, col3][i % 3]
        if col.button(prompt, key=f"qp_{i}", use_container_width=True):
            st.session_state.pending_input = prompt
            st.rerun()

    # Handle quick prompt
    if "pending_input" in st.session_state:
        user_input = st.session_state.pending_input
        del st.session_state.pending_input
    else:
        user_input = st.chat_input("Ask anything about travel...")

    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = travel_agent(user_input, llm)
            st.write(response)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

# ════════════════════════════════════════
# TAB 2: WEATHER & CURRENCY
# ════════════════════════════════════════
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌤️ Weather Check")
        city = st.text_input(
            "Enter city:",
            placeholder="e.g. Tokyo, Bali, Paris"
        )
        if st.button("Get Weather", use_container_width=True, type="primary"):
            if city:
                result = get_weather_info(city)
                st.info(result)
            else:
                st.warning("Please enter a city name!")

    with col2:
        st.subheader("💱 Currency Converter")
        amount    = st.number_input("Amount:", value=100.0, min_value=0.01)
        c1, c2    = st.columns(2)
        from_curr = c1.selectbox(
            "From:",
            ["USD","EUR","GBP","INR","JPY","AUD","SGD","THB"]
        )
        to_curr   = c2.selectbox(
            "To:",
            ["INR","USD","EUR","JPY","GBP","THB","SGD","AUD"]
        )
        if st.button("Convert", use_container_width=True, type="primary"):
            result = convert_currency_info(amount, from_curr, to_curr)
            st.success(result)

# ════════════════════════════════════════
# TAB 3: TRIP PLANNER
# ════════════════════════════════════════
with tab3:
    st.subheader("🗓️ Plan Your Perfect Trip")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        destination = st.text_input(
            "🌍 Destination",
            placeholder="e.g. Bali, Tokyo, Paris"
        )
        days      = st.slider("📅 Number of Days", 1, 14, 5)
        budget    = st.radio(
            "💰 Budget Level",
            ["budget", "mid-range", "luxury"],
            index=1
        )
        travelers = st.slider("👥 Travelers", 1, 10, 2)

        c1, c2    = st.columns(2)
        plan_btn  = c1.button(
            "🗓️ Plan Trip!",
            type="primary",
            use_container_width=True
        )
        cost_btn  = c2.button(
            "💰 Estimate Cost",
            use_container_width=True
        )

    with col_right:
        if plan_btn and destination:
            with st.spinner("Creating your itinerary..."):
                q = (
                    f"Create a detailed {days}-day itinerary for "
                    f"{destination} for {travelers} traveler(s) with "
                    f"{budget} budget. Include morning, afternoon, and "
                    f"evening activities. Add food recommendations, "
                    f"transport tips, and estimated daily cost in USD."
                )
                result = travel_agent(q, llm)
                st.markdown("### 📍 Your Itinerary")
                st.write(result)

        elif cost_btn and destination:
            with st.spinner("Calculating budget..."):
                q = (
                    f"Estimate the total cost for a {days}-day "
                    f"{budget} trip to {destination} for {travelers} "
                    f"traveler(s). Break down costs for: accommodation, "
                    f"food, activities, local transport, and flights. "
                    f"Give a total estimate in USD."
                )
                result = travel_agent(q, llm)
                st.markdown("### 💰 Budget Estimate")
                st.write(result)

        elif (plan_btn or cost_btn) and not destination:
            st.warning("⚠️ Please enter a destination first!")

        else:
            st.info(
                "👈 Fill in your trip details on the left "
                "and click Plan Trip or Estimate Cost!"
            )

# ════════════════════════════════════════
# TAB 4: ABOUT
# ════════════════════════════════════════
with tab4:
    st.subheader("ℹ️ About This Project")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ## AI Travel Concierge
        **Internship Project | Track A | 8 Weeks**

        ### Tech Stack
        | Component | Technology |
        |-----------|------------|
        | LLM | Groq (LLaMA 3.3) |
        | Framework | LangChain |
        | UI | Streamlit |
        | Deployment | Streamlit Cloud |
        """)

    with col2:
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
        - ✅ Week 3-4: Agent + Tools
        - 🔄 Week 5-6: Itinerary & DB
        - ⏳ Week 7-8: Final Polish
        """)
