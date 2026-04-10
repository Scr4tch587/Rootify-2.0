from youtube_transcript_api import YouTubeTranscriptApi, FetchedTranscript


def fetch_youtube_transcript(video_id: str) -> FetchedTranscript | None:
    ytt_api = YouTubeTranscriptApi()
    try:
        return ytt_api.fetch(video_id)
    except Exception:
        return None
