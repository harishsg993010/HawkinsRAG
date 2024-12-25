"""YouTube content loader implementation."""
import hashlib
from typing import Any, Dict, Optional
import logging
from ..utils.base import BaseLoader
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

class YouTubeLoader(BaseLoader):
    """Loader for YouTube videos and channels."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize YouTube loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}
        self.transcript_api = None
        self.youtube = None
        self._initialize_apis()

    def _initialize_apis(self) -> None:
        """Initialize required APIs with proper error handling."""
        # Initialize transcript API
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            self.transcript_api = YouTubeTranscriptApi
            logger.info("YouTube transcript API initialized successfully")
        except ImportError:
            logger.error("youtube_transcript_api not installed")
            raise ImportError(
                "YouTube transcript API required. Install with: "
                "pip install youtube-transcript-api"
            )

        # Initialize YouTube Data API
        try:
            from googleapiclient.discovery import build
            api_key = self.config.get("api_key")
            if not api_key:
                logger.error("No YouTube API key provided in configuration")
                raise ValueError("YouTube API key required in config")

            self.youtube = build('youtube', 'v3', developerKey=api_key)
            logger.info("YouTube Data API initialized successfully")
        except ImportError:
            logger.error("google-api-python-client not installed")
            raise ImportError(
                "Google API client required. Install with: "
                "pip install google-api-python-client"
            )

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from various YouTube URL formats."""
        try:
            parsed_url = urlparse(url)
            if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
                if parsed_url.path == '/watch':
                    video_id = parse_qs(parsed_url.query).get('v', [None])[0]
                    if video_id:
                        return video_id
            elif parsed_url.hostname == 'youtu.be':
                return parsed_url.path[1:]

            logger.error(f"Could not extract video ID from URL: {url}")
            raise ValueError(f"Invalid YouTube URL format: {url}")
        except Exception as e:
            logger.error(f"Error parsing YouTube URL: {str(e)}")
            raise ValueError(f"Invalid YouTube URL format: {url}")

    def _get_video_transcript(self, video_id: str) -> str:
        """Get transcript for a video."""
        if not self.transcript_api:
            logger.error("Transcript API not initialized")
            return ""

        try:
            logger.info(f"Fetching transcript for video: {video_id}")
            transcript = self.transcript_api.get_transcript(video_id)
            return "\n".join(
                f"[{item['start']:.2f}] {item['text']}"
                for item in transcript
            )
        except Exception as e:
            logger.warning(f"Could not get transcript for video {video_id}: {str(e)}")
            return ""

    def _get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get detailed information about a video."""
        if not self.youtube:
            logger.error("YouTube API not initialized")
            raise ValueError("YouTube API not initialized properly")

        try:
            logger.info(f"Fetching video details for: {video_id}")
            response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()

            if not response.get('items'):
                logger.error(f"No video found with ID: {video_id}")
                raise ValueError(f"Video not found: {video_id}")

            video = response['items'][0]
            snippet = video['snippet']

            # Extract all available metadata
            metadata = {
                "title": snippet.get('title', ''),
                "description": snippet.get('description', ''),
                "published_at": snippet.get('publishedAt', ''),
                "channel_title": snippet.get('channelTitle', ''),
                "channel_id": snippet.get('channelId', ''),
                "duration": video.get('contentDetails', {}).get('duration', ''),
                "view_count": video.get('statistics', {}).get('viewCount', '0'),
                "like_count": video.get('statistics', {}).get('likeCount', '0'),
                "comment_count": video.get('statistics', {}).get('commentCount', '0'),
                "tags": snippet.get('tags', []),
                "category_id": snippet.get('categoryId', '')
            }
            return metadata
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            raise ValueError(f"Failed to get video details: {str(e)}")

    def load(self, source: str) -> Dict[str, Any]:
        """Load content from YouTube video.

        Args:
            source: YouTube video URL or ID

        Returns:
            Dict containing:
                - content: The video content (title, description, transcript)
                - meta_data: Video metadata (views, likes, etc.)
        """
        try:
            logger.info(f"Loading YouTube content from: {source}")
            video_id = self._extract_video_id(source)
            logger.info(f"Extracted video ID: {video_id}")

            # Get video details and transcript
            video_data = self._get_video_details(video_id)
            transcript = self._get_video_transcript(video_id)

            # Format content in a structured way for better RAG performance
            content_parts = [
                f"# {video_data['title']}",
                f"\nChannel: {video_data['channel_title']}",
                f"\nDescription: {video_data['description']}"
            ]

            # Add tags if available
            if video_data.get('tags'):
                content_parts.append(f"\nTags: {', '.join(video_data['tags'])}")

            # Add transcript with proper sectioning
            if transcript:
                content_parts.extend(["\n## Transcript", transcript])
            else:
                content_parts.append("\nNo transcript available")

            content = "\n".join(content_parts)

            # Generate document ID
            doc_id = hashlib.sha256(
                f"{video_id}-{video_data['published_at']}".encode()
            ).hexdigest()[:16]

            # Create comprehensive metadata
            metadata = {
                "doc_id": doc_id,
                "source": source,
                "type": "youtube",
                "video_id": video_id,
                "content_type": "video/transcript",
                "has_transcript": bool(transcript),
                **video_data
            }

            logger.info(f"Successfully loaded YouTube content for video: {video_id}")
            return {
                "content": content,
                "meta_data": metadata
            }

        except Exception as e:
            logger.error(f"Error loading YouTube content: {str(e)}")
            raise ValueError(f"Failed to load YouTube content: {str(e)}")

# For backward compatibility and explicit exports
__all__ = ['YouTubeLoader']