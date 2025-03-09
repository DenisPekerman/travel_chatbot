import os
import openai
import gradio as gr
from dotenv import load_dotenv

# Load environment variables from the .env file (ensure this file is secure)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def travel_agent_chat(user_message, history):
    if history is None:
        history = []

    # System prompt to set the travel agent personality and guidelines
    system_message = (
        "You are a knowledgeable and friendly travel agent. "
        "Provide expert travel advice, including recommendations on destinations, itineraries, flights, hotels, and local experiences. "
        "If the user asks questions unrelated to travel, politely state that you only provide travel-related information."
    )

    # Build the conversation messages for OpenAI
    messages = [{"role": "system", "content": system_message}]
    for user_text, bot_text in history:
        messages.append({"role": "user", "content": user_text})
        messages.append({"role": "assistant", "content": bot_text})
    messages.append({"role": "user", "content": user_message})

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        bot_message = response.choices[0].message.content.strip()
    except Exception as e:
        bot_message = f"Error during API call: {str(e)}"
    
    history.append((user_message, bot_message))
    return history

def respond(user_message, history):
    # Update conversation history with the latest user message and response
    history = travel_agent_chat(user_message, history)
    # Return empty string for clearing the input and the updated conversation history
    return "", history, history

with gr.Blocks() as demo:
    gr.Markdown("# Travel Agent Chatbot Demo")
    gr.Markdown(
        "Chat with our travel specialist! Ask for travel advice, destination recommendations, and itinerary ideas. "
        "The conversation history will display both your messages and the agent's responses."
    )
    
    # Chatbot component displays the conversation history
    chatbot = gr.Chatbot(label="Conversation History")
    # Textbox for user input
    msg = gr.Textbox(placeholder="Type your message here...", label="Your Message")
    # State component to hold conversation history
    state = gr.State([])

    # When the user submits a message, update the conversation history
    msg.submit(respond, inputs=[msg, state], outputs=[msg, chatbot, state])

demo.launch(share=True)
