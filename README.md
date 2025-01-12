# Static Chatbot

A Python-based chatbot application designed for quick and accurate responses for API docs using a local database and efficient data handling.

## Idea

- Loaded the data from the notion pages using notion APIs with markdowns and saved it inside the text file.
- Loaded the data from text file and created chunks using the `MarkdownHeaderTextSplitter` and `RecursiveCharacterTextSplitter` and created embeddings using the `Cohere's` `embed-english-v3.0` model and stored it in `ChromaDB`.
- Check `data_loader.py` and `data_puller.py` for pulling the data from notion and loading the data into Vector database.
- The approach is `Reliable RAG`, used LLMs to validate the `context relevence` of fetched data from the vector database and also check the `groundedness` of the LLM generated output and define the `hellucination`.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd static_chatbot
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env`.

### Running the Application

Run the chatbot:
```bash
streamlit run app.py
```

## Project Structure

```
static_chatbot/
|-- app.py               # Main application entry point
|-- requirements.txt     # Python dependencies
|-- data_loader.py       # Data loading functionality
|-- data_puller.py       # Data fetching from external APIs
|-- constants.py         # Project-wide constants
|-- utils.py             # Utility functions
|-- chroma.sqlite3       # SQLite database
|-- .env                 # Environment variables
|-- .gitignore           # Git ignore file
```
