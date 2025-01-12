# Static Chatbot

A Python-based chatbot application designed for quick and accurate responses for API docs using a local database and efficient data handling.

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
