import gradio as gr

# Define the function to toggle visibility
def toggle_visibility(show):
    if show:
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)

# Create the Gradio interface
with gr.Blocks() as demo:
    # Add components
    textbox = gr.Textbox(label="Enter something:", visible=True)  # Initially visible
    toggle_button = gr.Button("Toggle Visibility")
    
    # Add an event listener to the button
    toggle_button.click(toggle_visibility, inputs=[textbox.visible], outputs=[textbox])

# Launch the app
demo.launch()
