from typing import List, Dict
import os
from pytubefix import YouTube
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from utils.caption_utils import parse_srt_captions

class VideoProcessor:
    """Handles video processing and text extraction."""
    
    def process_youtube_video(self, video_url: str) -> List[Dict]:
        """
        Process a YouTube video and extract captions.
        
        Args:
            video_url (str): YouTube video URL
            
        Returns:
            List[Dict]: List of segments with timestamps and text
        """
        yt = YouTube(url=video_url)
        segments = None
        
        # Try auto-generated captions first
        if yt.captions and 'a.en' in yt.captions:
            caption = yt.captions['a.en']
            raw_captions = caption.generate_srt_captions()
            segments = parse_srt_captions(raw_captions)
        # Fall back to manual English captions
        elif yt.captions and 'en' in yt.captions:
            caption = yt.captions['en']
            raw_captions = caption.generate_srt_captions()
            segments = parse_srt_captions(raw_captions)
            
        return segments
    
    def process_video_file(self, video_path: str) -> List[Dict]:
        """
        Process a local video file and extract text.
        
        Args:
            video_path (str): Path to video file
            
        Returns:
            List[Dict]: List of segments with timestamps and text
        """
        video = VideoFileClip(video_path)
        audio = video.audio
        
        audio_path = "temp_audio.wav"
        audio.write_audiofile(audio_path)
        
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        os.remove(audio_path)
        video.close()
        audio.close()
        
        return [{
            'start': 0,
            'end': video.duration,
            'text': text
        }] 