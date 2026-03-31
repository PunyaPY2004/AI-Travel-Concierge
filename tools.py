# ============================================================
# TOOL 1-WEATHER TOOL - FINAL CLEAN VERSION (FIXED - No Emoji in code)
# ============================================================
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """
    Get current weather and travel conditions for a city.
    Input: city name e.g. 'Paris' or 'Tokyo' or 'Bali'
    """
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
        "phuket"    : {"temp":30, "feel":34, "desc":"Tropical & Humid",     "humidity":80, "wind":12},
        "goa"       : {"temp":31, "feel":35, "desc":"Sunny & Breezy",       "humidity":75, "wind":18},
        "mumbai"    : {"temp":32, "feel":36, "desc":"Hazy & Humid",         "humidity":88, "wind":16},
        "bangalore" : {"temp":26, "feel":24, "desc":"Pleasant & Cloudy",    "humidity":65, "wind":10},
        "chennai"   : {"temp":33, "feel":37, "desc":"Hot & Humid",          "humidity":80, "wind":15},
        "hyderabad" : {"temp":28, "feel":30, "desc":"Partly Cloudy",        "humidity":58, "wind":12},
        "jaipur"    : {"temp":27, "feel":29, "desc":"Sunny & Dry",          "humidity":40, "wind":14},
        "agra"      : {"temp":27, "feel":28, "desc":"Mostly Sunny",         "humidity":45, "wind":11},
    }

    city_lower = city.lower().strip()

    # ── Case 1: City in built-in database ───────────────────
    if city_lower in CITY_WEATHER:
        w      = CITY_WEATHER[city_lower]
        temp   = w["temp"]
        temp_f = round(temp * 9/5 + 32)

        # Travel tip based on temperature
        if temp >= 35:
            tip = "Very hot! Carry water, use sunscreen, avoid midday sun."
        elif temp >= 28:
            tip = "Warm and pleasant! Light clothes, sunscreen recommended."
        elif temp >= 20:
            tip = "Great weather for sightseeing! Comfortable temperature."
        elif temp >= 12:
            tip = "Mild but cool. Carry a light jacket."
        elif temp >= 5:
            tip = "Cold! Pack warm layers and a winter jacket."
        else:
            tip = "Very cold! Heavy winter clothing essential."

        if "rain" in w["desc"].lower():
            tip += " Carry an umbrella!"

        # Build output string with emojis in Python strings (safe)
        line1 = "Weather in " + city.title()
        line2 = "=" * 40
        line3 = "Temperature  : " + str(temp) + "C / " + str(temp_f) + "F"
        line4 = "Feels like   : " + str(w["feel"]) + "C"
        line5 = "Condition    : " + w["desc"]
        line6 = "Humidity     : " + str(w["humidity"]) + "%"
        line7 = "Wind Speed   : " + str(w["wind"]) + " km/h"
        line8 = "Travel Tip   : " + tip

        return (
            "\n" +
            "\U0001f30d " + line1 + "\n" +   # globe emoji
            line2 + "\n" +
            "\U0001f321  " + line3 + "\n" +  # thermometer emoji
            "     " + line4 + "\n" +
            "\u2601  " + line5 + "\n" +       # cloud emoji
            "\U0001f4a7 " + line6 + "\n" +   # droplet emoji
            "\U0001f4a8 " + line7 + "\n" +   # wind emoji
            line2 + "\n" +
            "\U0001f4a1 " + line8            # bulb emoji
        )

    # ── Case 2: City NOT in database → LLM with strict prompt ──
    try:
        prompt = (
            "Give weather info for " + city.title() + ". "
            "Use ONE single estimate, not seasonal breakdown. "
            "Reply in this exact format:\n"
            "Weather in " + city.title() + ":\n"
            "Temperature: [number] C\n"
            "Feels like: [number] C\n"
            "Condition: [one condition]\n"
            "Humidity: [number] %\n"
            "Wind: [number] km/h\n"
            "Travel Tip: [one practical tip]"
        )
        resp = llm.invoke(prompt)
        return resp.content.strip()

    except Exception as e:
        return (
            "Weather data unavailable for " + city.title() + ".\n"
            "Check weather.com or timeanddate.com\n"
            "Error: " + str(e)[:60]
        )


# ── Test ─────────────────────────────────────────────────────
print("Testing Final Weather Tool...\n")

for city in ["Paris", "Bali", "Tokyo", "Mumbai", "Dubai"]:
    print(get_weather.invoke(city))
    print()

# ============================================================
# TOOL 2: CURRENCY CONVERTER (ExchangeRate API)
# ============================================================

@tool
def convert_currency(query: str) -> str:
    """
    Convert currency amounts for travel budgeting.
    Use when user asks about currency exchange, travel budget in local currency, or money conversion.
    Input format: 'amount FROM_CURRENCY TO_CURRENCY' e.g. '100 USD INR' or '50 EUR JPY'
    Common codes: USD, EUR, INR, GBP, JPY, AUD, CAD, SGD, THB, IDR
    """
    try:
        # Parse the input
        parts = query.strip().split()
        if len(parts) < 3:
            return "Please provide: 'amount FROM TO' e.g. '100 USD INR'"

        amount     = float(parts[0])
        from_curr  = parts[1].upper()
        to_curr    = parts[2].upper()

        # Call ExchangeRate API
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{from_curr}/{to_curr}/{amount}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("result") == "success":
            converted    = data["conversion_result"]
            rate         = data["conversion_rate"]

            return f"""
💱 Currency Conversion:
   {amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}
   Exchange Rate: 1 {from_curr} = {rate:.4f} {to_curr}

💡 Travel Budget Tips:
   • Always carry some local cash for small purchases
   • Use Wise/Revolut for low-fee international transfers
   • Avoid airport currency exchange (poor rates)
   • Notify your bank before traveling abroad
            """
        else:
            error = data.get("error-type", "Unknown error")
            # Fallback: provide approximate rates for common pairs
            fallback_rates = {
                ("USD", "INR"): 83.5, ("EUR", "INR"): 90.2,
                ("GBP", "INR"): 105.8, ("USD", "EUR"): 0.92,
                ("USD", "JPY"): 149.5, ("USD", "THB"): 35.2
            }
            rate = fallback_rates.get((from_curr, to_curr))
            if rate:
                converted = amount * rate
                return f"💱 Approximate: {amount} {from_curr} ≈ {converted:,.2f} {to_curr} (offline rate, may vary)"
            return f"Could not convert {from_curr} to {to_curr}: {error}"

    except ValueError:
        return "Invalid amount. Use format: '100 USD INR'"
    except Exception as e:
        return f"Currency conversion error: {str(e)}"


# Test it
print("🧪 Testing Currency Converter...")
print(convert_currency.invoke("1000 USD INR"))

# ============================================================
# TOOL 3: FLIGHT SEARCH (SERP API - Google Flights)
# ============================================================
from serpapi import GoogleSearch

@tool
def search_flights(query: str) -> str:
    """
    Search for flight information between destinations.
    Use when user asks about flights, airfares, or travel routes.
    Input format: 'FROM_CITY TO_CITY DATE' e.g. 'Mumbai London 2025-03-15'
    or just 'FROM_CITY TO_CITY' for general info
    """
    try:
        parts = query.strip().split()
        if len(parts) < 2:
            return "Please specify: 'FROM_CITY TO_CITY' e.g. 'Mumbai London'"

        # Build search query for Google Flights via SERP
        from_city = parts[0]
        to_city   = parts[1]
        date      = parts[2] if len(parts) > 2 else ""

        search_query = f"flights from {from_city} to {to_city} {date} price"

        params = {
            "engine"  : "google",
            "q"       : search_query,
            "api_key" : SERP_API_KEY,
            "num"     : 5
        }

        search   = GoogleSearch(params)
        results  = search.get_dict()

        # Extract useful flight info from results
        output = f"✈️ Flight Search: {from_city} → {to_city}\n"
        output += "=" * 40 + "\n"

        # Try to get answer box or knowledge panel
        if "answer_box" in results:
            output += f"📌 {results['answer_box'].get('answer', '')[:300]}\n\n"

        # Get organic search results
        if "organic_results" in results:
            for i, result in enumerate(results["organic_results"][:4], 1):
                title   = result.get("title", "")[:80]
                snippet = result.get("snippet", "")[:200]
                link    = result.get("link", "")
                output += f"{i}. {title}\n   {snippet}\n   🔗 {link}\n\n"

        # Add booking tips
        output += """
💡 Flight Booking Tips:
   • Compare prices on: Google Flights, Skyscanner, MakeMyTrip
   • Book 6-8 weeks in advance for best prices
   • Try flexible dates (±3 days) to find cheaper fares
   • Consider nearby airports for better deals
   • Set price alerts on Google Flights!
        """
        return output

    except Exception as e:
        # Fallback response with general flight advice
        return f"""
✈️ Flight Search for '{query}':
Unable to fetch live results ({str(e)[:50]})

📱 Book your flights on these platforms:
   • Google Flights: flights.google.com
   • Skyscanner: skyscanner.com
   • MakeMyTrip: makemytrip.com (India)
   • Kayak: kayak.com

💡 Pro Tips:
   • Best days to fly: Tuesday/Wednesday (usually cheaper)
   • Book 6-8 weeks ahead for international, 2-4 weeks for domestic
   • Enable price alerts for your route
        """

# Test it
print("🧪 Testing Flight Search...")
print(search_flights.invoke("Mumbai London"))

# ============================================================
# TOOL 4: HOTEL SEARCH (SERP API - Google Hotels)
# ============================================================

@tool
def search_hotels(query: str) -> str:
    """
    Search for hotel recommendations in a city.
    Use when user asks about accommodation, hotels, hostels, or places to stay.
    Input format: 'CITY BUDGET_LEVEL' e.g. 'Paris budget' or 'Tokyo luxury' or just 'Bali'
    Budget levels: budget, mid-range, luxury
    """
    try:
        parts        = query.strip().split()
        city         = parts[0] if parts else "Unknown"
        budget_level = parts[1].lower() if len(parts) > 1 else "mid-range"

        search_query = f"best {budget_level} hotels in {city} booking.com"

        params = {
            "engine"  : "google",
            "q"       : search_query,
            "api_key" : SERP_API_KEY,
            "num"     : 5
        }

        search  = GoogleSearch(params)
        results = search.get_dict()

        output = f"🏨 Hotel Search: {city} ({budget_level})\n"
        output += "=" * 40 + "\n"

        if "organic_results" in results:
            for i, result in enumerate(results["organic_results"][:4], 1):
                title   = result.get("title", "")[:80]
                snippet = result.get("snippet", "")[:200]
                output += f"{i}. {title}\n   {snippet}\n\n"

        # Price estimates based on budget level
        price_ranges = {
            "budget"    : "$10-40/night (hostels, guesthouses)",
            "mid-range" : "$50-120/night (3-star hotels)",
            "luxury"    : "$150-500+/night (4-5 star hotels)"
        }
        price_range = price_ranges.get(budget_level, price_ranges["mid-range"])

        output += f"""
💰 Typical Price Range ({budget_level}): {price_range}

📱 Where to Book:
   • Booking.com – booking.com (best for hotels)
   • Airbnb – airbnb.com (apartments/homes)
   • Hostelworld – hostelworld.com (budget/hostels)
   • MakeMyTrip – makemytrip.com (India focused)

💡 Hotel Tips:
   • Read reviews from last 3 months for accuracy
   • Check cancellation policy before booking
   • Book central locations to save on transport
   • Look for hotels with free breakfast included
        """
        return output

    except Exception as e:
        return f"""
🏨 Hotels in {query}:
Live search unavailable. Here are trusted platforms:
   • Booking.com | Airbnb | Hotels.com
   • Agoda (great for Asia) | MakeMyTrip (India)
   Budget: $15-30/night | Mid-range: $50-120 | Luxury: $150+
        """

# Test it
print("🧪 Testing Hotel Search...")
print(search_hotels.invoke("Bali budget"))

# ============================================================
# TOOL 5: GENERAL TRAVEL WEB SEARCH (SERP API)
# ============================================================

@tool
def search_travel_info(query: str) -> str:
    """
    Search the web for any travel-related information.
    Use for: visa requirements, travel advisories, local attractions, restaurants,
    transportation, cultural tips, events, or any travel topic not covered by other tools.
    Input: any travel question e.g. 'visa requirements for India from USA'
    """
    try:
        params = {
            "engine"  : "google",
            "q"       : f"travel {query} 2024",
            "api_key" : SERP_API_KEY,
            "num"     : 5
        }

        search  = GoogleSearch(params)
        results = search.get_dict()

        output = f"🔍 Travel Info: {query}\n"
        output += "=" * 40 + "\n"

        # Check for featured snippet
        if "answer_box" in results:
            ab = results["answer_box"]
            if "answer" in ab:
                output += f"📌 Quick Answer: {ab['answer'][:400]}\n\n"
            elif "snippet" in ab:
                output += f"📌 Featured Info: {ab['snippet'][:400]}\n\n"

        # Organic results
        if "organic_results" in results:
            for i, result in enumerate(results["organic_results"][:4], 1):
                title   = result.get("title", "")[:80]
                snippet = result.get("snippet", "")[:250]
                link    = result.get("link", "")
                output += f"{i}. **{title}**\n   {snippet}\n   🔗 {link}\n\n"

        return output if len(output) > 60 else f"No specific results found for: {query}"

    except Exception as e:
        return f"Search unavailable for '{query}': {str(e)[:100]}. Please check SERP API key."


# Test it
print("🧪 Testing Web Search Tool...")
print(search_travel_info.invoke("best street food in Japan"))
