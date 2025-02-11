import os
from dotenv import load_dotenv
from assistant.educational_assistant import EducationalAssistant

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize assistant
    assistant = EducationalAssistant(api_key=os.getenv("GROQ_API_KEY"))
    
    # Process YouTube video
    video_url = "https://www.youtube.com/watch?v=D1Ymc311XS8"
    segments = assistant.process_video(video_url, is_youtube=True)
    
    if segments:
        # Get key segments
        key_segments = assistant.identify_key_segments(segments)
        
        # Generate questions for each segment
        grade = 2
        num_questions = 3
        
        for i, segment in enumerate(key_segments, 1):
            print(f"\nSegment {i}: {segment['title']}")
            print(f"Timestamp: {segment['start']:.1f}s - {segment['end']:.1f}s")
            print("Analysis:")
            print(segment['analysis'])
            print("\nQuestions:")
            questions = assistant.generate_questions(segment, grade, num_questions)
            print(questions)

if __name__ == "__main__":
    main() 