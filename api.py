from fastapi import FastAPI
from google import genai
from pydantic import BaseModel
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Review Analysis Project!"}

class Review(BaseModel):
    text: str
    
class AnalysisResult(BaseModel):
    label: str # "positive", "negative", or "neutral"
    score: int # 1 (very bad) to 5 (very good)
    theme: str # one word: what the review is mainly about (e.g. "delivery")

@app.post("/analyze_review")
def analyze_review(review: Review):
    
    response = client.models.generate_content(
        model = "gemini-3.1-flash-lite",
        
        contents=(
        "Analyze this customer review. \n"
        "label must be 'positive', 'negative', or 'neutral'. \n"
        "score must be a number from 1 (very bad) to 5 (very good). \n"
        "theme must be ONE lowercase word for the main topic "
        "(for example: delivery, taste, price, service, quality). \n"
        f"Review: {review.text}"
        ),
        
        config = types.GenerateContentConfig(
            response_mime_type = "application/json",
            response_schema = AnalysisResult
        )
    
    )
    
    return response.parsed