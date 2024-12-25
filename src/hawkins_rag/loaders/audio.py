import os
import hashlib
from typing import Any, Dict, Optional
from ..utils.base import BaseLoader
import logging

logger = logging.getLogger(__name__)

class AudioLoader(BaseLoader):
    """Loader for audio files using Deepgram."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the audio loader with Deepgram credentials."""
        super().__init__(config)
        self.config = config or {}

        if not os.environ.get("DEEPGRAM_API_KEY"):
            raise ValueError("DEEPGRAM_API_KEY environment variable required")

        try:
            from deepgram import DeepgramClient, PrerecordedOptions
            self.client = DeepgramClient(os.environ.get("DEEPGRAM_API_KEY"))
            self.PrerecordedOptions = PrerecordedOptions
            logger.info("Deepgram client initialized successfully")
        except ImportError:
            logger.error("Deepgram SDK not installed")
            raise ImportError(
                "Deepgram SDK required. Install with: pip install deepgram-sdk"
            )

    def load(self, source: str) -> Dict[str, Any]:
        """Load and transcribe audio from file or URL.

        Args:
            source: Path to local audio file or URL

        Returns:
            Dict containing:
                - content: The transcribed text
                - meta_data: Audio metadata
        """
        try:
            logger.info(f"Processing audio from: {source}")

            # Configure transcription options
            options = self.PrerecordedOptions(
                model="nova-2",  # Using Nova 2 model for better accuracy
                smart_format=True,
                language="en",
                detect_language=True
            )

            # Process URL or local file
            if source.startswith(('http://', 'https://')):
                logger.info(f"Transcribing audio from URL: {source}")
                source_obj = {"url": source}
                response = self.client.listen.prerecorded.v("1").transcribe_url(
                    source_obj, options
                )
            else:
                logger.info(f"Transcribing local audio file: {source}")
                with open(source, "rb") as audio:
                    source_obj = {"buffer": audio}
                    response = self.client.listen.prerecorded.v("1").transcribe_file(
                        source_obj, options
                    )

            # Extract transcription and metadata
            transcription = response.results.channels[0].alternatives[0].transcript
            if not transcription:
                raise ValueError("No transcription generated")

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(source) + transcription[:100]).encode()
            ).hexdigest()[:16]

            # Extract metadata
            metadata = {
                "source": source,
                "type": "audio",
                "language": response.results.channels[0].detected_language,
                "duration": response.results.channels[0].duration,
                "confidence": response.results.channels[0].alternatives[0].confidence
            }

            logger.info(f"Successfully transcribed audio from: {source}")
            return {
                "content": transcription,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "audio",
                    **metadata
                }
            }

        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            raise ValueError(f"Audio processing failed: {str(e)}")

# For backward compatibility and explicit exports
__all__ = ['AudioLoader']