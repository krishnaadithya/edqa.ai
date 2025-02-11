from typing import List, Dict

def timestamp_to_seconds(timestamp: str) -> float:
    """
    Convert SRT timestamp to seconds.
    
    Args:
        timestamp (str): Timestamp in SRT format (HH:MM:SS,mmm)
        
    Returns:
        float: Time in seconds
    """
    if ',' in timestamp:
        timestamp = timestamp.replace(',', '.')

    parts = timestamp.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    return 0

def parse_srt_captions(srt_captions: str) -> List[Dict]:
    """
    Parse SRT format captions into segments.
    
    Args:
        srt_captions (str): Raw SRT caption text
        
    Returns:
        List[Dict]: List of segments with timestamps and text
    """
    segments = []
    current_segment = {}

    for line in srt_captions.split('\n'):
        line = line.strip()

        if line.isdigit():  # Segment number
            if current_segment:
                segments.append(current_segment)
            current_segment = {}
        elif '-->' in line:  # Timestamp
            start, end = line.split('-->')
            current_segment['start'] = timestamp_to_seconds(start.strip())
            current_segment['end'] = timestamp_to_seconds(end.strip())
        elif line:  # Text content
            if 'text' in current_segment:
                current_segment['text'] += ' ' + line
            else:
                current_segment['text'] = line

    if current_segment:
        segments.append(current_segment)

    return segments 