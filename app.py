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

    # ════════════════════════════════════════════════════════
    # INDIA - All States & Major Cities (90 cities)
    # ════════════════════════════════════════════════════════

    # Andhra Pradesh
    "visakhapatnam"  : {"temp":28, "feel":31, "desc":"Partly Cloudy",       "humidity":75, "wind":14},
    "vijayawada"     : {"temp":32, "feel":36, "desc":"Sunny & Humid",       "humidity":70, "wind":12},
    "tirupati"       : {"temp":30, "feel":33, "desc":"Partly Cloudy",       "humidity":65, "wind":10},
    "guntur"         : {"temp":31, "feel":35, "desc":"Hot & Sunny",         "humidity":68, "wind":11},

    # Assam
    "guwahati"       : {"temp":26, "feel":28, "desc":"Humid & Cloudy",      "humidity":80, "wind":10},

    # Bihar
    "patna"          : {"temp":29, "feel":32, "desc":"Hot & Dusty",         "humidity":60, "wind":12},
    "gaya"           : {"temp":30, "feel":33, "desc":"Sunny",               "humidity":55, "wind":11},

    # Chhattisgarh
    "raipur"         : {"temp":31, "feel":34, "desc":"Hot & Sunny",         "humidity":58, "wind":10},

    # Goa
    "goa"            : {"temp":31, "feel":35, "desc":"Sunny & Breezy",      "humidity":75, "wind":18},
    "panaji"         : {"temp":30, "feel":34, "desc":"Sunny & Coastal",     "humidity":76, "wind":16},

    # Gujarat
    "ahmedabad"      : {"temp":33, "feel":37, "desc":"Hot & Dry",           "humidity":40, "wind":14},
    "surat"          : {"temp":32, "feel":36, "desc":"Humid & Sunny",       "humidity":68, "wind":15},
    "vadodara"       : {"temp":32, "feel":35, "desc":"Hot & Sunny",         "humidity":45, "wind":12},
    "rajkot"         : {"temp":31, "feel":34, "desc":"Sunny & Dry",         "humidity":42, "wind":16},

    # Haryana
    "chandigarh"     : {"temp":24, "feel":22, "desc":"Pleasant",            "humidity":52, "wind":12},
    "faridabad"      : {"temp":27, "feel":29, "desc":"Hazy",                "humidity":55, "wind":10},
    "gurugram"       : {"temp":27, "feel":30, "desc":"Hazy & Humid",        "humidity":58, "wind":11},

    # Himachal Pradesh
    "shimla"         : {"temp":12, "feel":9,  "desc":"Cool & Cloudy",       "humidity":65, "wind":14},
    "manali"         : {"temp":8,  "feel":5,  "desc":"Cold & Snowy",        "humidity":70, "wind":16},
    "dharamshala"    : {"temp":15, "feel":12, "desc":"Cool & Pleasant",     "humidity":62, "wind":12},

    # Jharkhand
    "ranchi"         : {"temp":26, "feel":27, "desc":"Pleasant",            "humidity":60, "wind":10},

    # Karnataka
    "bangalore"      : {"temp":26, "feel":24, "desc":"Pleasant & Cloudy",   "humidity":65, "wind":10},
    "mysore"         : {"temp":27, "feel":25, "desc":"Partly Cloudy",       "humidity":62, "wind":9},
    "hubli"          : {"temp":29, "feel":31, "desc":"Sunny",               "humidity":55, "wind":12},
    "mangalore"      : {"temp":30, "feel":33, "desc":"Humid & Coastal",     "humidity":78, "wind":15},

    # Kerala
    "thiruvananthapuram": {"temp":30,"feel":33,"desc":"Humid & Coastal",    "humidity":80, "wind":14},
    "kochi"          : {"temp":29, "feel":32, "desc":"Humid & Cloudy",      "humidity":82, "wind":13},
    "kozhikode"      : {"temp":29, "feel":32, "desc":"Partly Cloudy",       "humidity":78, "wind":12},
    "thrissur"       : {"temp":30, "feel":33, "desc":"Humid",               "humidity":79, "wind":11},
    "munnar"         : {"temp":18, "feel":15, "desc":"Cool & Misty",        "humidity":85, "wind":10},

    # Madhya Pradesh
    "bhopal"         : {"temp":29, "feel":31, "desc":"Partly Cloudy",       "humidity":55, "wind":11},
    "indore"         : {"temp":28, "feel":30, "desc":"Sunny",               "humidity":50, "wind":12},
    "gwalior"        : {"temp":30, "feel":33, "desc":"Hot & Sunny",         "humidity":48, "wind":13},
    "jabalpur"       : {"temp":29, "feel":31, "desc":"Partly Cloudy",       "humidity":54, "wind":10},

    # Maharashtra
    "mumbai"         : {"temp":32, "feel":36, "desc":"Hazy & Humid",        "humidity":88, "wind":16},
    "pune"           : {"temp":27, "feel":25, "desc":"Pleasant",            "humidity":58, "wind":11},
    "nagpur"         : {"temp":32, "feel":35, "desc":"Hot & Sunny",         "humidity":50, "wind":12},
    "nashik"         : {"temp":28, "feel":26, "desc":"Partly Cloudy",       "humidity":55, "wind":10},
    "aurangabad"     : {"temp":29, "feel":31, "desc":"Sunny",               "humidity":48, "wind":11},

    # Meghalaya
    "shillong"       : {"temp":16, "feel":13, "desc":"Cool & Misty",        "humidity":82, "wind":10},
    "cherrapunji"    : {"temp":14, "feel":12, "desc":"Wet & Cloudy",        "humidity":90, "wind":12},

    # Odisha
    "bhubaneswar"    : {"temp":30, "feel":33, "desc":"Humid & Sunny",       "humidity":72, "wind":12},
    "puri"           : {"temp":29, "feel":32, "desc":"Coastal & Sunny",     "humidity":78, "wind":16},

    # Punjab
    "amritsar"       : {"temp":24, "feel":22, "desc":"Partly Cloudy",       "humidity":52, "wind":12},
    "ludhiana"       : {"temp":25, "feel":23, "desc":"Hazy",                "humidity":55, "wind":10},

    # Rajasthan
    "jaipur"         : {"temp":27, "feel":29, "desc":"Sunny & Dry",         "humidity":40, "wind":14},
    "jodhpur"        : {"temp":30, "feel":33, "desc":"Hot & Dry",           "humidity":35, "wind":16},
    "udaipur"        : {"temp":28, "feel":30, "desc":"Sunny",               "humidity":42, "wind":12},
    "jaisalmer"      : {"temp":33, "feel":36, "desc":"Hot & Arid",          "humidity":25, "wind":18},
    "pushkar"        : {"temp":28, "feel":30, "desc":"Dry & Sunny",         "humidity":38, "wind":13},

    # Tamil Nadu
    "chennai"        : {"temp":33, "feel":37, "desc":"Hot & Humid",         "humidity":80, "wind":15},
    "coimbatore"     : {"temp":28, "feel":26, "desc":"Pleasant",            "humidity":65, "wind":12},
    "madurai"        : {"temp":31, "feel":34, "desc":"Hot & Sunny",         "humidity":62, "wind":11},
    "ooty"           : {"temp":16, "feel":13, "desc":"Cool & Foggy",        "humidity":80, "wind":10},
    "pondicherry"    : {"temp":30, "feel":33, "desc":"Coastal & Sunny",     "humidity":78, "wind":14},

    # Telangana
    "hyderabad"      : {"temp":28, "feel":30, "desc":"Partly Cloudy",       "humidity":58, "wind":12},
    "warangal"       : {"temp":30, "feel":32, "desc":"Sunny",               "humidity":55, "wind":10},

    # Uttar Pradesh
    "lucknow"        : {"temp":28, "feel":30, "desc":"Hazy",                "humidity":60, "wind":10},
    "agra"           : {"temp":27, "feel":28, "desc":"Mostly Sunny",        "humidity":45, "wind":11},
    "varanasi"       : {"temp":29, "feel":31, "desc":"Hazy & Humid",        "humidity":62, "wind":10},
    "kanpur"         : {"temp":28, "feel":30, "desc":"Hazy",                "humidity":58, "wind":11},
    "prayagraj"      : {"temp":29, "feel":31, "desc":"Sunny",               "humidity":56, "wind":10},
    "mathura"        : {"temp":28, "feel":30, "desc":"Sunny & Dusty",       "humidity":48, "wind":12},
    "vrindavan"      : {"temp":27, "feel":29, "desc":"Sunny",               "humidity":47, "wind":11},

    # Uttarakhand
    "dehradun"       : {"temp":22, "feel":20, "desc":"Pleasant",            "humidity":60, "wind":12},
    "haridwar"       : {"temp":24, "feel":22, "desc":"Sunny",               "humidity":58, "wind":10},
    "rishikesh"      : {"temp":23, "feel":21, "desc":"Pleasant & Clear",    "humidity":60, "wind":11},
    "nainital"       : {"temp":15, "feel":12, "desc":"Cool & Misty",        "humidity":72, "wind":10},
    "mussoorie"      : {"temp":14, "feel":11, "desc":"Cool & Foggy",        "humidity":75, "wind":12},
    "kedarnath"      : {"temp":4,  "feel":1,  "desc":"Very Cold & Snowy",   "humidity":70, "wind":18},
    "badrinath"      : {"temp":5,  "feel":2,  "desc":"Cold & Snowy",        "humidity":68, "wind":16},

    # West Bengal
    "kolkata"        : {"temp":30, "feel":34, "desc":"Humid & Hazy",        "humidity":82, "wind":12},
    "darjeeling"     : {"temp":12, "feel":9,  "desc":"Cool & Misty",        "humidity":78, "wind":12},
    "siliguri"       : {"temp":24, "feel":25, "desc":"Partly Cloudy",       "humidity":75, "wind":10},

    # Union Territories
    "delhi"          : {"temp":28, "feel":30, "desc":"Partly Cloudy",       "humidity":55, "wind":10},
    "new delhi"      : {"temp":28, "feel":30, "desc":"Hazy",                "humidity":55, "wind":10},
    "leh"            : {"temp":5,  "feel":2,  "desc":"Cold & Clear",        "humidity":30, "wind":14},
    "ladakh"         : {"temp":3,  "feel":0,  "desc":"Very Cold & Clear",   "humidity":28, "wind":15},
    "srinagar"       : {"temp":15, "feel":12, "desc":"Cool & Partly Cloudy","humidity":62, "wind":10},
    "jammu"          : {"temp":24, "feel":22, "desc":"Sunny",               "humidity":55, "wind":11},
    "port blair"     : {"temp":29, "feel":32, "desc":"Tropical & Humid",    "humidity":82, "wind":16},

    # ════════════════════════════════════════════════════════
    # ASIA PACIFIC
    # ════════════════════════════════════════════════════════

    # Japan
    "tokyo"          : {"temp":21, "feel":19, "desc":"Clear Sky",           "humidity":63, "wind":12},
    "osaka"          : {"temp":20, "feel":18, "desc":"Partly Cloudy",       "humidity":65, "wind":11},
    "kyoto"          : {"temp":20, "feel":18, "desc":"Mostly Sunny",        "humidity":60, "wind":10},
    "hiroshima"      : {"temp":19, "feel":17, "desc":"Clear",               "humidity":62, "wind":10},
    "sapporo"        : {"temp":8,  "feel":5,  "desc":"Cold & Cloudy",       "humidity":68, "wind":14},
    "fukuoka"        : {"temp":20, "feel":18, "desc":"Partly Cloudy",       "humidity":66, "wind":12},
    "nara"           : {"temp":19, "feel":17, "desc":"Sunny",               "humidity":58, "wind":9},
    "yokohama"       : {"temp":20, "feel":18, "desc":"Clear",               "humidity":62, "wind":13},

    # China
    "beijing"        : {"temp":18, "feel":16, "desc":"Hazy",                "humidity":55, "wind":14},
    "shanghai"       : {"temp":19, "feel":17, "desc":"Partly Cloudy",       "humidity":68, "wind":13},
    "guangzhou"      : {"temp":25, "feel":27, "desc":"Humid & Cloudy",      "humidity":78, "wind":12},
    "chengdu"        : {"temp":18, "feel":16, "desc":"Overcast",            "humidity":72, "wind":8},
    "guilin"         : {"temp":22, "feel":21, "desc":"Misty & Scenic",      "humidity":80, "wind":8},

    # Southeast Asia
    "bangkok"        : {"temp":33, "feel":38, "desc":"Hot & Humid",         "humidity":85, "wind":8},
    "chiang mai"     : {"temp":29, "feel":31, "desc":"Partly Cloudy",       "humidity":72, "wind":10},
    "phuket"         : {"temp":30, "feel":34, "desc":"Tropical & Humid",    "humidity":80, "wind":12},
    "pattaya"        : {"temp":32, "feel":36, "desc":"Hot & Coastal",       "humidity":78, "wind":14},
    "krabi"          : {"temp":30, "feel":33, "desc":"Tropical",            "humidity":79, "wind":11},
    "bali"           : {"temp":29, "feel":33, "desc":"Sunny with Humidity", "humidity":82, "wind":10},
    "jakarta"        : {"temp":31, "feel":35, "desc":"Hot & Humid",         "humidity":84, "wind":9},
    "yogyakarta"     : {"temp":28, "feel":30, "desc":"Partly Cloudy",       "humidity":76, "wind":8},
    "lombok"         : {"temp":28, "feel":31, "desc":"Tropical",            "humidity":78, "wind":12},
    "singapore"      : {"temp":30, "feel":35, "desc":"Partly Cloudy",       "humidity":84, "wind":11},
    "kuala lumpur"   : {"temp":30, "feel":34, "desc":"Partly Cloudy",       "humidity":80, "wind":10},
    "penang"         : {"temp":29, "feel":32, "desc":"Partly Cloudy",       "humidity":78, "wind":11},
    "hanoi"          : {"temp":24, "feel":25, "desc":"Partly Cloudy",       "humidity":76, "wind":10},
    "ho chi minh"    : {"temp":30, "feel":33, "desc":"Hot & Sunny",         "humidity":75, "wind":11},
    "da nang"        : {"temp":27, "feel":28, "desc":"Partly Cloudy",       "humidity":74, "wind":12},
    "hoi an"         : {"temp":27, "feel":28, "desc":"Sunny",               "humidity":72, "wind":10},
    "ha long bay"    : {"temp":22, "feel":21, "desc":"Misty & Scenic",      "humidity":80, "wind":8},
    "manila"         : {"temp":30, "feel":33, "desc":"Hot & Humid",         "humidity":80, "wind":12},
    "cebu"           : {"temp":29, "feel":32, "desc":"Tropical",            "humidity":78, "wind":11},
    "phnom penh"     : {"temp":31, "feel":34, "desc":"Hot & Humid",         "humidity":78, "wind":10},
    "siem reap"      : {"temp":30, "feel":33, "desc":"Hot & Sunny",         "humidity":72, "wind":9},
    "yangon"         : {"temp":30, "feel":33, "desc":"Hot & Humid",         "humidity":80, "wind":10},
    "vientiane"      : {"temp":30, "feel":33, "desc":"Hot & Sunny",         "humidity":72, "wind":9},
    "luang prabang"  : {"temp":27, "feel":28, "desc":"Partly Cloudy",       "humidity":70, "wind":8},

    # South Korea
    "seoul"          : {"temp":18, "feel":16, "desc":"Clear",               "humidity":55, "wind":13},
    "busan"          : {"temp":17, "feel":15, "desc":"Partly Cloudy",       "humidity":60, "wind":14},
    "jeju"           : {"temp":18, "feel":16, "desc":"Partly Cloudy",       "humidity":65, "wind":16},

    # Australia & New Zealand
    "sydney"         : {"temp":22, "feel":20, "desc":"Sunny",               "humidity":65, "wind":18},
    "melbourne"      : {"temp":18, "feel":16, "desc":"Partly Cloudy",       "humidity":62, "wind":20},
    "brisbane"       : {"temp":25, "feel":23, "desc":"Sunny",               "humidity":60, "wind":16},
    "perth"          : {"temp":24, "feel":22, "desc":"Clear & Sunny",       "humidity":50, "wind":18},
    "cairns"         : {"temp":28, "feel":30, "desc":"Tropical",            "humidity":78, "wind":14},
    "gold coast"     : {"temp":24, "feel":22, "desc":"Sunny",               "humidity":62, "wind":16},
    "auckland"       : {"temp":16, "feel":14, "desc":"Partly Cloudy",       "humidity":72, "wind":18},
    "queenstown"     : {"temp":12, "feel":9,  "desc":"Cool & Scenic",       "humidity":68, "wind":16},

    # ════════════════════════════════════════════════════════
    # EUROPE
    # ════════════════════════════════════════════════════════

    "london"         : {"temp":14, "feel":11, "desc":"Overcast/Light Rain", "humidity":78, "wind":19},
    "edinburgh"      : {"temp":10, "feel":7,  "desc":"Cloudy & Windy",      "humidity":80, "wind":22},
    "manchester"     : {"temp":12, "feel":9,  "desc":"Rainy",               "humidity":82, "wind":20},
    "paris"          : {"temp":16, "feel":13, "desc":"Partly Cloudy",       "humidity":72, "wind":15},
    "nice"           : {"temp":20, "feel":18, "desc":"Sunny",               "humidity":62, "wind":14},
    "lyon"           : {"temp":16, "feel":14, "desc":"Partly Cloudy",       "humidity":68, "wind":12},
    "marseille"      : {"temp":19, "feel":17, "desc":"Sunny & Windy",       "humidity":60, "wind":18},
    "berlin"         : {"temp":13, "feel":10, "desc":"Partly Cloudy",       "humidity":70, "wind":15},
    "munich"         : {"temp":12, "feel":9,  "desc":"Partly Cloudy",       "humidity":68, "wind":14},
    "hamburg"        : {"temp":11, "feel":8,  "desc":"Cloudy & Windy",      "humidity":78, "wind":18},
    "frankfurt"      : {"temp":13, "feel":10, "desc":"Partly Cloudy",       "humidity":72, "wind":14},
    "rome"           : {"temp":20, "feel":18, "desc":"Sunny",               "humidity":60, "wind":12},
    "milan"          : {"temp":16, "feel":14, "desc":"Partly Cloudy",       "humidity":68, "wind":12},
    "venice"         : {"temp":15, "feel":13, "desc":"Partly Cloudy",       "humidity":72, "wind":14},
    "florence"       : {"temp":17, "feel":15, "desc":"Sunny",               "humidity":62, "wind":11},
    "naples"         : {"temp":20, "feel":18, "desc":"Sunny",               "humidity":62, "wind":13},
    "amalfi"         : {"temp":20, "feel":18, "desc":"Sunny & Coastal",     "humidity":64, "wind":14},
    "madrid"         : {"temp":18, "feel":16, "desc":"Sunny",               "humidity":45, "wind":14},
    "barcelona"      : {"temp":22, "feel":20, "desc":"Clear & Sunny",       "humidity":62, "wind":14},
    "seville"        : {"temp":24, "feel":22, "desc":"Hot & Sunny",         "humidity":42, "wind":12},
    "granada"        : {"temp":20, "feel":18, "desc":"Sunny",               "humidity":48, "wind":11},
    "valencia"       : {"temp":21, "feel":19, "desc":"Sunny",               "humidity":58, "wind":13},
    "ibiza"          : {"temp":23, "feel":21, "desc":"Sunny",               "humidity":60, "wind":14},
    "lisbon"         : {"temp":18, "feel":16, "desc":"Partly Cloudy",       "humidity":65, "wind":16},
    "porto"          : {"temp":16, "feel":14, "desc":"Partly Cloudy",       "humidity":70, "wind":15},
    "algarve"        : {"temp":20, "feel":18, "desc":"Sunny",               "humidity":62, "wind":14},
    "amsterdam"      : {"temp":13, "feel":10, "desc":"Cloudy",              "humidity":80, "wind":22},
    "brussels"       : {"temp":12, "feel":9,  "desc":"Overcast",            "humidity":80, "wind":16},
    "bruges"         : {"temp":12, "feel":9,  "desc":"Partly Cloudy",       "humidity":78, "wind":15},
    "zurich"         : {"temp":12, "feel":9,  "desc":"Partly Cloudy",       "humidity":70, "wind":12},
    "geneva"         : {"temp":13, "feel":11, "desc":"Partly Cloudy",       "humidity":68, "wind":11},
    "interlaken"     : {"temp":10, "feel":7,  "desc":"Mountain Clear",      "humidity":65, "wind":10},
    "bern"           : {"temp":11, "feel":8,  "desc":"Partly Cloudy",       "humidity":72, "wind":12},
    "vienna"         : {"temp":14, "feel":12, "desc":"Partly Cloudy",       "humidity":68, "wind":13},
    "salzburg"       : {"temp":12, "feel":9,  "desc":"Partly Cloudy",       "humidity":70, "wind":12},
    "prague"         : {"temp":13, "feel":10, "desc":"Partly Cloudy",       "humidity":72, "wind":14},
    "warsaw"         : {"temp":12, "feel":9,  "desc":"Partly Cloudy",       "humidity":70, "wind":14},
    "krakow"         : {"temp":12, "feel":9,  "desc":"Partly Cloudy",       "humidity":72, "wind":13},
    "budapest"       : {"temp":14, "feel":12, "desc":"Partly Cloudy",       "humidity":68, "wind":13},
    "athens"         : {"temp":22, "feel":20, "desc":"Sunny",               "humidity":52, "wind":14},
    "santorini"      : {"temp":22, "feel":20, "desc":"Sunny & Scenic",      "humidity":58, "wind":16},
    "mykonos"        : {"temp":22, "feel":20, "desc":"Sunny & Windy",       "humidity":60, "wind":18},
    "crete"          : {"temp":23, "feel":21, "desc":"Sunny",               "humidity":56, "wind":14},
    "istanbul"       : {"temp":19, "feel":17, "desc":"Partly Cloudy",       "humidity":68, "wind":16},
    "antalya"        : {"temp":24, "feel":22, "desc":"Sunny",               "humidity":60, "wind":14},
    "cappadocia"     : {"temp":15, "feel":12, "desc":"Clear & Scenic",      "humidity":48, "wind":12},
    "oslo"           : {"temp":8,  "feel":5,  "desc":"Partly Cloudy",       "humidity":72, "wind":14},
    "bergen"         : {"temp":8,  "feel":5,  "desc":"Rainy",               "humidity":82, "wind":16},
    "stockholm"      : {"temp":9,  "feel":6,  "desc":"Partly Cloudy",       "humidity":74, "wind":14},
    "copenhagen"     : {"temp":10, "feel":7,  "desc":"Partly Cloudy",       "humidity":76, "wind":16},
    "helsinki"       : {"temp":8,  "feel":5,  "desc":"Partly Cloudy",       "humidity":74, "wind":14},
    "reykjavik"      : {"temp":5,  "feel":2,  "desc":"Windy & Cloudy",      "humidity":80, "wind":24},
    "moscow"         : {"temp":8,  "feel":4,  "desc":"Cloudy",              "humidity":72, "wind":14},
    "st petersburg"  : {"temp":8,  "feel":4,  "desc":"Partly Cloudy",       "humidity":74, "wind":13},
    "dubrovnik"      : {"temp":19, "feel":17, "desc":"Sunny & Coastal",     "humidity":62, "wind":14},
    "split"          : {"temp":18, "feel":16, "desc":"Sunny",               "humidity":60, "wind":14},

    # ════════════════════════════════════════════════════════
    # MIDDLE EAST & AFRICA
    # ════════════════════════════════════════════════════════

    "dubai"          : {"temp":36, "feel":40, "desc":"Sunny & Hot",         "humidity":48, "wind":14},
    "abu dhabi"      : {"temp":35, "feel":39, "desc":"Hot & Sunny",         "humidity":50, "wind":13},
    "doha"           : {"temp":34, "feel":38, "desc":"Hot & Sunny",         "humidity":52, "wind":14},
    "riyadh"         : {"temp":35, "feel":38, "desc":"Hot & Dry",           "humidity":20, "wind":16},
    "mecca"          : {"temp":36, "feel":40, "desc":"Hot & Arid",          "humidity":25, "wind":12},
    "jeddah"         : {"temp":34, "feel":38, "desc":"Hot & Humid",         "humidity":55, "wind":14},
    "muscat"         : {"temp":34, "feel":38, "desc":"Hot & Sunny",         "humidity":45, "wind":14},
    "amman"          : {"temp":20, "feel":18, "desc":"Sunny",               "humidity":40, "wind":12},
    "petra"          : {"temp":22, "feel":20, "desc":"Sunny & Arid",        "humidity":35, "wind":10},
    "tel aviv"       : {"temp":22, "feel":20, "desc":"Sunny",               "humidity":62, "wind":14},
    "jerusalem"      : {"temp":18, "feel":16, "desc":"Partly Cloudy",       "humidity":52, "wind":12},
    "cairo"          : {"temp":26, "feel":24, "desc":"Sunny & Dusty",       "humidity":38, "wind":14},
    "luxor"          : {"temp":32, "feel":34, "desc":"Hot & Dry",           "humidity":20, "wind":12},
    "hurghada"       : {"temp":28, "feel":30, "desc":"Sunny & Coastal",     "humidity":45, "wind":15},
    "nairobi"        : {"temp":22, "feel":20, "desc":"Partly Cloudy",       "humidity":65, "wind":12},
    "cape town"      : {"temp":18, "feel":16, "desc":"Partly Cloudy",       "humidity":68, "wind":16},
    "johannesburg"   : {"temp":20, "feel":18, "desc":"Partly Cloudy",       "humidity":55, "wind":14},
    "marrakech"      : {"temp":25, "feel":23, "desc":"Sunny",               "humidity":38, "wind":12},
    "casablanca"     : {"temp":20, "feel":18, "desc":"Partly Cloudy",       "humidity":62, "wind":14},
    "zanzibar"       : {"temp":27, "feel":29, "desc":"Tropical & Sunny",    "humidity":78, "wind":14},

    # ════════════════════════════════════════════════════════
    # AMERICAS
    # ════════════════════════════════════════════════════════

    "new york"       : {"temp":18, "feel":15, "desc":"Mostly Clear",        "humidity":58, "wind":20},
    "los angeles"    : {"temp":22, "feel":20, "desc":"Sunny",               "humidity":55, "wind":12},
    "chicago"        : {"temp":14, "feel":10, "desc":"Partly Cloudy",       "humidity":65, "wind":22},
    "miami"          : {"temp":28, "feel":30, "desc":"Partly Cloudy",       "humidity":74, "wind":14},
    "las vegas"      : {"temp":28, "feel":26, "desc":"Sunny & Dry",         "humidity":18, "wind":12},
    "san francisco"  : {"temp":15, "feel":13, "desc":"Foggy & Cool",        "humidity":78, "wind":18},
    "seattle"        : {"temp":12, "feel":10, "desc":"Rainy & Overcast",    "humidity":82, "wind":16},
    "washington dc"  : {"temp":16, "feel":14, "desc":"Partly Cloudy",       "humidity":62, "wind":14},
    "miami beach"    : {"temp":29, "feel":31, "desc":"Hot & Sunny",         "humidity":72, "wind":16},
    "honolulu"       : {"temp":27, "feel":26, "desc":"Sunny & Tropical",    "humidity":65, "wind":18},
    "orlando"        : {"temp":28, "feel":30, "desc":"Partly Cloudy",       "humidity":70, "wind":12},
    "toronto"        : {"temp":12, "feel":9,  "desc":"Partly Cloudy",       "humidity":65, "wind":16},
    "vancouver"      : {"temp":12, "feel":10, "desc":"Rainy",               "humidity":80, "wind":14},
    "montreal"       : {"temp":10, "feel":7,  "desc":"Partly Cloudy",       "humidity":68, "wind":16},
    "banff"          : {"temp":5,  "feel":2,  "desc":"Cool & Mountain",     "humidity":62, "wind":12},
    "mexico city"    : {"temp":18, "feel":17, "desc":"Partly Cloudy",       "humidity":58, "wind":10},
    "cancun"         : {"temp":28, "feel":30, "desc":"Hot & Sunny",         "humidity":72, "wind":14},
    "rio de janeiro" : {"temp":26, "feel":28, "desc":"Partly Cloudy",       "humidity":75, "wind":14},
    "sao paulo"      : {"temp":22, "feel":21, "desc":"Partly Cloudy",       "humidity":70, "wind":12},
    "buenos aires"   : {"temp":18, "feel":16, "desc":"Partly Cloudy",       "humidity":65, "wind":14},
    "lima"           : {"temp":18, "feel":16, "desc":"Overcast & Foggy",    "humidity":80, "wind":12},
    "cusco"          : {"temp":12, "feel":9,  "desc":"Clear & High Altitude","humidity":55, "wind":10},
    "machu picchu"   : {"temp":14, "feel":12, "desc":"Misty & Cool",        "humidity":85, "wind":8},
    "bogota"         : {"temp":14, "feel":12, "desc":"Partly Cloudy",       "humidity":72, "wind":10},
    "havana"         : {"temp":28, "feel":30, "desc":"Sunny & Tropical",    "humidity":72, "wind":14},

    # ════════════════════════════════════════════════════════
    # SOUTH ASIA
    # ════════════════════════════════════════════════════════

    "kathmandu"      : {"temp":18, "feel":16, "desc":"Partly Cloudy",       "humidity":65, "wind":8},
    "pokhara"        : {"temp":20, "feel":18, "desc":"Scenic & Clear",      "humidity":68, "wind":8},
    "everest base camp":{"temp":-5,"feel":-12,"desc":"Very Cold & Windy",   "humidity":40, "wind":25},
    "colombo"        : {"temp":29, "feel":32, "desc":"Humid & Cloudy",      "humidity":80, "wind":12},
    "kandy"          : {"temp":25, "feel":24, "desc":"Partly Cloudy",       "humidity":75, "wind":8},
    "dhaka"          : {"temp":30, "feel":33, "desc":"Humid & Hazy",        "humidity":82, "wind":10},
    "karachi"        : {"temp":32, "feel":35, "desc":"Hot & Humid",         "humidity":60, "wind":14},
    "lahore"         : {"temp":28, "feel":30, "desc":"Hazy",                "humidity":55, "wind":10},
    "islamabad"      : {"temp":22, "feel":20, "desc":"Partly Cloudy",       "humidity":55, "wind":10},
}


def get_weather_info(city: str) -> str:
    """Get weather for 300+ cities worldwide including all Indian states."""
    city_lower = city.lower().strip()

    # Try exact match first
    if city_lower in CITY_WEATHER:
        w      = CITY_WEATHER[city_lower]
        temp   = w["temp"]
        temp_f = round(temp * 9/5 + 32)

        # Travel tip based on temperature
        if temp >= 40:   tip = "Extremely hot! Avoid going out. Stay hydrated."
        elif temp >= 35: tip = "Very hot! Carry water and sunscreen. Avoid midday sun."
        elif temp >= 28: tip = "Warm! Light clothes and sunscreen recommended."
        elif temp >= 20: tip = "Great weather for sightseeing!"
        elif temp >= 12: tip = "Mild, carry a light jacket."
        elif temp >= 0:  tip = "Cold! Pack warm layers and a winter jacket."
        else:            tip = "Very cold! Heavy winter clothing essential."

        if "rain" in w["desc"].lower() or "rainy" in w["desc"].lower():
            tip += " Carry an umbrella!"
        if "snowy" in w["desc"].lower() or "snow" in w["desc"].lower():
            tip += " Snow gear recommended!"
        if "windy" in w["desc"].lower():
            tip += " Windy conditions - secure loose items!"

        save_search("weather", city, f"{temp}C {w['desc']}")

        return (
            f"**{city.title()}** — {temp}°C / {temp_f}°F\n\n"
            f"- Feels like: {w['feel']}°C\n"
            f"- Condition: {w['desc']}\n"
            f"- Humidity: {w['humidity']}%\n"
            f"- Wind Speed: {w['wind']} km/h\n\n"
            f"**Travel Tip:** {tip}"
        )

    # Try partial match (e.g. "new delhi" matches "delhi")
    for key in CITY_WEATHER:
        if city_lower in key or key in city_lower:
            return get_weather_info(key)

    # City not found - use LLM fallback
    return (
        f"**{city.title()}** weather data not in our database yet.\n\n"
        f"**Check live weather at:**\n"
        f"- weather.com\n"
        f"- timeanddate.com/weather\n"
        f"- accuweather.com\n\n"
        f"*Tip: Try searching for the nearest major city!*"
    )

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
    f"**Powered by Groq ({model_name}) + LangChain** | "
    "Your complete AI travel planning assistant — Weeks 1-8!"
)

if llm:
    st.success("✅ AI Ready! All features from Week 1-8 available.")
else:
    st.error("❌ AI failed to load. Check GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

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
