from typing import List, Dict, Optional
from groq import Groq
from utils.caption_utils import parse_srt_captions
from .video_processor import VideoProcessor

class EducationalAssistant:
    """
    A class that processes educational videos and generates quiz questions based on content.
    """
    def __init__(self, api_key: str):
        """
        Initialize the Educational Assistant.
        
        Args:
            api_key (str): Groq API key for LLM services
        """
        self.groq_client = Groq(api_key=api_key)
        self.video_processor = VideoProcessor()
        
    def process_video(self, video_source: str, is_youtube: bool = True) -> List[Dict]:
        """
        Process a video and extract segments.
        
        Args:
            video_source (str): URL or path to video
            is_youtube (bool): Whether the source is a YouTube URL
            
        Returns:
            List[Dict]: List of video segments with timestamps and text
        """
        if is_youtube:
            return self.video_processor.process_youtube_video(video_source)
        return self.video_processor.process_video_file(video_source)
    
    def identify_key_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Use LLM to identify important segments in the video.
        
        Args:
            segments (List[Dict]): List of video segments
            
        Returns:
            List[Dict]: List of key segments with analysis
        """
        full_text = " ".join(segment['text'] for segment in segments)
        
        prompt = """Analyze this video transcript and identify the most important segments or topics. 
        For each important segment, provide:
        1. A brief title for the segment
        2. The key points or main ideas discussed
        3. Why this segment is important for learning
        
        Format your response as:
        SEGMENT: [title]
        KEY POINTS: [bullet points of main ideas]
        IMPORTANCE: [why this matters]
        
        Transcript:
        {text}
        """
        
        completion = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt.format(text=full_text)}],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
        )
        
        analysis = completion.choices[0].message.content
        return self._match_segments_to_timestamps(analysis, segments)
    
    def generate_questions(self, segment: Dict, grade: int, num_questions: int = 3) -> str:
        """
        Generate quiz questions for a video segment.
        
        Args:
            segment (Dict): Video segment with analysis
            grade (int): Target grade level
            num_questions (int): Number of questions to generate
            
        Returns:
            str: Generated questions and answers
        """
        prompt = f"""Based on this video segment titled "{segment['title']}", generate {num_questions} quiz questions.
        Consider the following analysis of the segment:
        {segment['analysis']}
        
        Generate questions that test understanding of the key concepts for a grade {grade} student.
        Format each question as:
        Q: [question]
        A: [answer]
        
        Content: {segment['text']}
        Generate questions only based on the content of the segment, do not make up any questions.
        """
        
        completion = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
        )
        
        return completion.choices[0].message.content
    
    def _match_segments_to_timestamps(self, analysis: str, original_segments: List[Dict]) -> List[Dict]:
        """Match LLM-identified segments with video timestamps."""
        llm_segments = analysis.split('SEGMENT:')[1:]
        key_segments = []
        
        for llm_segment in llm_segments:
            lines = llm_segment.strip().split('\n')
            title = lines[0].strip()
            
            for segment in original_segments:
                if any(keyword.lower() in segment['text'].lower() 
                      for keyword in title.split()):
                    key_segments.append({
                        'start': segment['start'],
                        'end': segment['end'],
                        'title': title,
                        'text': segment['text'],
                        'analysis': llm_segment.strip()
                    })
                    break
        
        return key_segments 