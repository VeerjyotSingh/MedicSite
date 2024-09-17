import os

try:
  # Import libraries (assuming they are installed)
  import google.generativeai as genai
  import gradio as gr
except ModuleNotFoundError as e:
  print(f"Error: Required libraries not found. Please install them using 'pip install google-generativeai gradio'.")
  exit(1)  # Exit with an error code if libraries are missing

# Retrieve Gemini API key from environment variable
API_KEY = os.getenv("Gemini")

if not API_KEY:
  print("Error: Gemini API key not found. Please set the 'Gemini' environment variable with your API key.")
  exit(1)  # Exit with an error code if API key is missing

# Configure the API key
genai.configure(api_key=API_KEY)


def query_gemini(prompt, history):
  try:
    # Use the 'gemini-1.5-flash' model (replace if different)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        f"You are a medical assistant. Response as if you are a chatbot for doctors. Your name is MedicBot: {prompt}")

    # Check for valid response and access content
    if response and hasattr(response, 'candidates') and response.candidates:
      candidate = response.candidates[0]
      text = candidate.content.parts[0].text
      return text
    else:
      return "No valid response received."
  except Exception as e:
    print("Error occurred while checking Gemini:", e)
    return "An error occurred while processing your request."


# Create the Gradio interface
iface = gr.ChatInterface(
    fn=query_gemini,
    title="MedicBot Chatbot",
    description="Ask your medical queries",
    # Add other interface customization options as needed
)

# Launch the interface (adjust port as needed)
iface.launch(server_name="0.0.0.0", server_port=7860, share=False)