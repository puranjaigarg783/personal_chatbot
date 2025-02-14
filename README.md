# Personal AI Assistant

A Streamlit-based chatbot that uses Anthropic's Claude API to process and discuss PDFs and images.

## Features
- PDF document processing
- Image upload and analysis
- Interactive chat interface
- Powered by Claude-3 Opus model

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```
Then edit `.env` and add your Anthropic API key.

3. Run the application:
```bash
streamlit run app.py
```

## Usage
1. Upload a PDF or image using the sidebar
2. Chat with the AI about the uploaded content
3. Ask questions and get detailed responses

## Requirements
- Python 3.8+
- Anthropic API key