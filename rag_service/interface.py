import gradio as gr
import requests

API_URL = "http://backend:8000/query"  # service name in docker-compose

def convert_to_backend_format(gradio_history):
    formatted_history = []
    
    # Group consecutive user/assistant pairs
    i = 0
    while i < len(gradio_history):
        if (i + 1 < len(gradio_history) and 
            gradio_history[i]["role"] == "user" and 
            gradio_history[i+1]["role"] == "assistant"):
            
            formatted_history.append({
                "question": gradio_history[i]["content"],    # user message
                "answer": gradio_history[i+1]["content"]     # assistant message
            })
            i += 2
        else:
            i += 1
    
    return formatted_history

def chat(message, history):
    # Convert Gradio's history format to backend's expected format
    formatted_history = convert_to_backend_format(history)
    payload = {
        "message": message,
        "history": formatted_history
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Append the new exchange to history
            history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": data["response"]}
            ]
            return history, ""
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_msg})
            return history, ""
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return history, ""

def clear_chat():
    return [], ""

# Create the Gradio interface
with gr.Blocks(title="RAG Chat Interface") as demo:
    gr.Markdown("# RAG Chat Interface")
    gr.Markdown("Ask questions and get answers based on your knowledge base.")
    
    chatbot = gr.Chatbot(
        label="Chat History",
        height=500,
        show_label=True,
        type="messages"
    )
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Type your question here...",
            label="Message",
            scale=4
        )
        submit_btn = gr.Button("Send", scale=2, variant="primary")
    
    with gr.Row():
        clear_btn = gr.Button("Clear Chat", variant="secondary")
    
    # Event handlers & Buttons
    msg.submit(
        fn=chat, 
        inputs=[msg, chatbot], 
        outputs=[chatbot, msg]
    )
    
    submit_btn.click(
        fn=chat, 
        inputs=[msg, chatbot], 
        outputs=[chatbot, msg]
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, msg]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860, 
        share=False,
        show_error=True,
        inbrowser=True
    )