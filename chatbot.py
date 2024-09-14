import google.generativeai as genai
import gradio as gr

API_KEY = "AIzaSyBsDHFv1oyRJixsmXAwzqR-tlhcuVx5siE"  # Replace with your Gemini API key
genai.configure(api_key=API_KEY)  # Configure the API key

def query_gemini(prompt, history):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"You are a medical assistant. Response as if you are a chatbot for doctors. Your name is MedicBot: {prompt}")
    return response.text

# Create the Gradio interface
iface = gr.ChatInterface(
    fn=query_gemini,
    title="MedicBot Chatbot",
    description="Ask your medical queries"
)

# Launch the interface
iface.launch(server_name="0.0.0.0", server_port=7860, share=False)  # Port must match in Flask
