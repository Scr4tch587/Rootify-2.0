from youtube_transcript_api import YouTubeTranscriptApi, FetchedTranscript

def fetch_youtube_transcript(video_id: str) -> FetchedTranscript:
    ytt_api = YouTubeTranscriptApi()
    return ytt_api.fetch(video_id)