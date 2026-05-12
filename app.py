import gradio as gr, httpx, uuid

BASE_URL = "http://localhost:8000"

def send_message(input_text, thread_id):
    try:
        response = httpx.post(f"{BASE_URL}/chat", json={"thread_id": thread_id, "message": input_text}, timeout=60.0)
        status =  response.json().get("status", "")
        if status == "success":
            response_text = response.json().get("response", "")
            return response_text, gr.update(visible = False), gr.update(visible = False)
        elif status == "interrupted":
            return response.json().get("message", ""), gr.update(visible = True), gr.update(visible = True)
        else:
            return response.json().get("error", ""), gr.update(visible = False), gr.update(visible = False) 
    except httpx.RequestError as e:
        return "An error occurred while processing your request.", gr.update(visible = False), gr.update(visible = False) 

def handle_approve(thread_id):
    try:
        response = httpx.post(f"{BASE_URL}/chat/resume", json={"thread_id": thread_id, "approved": True}, timeout=60.0)
        status =  response.json().get("status", "")
        if status == "success":
            response_text = response.json().get("response", "")
            return response_text, gr.update(visible = False), gr.update(visible = False)
        elif status == "interrupted":
            return response.json().get("message", ""), gr.update(visible = True), gr.update(visible = True)
        else:
            return response.json().get("error", ""), gr.update(visible = False), gr.update(visible = False) 
    except httpx.RequestError as e:
        return "An error occurred while processing your request.", gr.update(visible = False), gr.update(visible = False)

def handle_deny(thread_id):
    try:
        response = httpx.post(f"{BASE_URL}/chat/resume", json={"thread_id": thread_id, "approved": False}, timeout=60.0)
        status =  response.json().get("status", "")
        if status == "success":
            response_text = response.json().get("response", "")
            return response_text, gr.update(visible = False), gr.update(visible = False)
        elif status == "interrupted":
            return response.json().get("message", ""), gr.update(visible = True), gr.update(visible = True)
        else:
            return response.json().get("error", ""), gr.update(visible = False), gr.update(visible = False) 
    except httpx.RequestError as e:
        return "An error occurred while processing your request.", gr.update(visible = False), gr.update(visible = False)

with gr.Blocks() as demo:
    thread_id = gr.State(str(uuid.uuid4())) 
    user_input = gr.Textbox(label="Your message")
    send_btn = gr.Button("Send")
    output = gr.Textbox("Output", interactive=False)
    approve_btn = gr.Button("Approve", visible = False)
    deny_btn = gr.Button("Deny", visible = False)
    send_btn.click(fn = send_message, inputs=[user_input, thread_id], outputs=[output, approve_btn, deny_btn])
    approve_btn.click(fn=handle_approve, inputs=[thread_id], outputs=[output, approve_btn, deny_btn])
    deny_btn.click(fn=handle_deny, inputs=[thread_id], outputs=[output, approve_btn, deny_btn])



if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)