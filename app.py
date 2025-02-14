import streamlit as st
from PIL import Image
import PyPDF2
import io
import os
import base64
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def process_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def process_image(image_file):
    image = Image.open(image_file)
    # Convert image to RGB if it's not
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"<image>{img_str}</image>"

def get_chat_response(messages, file_content=None):
    # Convert messages to the format expected by Claude
    api_messages = []
    
    # If there's file content, add it as system message
    if file_content:
        if file_content.startswith("<image>"):
            api_messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": file_content[7:-8]  # Remove <image> tags
                        }
                    },
                    {
                        "type": "text",
                        "text": "This is the uploaded image. Please analyze it when answering questions."
                    }
                ]
            })
        else:
            api_messages.append({
                "role": "user",
                "content": f"Here's the content of the uploaded PDF:\n\n{file_content}\n\nPlease use this content when answering questions."
            })
    
    # Add the rest of the conversation
    for msg in messages:
        role = "assistant" if msg["role"] == "assistant" else "user"
        api_messages.append({
            "role": role,
            "content": msg["content"]
        })
    
    with st.spinner('AI is thinking...'):
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=api_messages,
            temperature=0.7,
        )
        return response.content[0].text

def main():
    st.set_page_config(page_title="Personal AI Assistant", layout="wide")
    
    st.title("Personal AI Assistant")
    
    # Initialize session state for chat history and file content
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "file_content" not in st.session_state:
        st.session_state.file_content = None

    # File upload section
    st.sidebar.header("Upload Files")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF or Image file", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            with st.spinner('Processing PDF...'):
                st.session_state.file_content = process_pdf(uploaded_file)
                st.sidebar.success("PDF processed successfully!")
        elif uploaded_file.type.startswith("image"):
            with st.spinner('Processing Image...'):
                st.session_state.file_content = process_image(uploaded_file)
                # Display the original image in the sidebar
                image = Image.open(uploaded_file)
                st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)
                st.sidebar.success("Image processed successfully!")

        if len(st.session_state.messages) == 0:
            system_message = {
                "role": "assistant",
                "content": f"I've processed your file. What would you like to know about it?"
            }
            st.session_state.messages.append(system_message)

    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat history
        user_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(user_message)
        
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        try:
            # Get AI response with spinner
            ai_response = get_chat_response(st.session_state.messages, st.session_state.file_content)
            assistant_message = {"role": "assistant", "content": ai_response}
            st.session_state.messages.append(assistant_message)
            
            # Show AI response immediately
            with st.chat_message("assistant"):
                st.write(ai_response)
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()