# Customer Feedback Analyzer (Gen AI)

A full-stack AI application that analyzes customer reviews in bulk using Google Gemini (`gemini-3.1-flash-lite`). It features a **FastAPI backend** serving structured Pydantic analysis, an interactive **Streamlit frontend dashboard**, and **SQLite persistence** for storing and viewing review history.

- You can try this app here: [Visit Here](https://customer-review-analyzer-gemini.streamlit.app/)

---

## 📌 Project Overview

**The Problem:** A business owner receives dozens of customer reviews and lacks the time to read through each one manually. They need an automated tool where they can paste batches of reviews, click a button, and immediately identify overall customer sentiment, average satisfaction ratings, and recurring complaints or praise.

**The Solution:**
- **Backend (`api.py`)**: A FastAPI microservice powered by Google GenAI (`gemini-3.1-flash-lite`) that accepts a review and outputs structured data: sentiment label, numerical score (1–5), and a one-word topic theme.
- **Frontend (`app.py`)**: A Streamlit dashboard where users paste multiple reviews, send them concurrently/batch-wise to the backend API, view summary metrics & charts, and save feedback records to a local database.
- **Database (`database.py`)**: SQLite integration (`feedback.db`) to retain historical feedback across sessions.

---

## 📂 Project Structure

```text
project_analyze_reviews/
├── api.py              # FastAPI backend service (Gemini 3.1 Flash Lite)
├── app.py              # Streamlit dashboard frontend
├── database.py         # SQLite database operations (feedback.db)
├── feedback.db         # SQLite database file storing analyzed feedback
├── sample_reviews.txt  # Sample customer reviews for quick testing
├── sample.env          # Template for environment variables
├── pyproject.toml      # Project configuration and dependencies (uv)
├── uv.lock             # Lockfile for reproducible dependencies
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## 🛠️ Tech Stack & Concepts

| Component | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI, Uvicorn | High-performance REST API service |
| **Gen AI** | Google GenAI SDK (`google-genai`), `gemini-3.1-flash-lite` | Structured sentiment and theme extraction |
| **Validation** | Pydantic v2 | Strict schema validation (`Review`, `AnalysisResult`) |
| **Frontend** | Streamlit | Interactive web dashboard and metrics display |
| **HTTP Client** | Requests | Communication between Streamlit frontend and FastAPI backend |
| **Database** | SQLite3 | Persistent storage of analyzed reviews (`feedback.db`) |
| **Environment** | `python-dotenv` | Secure API key management |
| **Package Manager** | `uv` | Fast Python package and virtual environment manager |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) package manager installed

### 2. Navigate to the Project Folder
Open your terminal and ensure you are in the project folder:

```bash
cd project_analyze_reviews
```

### 3. Install Dependencies
Using `uv`, synchronize all dependencies defined in `pyproject.toml`:

```bash
uv sync
```

*(Alternatively, if installing manually: `uv add "fastapi[standard]" google-genai python-dotenv pydantic streamlit requests`)*

### 4. Configure Environment Variables
Create a `.env` file from the provided `sample.env` template:

**On Linux / macOS:**
```bash
cp sample.env .env
```

**On Windows (PowerShell):**
```powershell
Copy-Item sample.env .env
```

**On Windows (Command Prompt):**
```cmd
copy sample.env .env
```

Open `.env` and set your Google Gemini API key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 🖥️ Running the Application

The project runs as a two-tier application. Open **two separate terminals**:

### Terminal 1: Start the FastAPI Backend
```bash
uv run fastapi dev api.py
```
- **Service URL:** `http://127.0.0.1:8000`
- **Interactive API Docs (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative Open/Alternative Docs (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Terminal 2: Start the Streamlit Frontend
```bash
uv run streamlit run app.py
```
- **Dashboard URL:** [http://localhost:8501](http://localhost:8501) (opens automatically in your browser)

---

## 📡 API Reference (`api.py`)

### 1. Root Endpoint
- **URL:** `/`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "message": "Welcome to the Review Analysis Project!"
  }
  ```

### 2. Analyze Review Endpoint
- **URL:** `/analyze_review`
- **Method:** `POST`
- **Request Body (`Review`):**
  ```json
  {
    "text": "The food was delicious but the delivery took over an hour. Not happy."
  }
  ```
- **Response Model (`AnalysisResult`):**
  ```json
  {
    "label": "negative",
    "score": 2,
    "theme": "delivery"
  }
  ```

#### Pydantic Schemas:
```python
class Review(BaseModel):
    text: str

class AnalysisResult(BaseModel):
    label: str  # "positive", "negative", or "neutral"
    score: int  # 1 (very bad) to 5 (very good)
    theme: str  # one lowercase word (e.g., "delivery", "taste", "price", "service", "quality")
```

#### Quick cURL Test:
```bash
curl -X POST "http://127.0.0.1:8000/analyze_review" \
     -H "Content-Type: application/json" \
     -d "{\"text\": \"Amazing taste and the order arrived hot and early. Will order again!\"}"
```

---

## 💻 Frontend Dashboard Guide (`app.py`)

1. **Paste Reviews:** Enter or paste customer reviews in the text box (one review per line). You can copy test reviews directly from `sample_reviews.txt`.
2. **Analyze:** Click the **Analyze** button.
   - The frontend parses lines and calls `http://127.0.0.1:8000/analyze_review` for each review.
   - Fault-tolerant: if any individual review request fails, it records an `"error"` row without crashing the batch.
3. **Inspect Results & Metrics:**
   - **Interactive Table:** View each review alongside its predicted sentiment `label`, numeric `score` (1–5), and `theme`.
   - **Summary Metrics:**
     - **Reviews:** Total count of analyzed reviews.
     - **Average Score:** Average rating across valid reviews (rounded to 1 decimal place).
     - **% Positive:** Proportion of positive reviews out of the total.
     - **Top Topic Banner:** Highlights which topic customers talk about the most (using `collections.Counter`).
4. **Persist to Database:** Click **💾 Save to database** to write the current batch into `feedback.db`.
5. **View Saved History:** Expand the **📚 Saved history (all reviews in the database)** accordion to inspect all feedback accumulated across all sessions.

---

## 🗄️ Database Management (`database.py`)

The SQLite database file is stored at `feedback.db`.

### Table Schema: `feedback`
| Column | Type | Description |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY` | Auto-incrementing review record ID |
| `review` | `TEXT` | Raw customer review text |
| `label` | `TEXT` | Sentiment classification (`positive`, `negative`, `neutral`) |
| `score` | `INTEGER` | Rating from 1 (very bad) to 5 (very good) |
| `theme` | `TEXT` | One-word topic theme (e.g., `delivery`, `taste`, `price`) |

### Core Functions:
- `init_db()`: Creates the `feedback` table if it does not already exist.
- `save_results(results)`: Appends newly analyzed review dictionaries to the database.
- `load_history()`: Queries and returns all historical review records from the database.

---

## 🧪 Testing with Sample Reviews

`sample_reviews.txt` contains 10 realistic customer reviews for quick testing:
- **Delivery:** *"The food was delicious but the delivery took over an hour. Not happy."*
- **Taste & Consistency:** *"The biryani was perfect, exactly like last time. Very consistent."*
- **Pricing:** *"Prices have gone up too much for the same small portion."*
- **Customer Service:** *"Service was rude when I called to ask about my order."*
- **App Usability:** *"The app kept crashing while I was trying to place my order."*

---

## 🔍 Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Frontend shows `"error"` rows | Backend is not running or unreachable | Start the backend first in Terminal 1 with `uv run fastapi dev api.py`. Ensure it is running on `http://127.0.0.1:8000`. |
| 404 Not Found when testing API | Using `/analyze` instead of `/analyze_review` | Ensure your requests target `http://127.0.0.1:8000/analyze_review`. |
| Gemini API error / 403 / Invalid key | Missing or incorrect `GOOGLE_API_KEY` | Create `.env` from `sample.env` and supply a valid Google Gemini API key. |
| Port already in use | Port `8000` or `8501` occupied | Stop any existing processes running on those ports, or pass custom `--port` flags. |

---

## 💡 Future Enhancements

Looking to build further? Consider adding:
1. **Interactive Charts:** Integrate `st.bar_chart` to visualize distribution across sentiment labels and themes.
2. **Sentiment Filtering:** Add a dropdown (`st.selectbox`) to filter the table by sentiment (e.g. view only "negative" reviews).
3. **Direct File Upload:** Add an `st.file_uploader` to upload `.txt` or `.csv` files directly instead of copy-pasting.
4. **Actionable Suggestions:** Extend the Gemini prompt to generate a 1-sentence recommended action for resolving negative feedback.
