travel_knowledge = [
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
    Southeast Asia (Thailand, Vietnam, Bali) is budget-friendly: $30-60/day including accommodation.
    Western Europe averages $100-200/day for mid-range travel.
    Japan costs $80-150/day; best visited in spring (cherry blossoms) or autumn (fall colors).
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
    India has diverse climates - plan based on region and season.
    North India (Delhi, Agra, Jaipur) Golden Triangle: October-March is ideal.
    Kerala backwaters: November-February is best.
    Goa beaches: November-February (peak season), avoid monsoon June-September.
    Himachal Pradesh and Ladakh: May-September.
    Budget: Rs.2000-5000/day for mid-range domestic travel.
    Book trains on IRCTC at least 2-3 months in advance.
    """,
    """
    FLIGHT BOOKING TIPS:
    Best days to book: Tuesday and Wednesday for cheaper fares.
    Use Google Flights, Skyscanner, or Kayak to compare prices.
    Flexible date search can save 20-40% on airfare.
    Consider nearby airports for cheaper options.
    Budget airlines: IndiGo, SpiceJet (India), Ryanair (Europe), AirAsia (Asia).
    Always check baggage allowance before booking.
    """,
    """
    HOTEL BOOKING TIPS:
    Book directly with hotels for better rates and flexibility.
    Compare on Booking.com, Airbnb, Hotels.com, MakeMyTrip.
    Hostels are great for solo travelers ($10-25/night).
    Mid-range hotels: $40-100/night globally.
    Check cancellation policies, especially for long trips.
    Location matters - staying central saves on transport costs.
    """
]

docs       = [Document(page_content=text) for text in travel_knowledge]
splitter   = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(docs)

print("⏳ Step 3: Loading embeddings (first time ~30 seconds)...")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
vectorstore = FAISS.from_documents(split_docs, embeddings)
retriever   = vectorstore.as_retriever(search_kwargs={"k": 3})
print(f"✅ Step 3: RAG Knowledge base ready with {len(split_docs)} chunks!")


# ============================================================
# BASIC RAG TRAVEL CHATBOT - FINAL FIXED VERSION
# ============================================================
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

TRAVEL_PROMPT_TEMPLATE = """
You are an expert AI Travel Concierge with deep knowledge about travel worldwide.
You are friendly, helpful, and provide practical, actionable travel advice.

Use the following travel knowledge to answer the question:
{context}

Question: {question}

Instructions:
- Be specific and helpful
- Include practical tips when relevant
- Mention costs/budgets when relevant
- If you don't know something specific, say so and give general advice
- Keep response concise but complete

Answer:
"""

TRAVEL_PROMPT = PromptTemplate(
    template=TRAVEL_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Build RAG chain
travel_qa_chain = (
    {
        "context" : retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | TRAVEL_PROMPT
    | llm
    | StrOutputParser()
)

def basic_travel_chat(question: str) -> str:
    try:
        return travel_qa_chain.invoke(question)
    except Exception as e:
        return f"Error: {str(e)}"

# Test
print("🧪 Testing the basic travel chatbot...\n")
test_questions = [
    "What's the best time to visit Bali?",
    "Give me budget tips for Southeast Asia travel",
    "What documents do I need for international travel?"
]

for q in test_questions:
    print(f"❓ Q: {q}")
    print(f"🤖 A: {basic_travel_chat(q)}")
    print("-" * 60)
