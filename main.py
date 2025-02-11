from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import re
import os
from dotenv import load_dotenv
from src.assistant.educational_assistant import EducationalAssistant

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize the educational assistant
assistant = EducationalAssistant(api_key=os.getenv("GROQ_API_KEY"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

class VideoRequest(BaseModel):
    video_url: str
    grade_level: int
    num_questions: int

def extract_video_id(url):
    # Extract video ID from YouTube URL
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if video_id_match:
        return video_id_match.group(1)
    return None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process_video(video_request: VideoRequest):
    try:
        video_url = video_request.video_url
        print(f"Processing video URL: {video_url}")
        
        video_id = extract_video_id(video_url)
        print(f"Extracted video ID: {video_id}")
        
        # Process video using your educational assistant
        print("Starting video processing...")
        segments = assistant.process_video(video_url, is_youtube=True)
        print(f"Got segments: {len(segments) if segments else 0}")
        
        questions_data = []
        
        if segments:
            # Get key segments
            print("Identifying key segments...")
            key_segments = assistant.identify_key_segments(segments)
            print(f"Found {len(key_segments)} key segments")
            
            # Use the user-provided grade level and number of questions
            grade = video_request.grade_level
            num_questions = video_request.num_questions
            
            for i, segment in enumerate(key_segments):
                print(f"\nProcessing segment {i+1}:")
                print(f"Segment start time: {segment['start']}")
                print(f"Segment title: {segment.get('title', 'No title')}")
                
                # Generate questions for this segment
                print("Generating questions...")
                segment_questions = assistant.generate_questions(segment, grade, num_questions)
                print(f"Raw questions output: {segment_questions}")
                
                if isinstance(segment_questions, str):
                    # Handle string format
                    questions_list = segment_questions.split('\n\n')
                    for q_text in questions_list:
                        if q_text.strip():
                            parts = q_text.split('\nAnswer: ')
                            if len(parts) == 2:
                                question = parts[0].replace('Question: ', '').strip()
                                answer = parts[1].strip()
                                questions_data.append({
                                    "timestamp": segment["start"],
                                    "question": question,
                                    "answer": answer
                                })
                elif isinstance(segment_questions, list):
                    # Handle list format
                    for q in segment_questions:
                        questions_data.append({
                            "timestamp": segment["start"],
                            "question": q.get("question", ""),
                            "answer": q.get("answer", "")
                        })
                else:
                    print(f"Unexpected question format: {type(segment_questions)}")
        
        print(f"\nFinal questions data: {questions_data}")
        return {
            "video_id": video_id,
            "questions": questions_data
        }
        
    except Exception as e:
        print(f"Error in process_video: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return some mock questions for testing
        return {
            "video_id": video_id if 'video_id' in locals() else None,
            "questions": [
                {
                    "timestamp": 30,
                    "question": "Test Question 1?",
                    "answer": "Test Answer 1"
                },
                {
                    "timestamp": 60,
                    "question": "Test Question 2?",
                    "answer": "Test Answer 2"
                }
            ]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 