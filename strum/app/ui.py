import gradio as gr
import os
from rag_pipeline import answer_query

def chat_with_assistant(user_input, history):
    # history is just an array of tuples
    response = answer_query(user_input, history)
    
    if hasattr(response, "message"):
        answer_text = response.message.content
    elif isinstance(response, dict) and "message" in response:
        answer_text = response["message"]["content"]
    else:
        answer_text = str(response)

    history = history or [] # creates history here if it doesn't already exist
                            # it will then pass it around all the different functions 
    history.append((user_input, answer_text))
    return history, ""

with gr.Blocks() as demo:
    # UI Elements
    gr.Markdown("Strum")
    # Chat History takes an array of tuples representing your input and
    # the response of the AI and displays them
    chat_history = gr.Chatbot()
    user_input = gr.Textbox(placeholder="Ask me about music production...")
    submit_btn = gr.Button("Send")

    # These both accomplish the same thing, just through different mediums
    submit_btn.click(chat_with_assistant,
                     inputs=[user_input, chat_history],    # values that go into the function
                     outputs=[chat_history, user_input])   # values that are updated upon return from the function
    user_input.submit(chat_with_assistant,
                      inputs=[user_input, chat_history],
                      outputs=[chat_history, user_input])

host = os.environ.get("GRADIO_HOST", "127.0.0.1") # Before it runs, it looks for an env var in Docker 
port = int(os.environ.get("GRADIO_PORT", 7860))   # It will grab that env var if it exists, otherwise will default to parameter on the right

demo.launch(server_name=host, server_port=port)

