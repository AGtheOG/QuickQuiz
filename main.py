from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()

# Mount static directory for CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates folder
templates = Jinja2Templates(directory="templates")

# Gemini AI setup (replace with your valid API key)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate_quiz(request: Request, topic: str = Form(...), difficulty: str = Form(...), num_questions: int = Form(...)):
    print("🔥 /generate endpoint called")
    try:

        prompt = f"""
            Generate a JSON array of {num_questions} multiple-choice questions about {topic} of {difficulty} difficulty level.
            Each object should be like this:

            {{
            "question": "Question text?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "A"
            }}
            also mind correct option is option choice not answer
            ⚠️ Return ONLY the JSON array. No explanation, no extra text. ⚠️
            """

        response = model.generate_content(prompt)
        quiz_data = response.text
        clean_json_str = quiz_data[7:-3]
        print("Raw AI response:", clean_json_str)
        import json
        quiz_json = json.loads(clean_json_str)


        return templates.TemplateResponse("quiz.html", {"request": request, "quiz": quiz_json})

    except Exception as e:
        print(f"An error occurred: {e}")
        return templates.TemplateResponse("quiz.html", {"request": request, "quiz": {"error": str(e)}})
    # uvicorn main:app --reload
    

