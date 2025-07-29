import gradio as gr
import os
from rag_pipeline import answer_query

def chat_with_assistant(user_input, history):
    response = answer_query(user_input)
    if hasattr(response, "message"):
        answer_text = response.message.content
    elif isinstance(response, dict) and "message" in response:
        answer_text = response["message"]["content"]
    else:
        answer_text = str(response)

    history = history or []
    history.append((user_input, answer_text))
    return history, history

with gr.Blocks() as demo:
    gr.Markdown("AI Music Assistant")
    chat_history = gr.Chatbot()
    user_input = gr.Textbox(placeholder="Ask me about music production...")
    submit_btn = gr.Button("Send")

    submit_btn.click(chat_with_assistant,
                     inputs=[user_input, chat_history],
                     outputs=[chat_history, chat_history])
    user_input.submit(chat_with_assistant,
                      inputs=[user_input, chat_history],
                      outputs=[chat_history, chat_history])

host = os.environ.get("GRADIO_HOST", "127.0.0.1") # Before it runs, it looks for an env var in Docker 
port = int(os.environ.get("GRADIO_PORT", 7860))   # It will grab that env var if it exists, otherwise will default to parameter on the right

demo.launch(server_name=host, server_port=port)

