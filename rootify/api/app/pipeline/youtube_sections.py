from app.pipeline.youtube_fetch import fetch_youtube_transcript
from typing import List, Dict

def fetch_youtube_sections(video_id: str) -> List[Dict[str, str]]:
    youtube_transcript = fetch_youtube_transcript(video_id)
    sections = []
    section_counter = 0
    text = ""
    start_time = None
    first_chunk = True
    for snippet in youtube_transcript:
        if first_chunk:
            first_chunk = False
            start_time = snippet.start
        text += snippet.text + " "
        section_counter += 1
        if section_counter == 10:
            sections.append({
                "keyword": None,
                "section_path": "youtube-" + video_id + "-" + str(start_time) + "-" + str(snippet.start),
                "text": text.strip()
            })
            text = ""
            first_chunk = True
            section_counter = 0
    if section_counter > 0:
        sections.append({
            "keyword": None,
            "section_path": "youtube-" + video_id + "-" + str(start_time) + "-" + str(snippet.start),
            "text": text.strip()
        })
    return sections
