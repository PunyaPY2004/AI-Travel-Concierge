# ============================================================
# GRADIO CHAT INTERFACE
# ============================================================
import gradio as gr

# Chat history storage
chat_history = []

def chat_with_concierge(user_message, history):
    """Handle a chat message and return response."""
    if not user_message.strip():
        return "", history

    # Get response from our RAG chatbot
    bot_response = basic_travel_chat(user_message)

    # Add to history
    history.append((user_message, bot_response))
    return "", history

# Create the Gradio interface
with gr.Blocks(title="AI Travel Concierge", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""# ✈️ AI Travel Concierge
    ### Your intelligent travel planning assistant powered by Gemini AI
    Ask me anything about travel destinations, flights, hotels, budgets, and more!
    """)

    chatbot = gr.Chatbot(
        value=[(None, "👋 Hello! I'm your AI Travel Concierge. I can help you plan trips, suggest destinations, estimate budgets, and more. Where would you like to go?")],
        height=450,
        label="Travel Assistant"
    )

    with gr.Row():
        msg_input = gr.Textbox(
            placeholder="e.g. Plan a 7-day trip to Japan for 2 people...",
            label="Your question",
            scale=4
        )
        send_btn = gr.Button("Send ✈️", scale=1, variant="primary")

    # Sample question buttons
    gr.Markdown("**💡 Try these:**")
    with gr.Row():
        gr.Button("Best time to visit Bali?").click(
            lambda: "Best time to visit Bali?", outputs=msg_input
        )
        gr.Button("Budget for 7 days in Thailand?").click(
            lambda: "What's the budget for 7 days in Thailand?", outputs=msg_input
        )
        gr.Button("India trip packing list").click(
            lambda: "Give me a packing list for India trip", outputs=msg_input
        )

    # Connect buttons to chat function
    send_btn.click(chat_with_concierge, [msg_input, chatbot], [msg_input, chatbot])
    msg_input.submit(chat_with_concierge, [msg_input, chatbot], [msg_input, chatbot])

# Launch the interface
# share=True creates a public link you can share (valid for 72 hours)
demo.launch(share=True, debug=False)
print("\n🔗 Your Travel Concierge UI is live! Click the link above.")

# ============================================================
# GRADIO CHAT UI FOR THE AGENT
# ============================================================
import gradio as gr

def agent_chat(user_message, history):
    """Chat function that uses the full agent."""
    if not user_message.strip():
        return "", history

    try:
        result    = agent_executor.invoke({"input": user_message})
        response  = result["output"]
    except Exception as e:
        response = f"I encountered an error: {str(e)}. Please try rephrasing your question."

    history.append((user_message, response))
    return "", history


with gr.Blocks(title="AI Travel Concierge", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""# ✈️ AI Travel Concierge - Full Agent
    ### Powered by Gemini AI + Real APIs | Weather • Flights • Hotels • Currency
    """)

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                value=[(None, "👋 Hello! I'm your AI Travel Concierge.\n\nI can help you with:\n✈️ Flight searches\n🏨 Hotel recommendations\n🌤️ Weather info\n💱 Currency conversion\n🗺️ Travel tips & itineraries\n\nWhere would you like to travel?")],
                height=500
            )
            with gr.Row():
                msg = gr.Textbox(placeholder="Ask me anything about travel...", scale=4, label="")
                btn = gr.Button("Send ✈️", scale=1, variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### 💡 Quick Questions")
            sample_qs = [
                "Weather in Bali right now?",
                "Flights from Mumbai to Dubai",
                "Budget hotels in Bangkok",
                "Convert 500 USD to Thai Baht",
                "Visa requirements for Japan",
                "Best time to visit Europe"
            ]
            for q in sample_qs:
                gr.Button(q, size="sm").click(lambda x=q: x, outputs=msg)

    btn.click(agent_chat, [msg, chatbot], [msg, chatbot])
    msg.submit(agent_chat, [msg, chatbot], [msg, chatbot])

demo.launch(share=True, debug=False)
print("\n🔗 Full Agent UI is live!")
