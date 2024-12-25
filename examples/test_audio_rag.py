"""Test script for audio content RAG implementation."""
import logging
import os
from pathlib import Path
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_audio_rag():
    """Test audio RAG with various content types."""
    # Initialize RAG with audio configuration
    config = {
        "loader_config": {
            "audio": {
                "api_key": os.getenv("DEEPGRAM_API_KEY")
            }
        }
    }

    try:
        logger.info("Initializing RAG system...")
        rag = HawkinsRAG(config=config)

        # Test with our harvard wav file
        test_file = "test_data/audio/harvard.wav"

        if not os.path.exists(test_file):
            logger.error(f"Test file not found: {test_file}")
            return

        logger.info(f"\nTesting audio file: {test_file}")
        try:
            # Load audio content
            result = rag.load_document(test_file, source_type="audio")

            if result:
                logger.info(f"Successfully loaded audio from {test_file}")

                # Test queries
                test_queries = [
                    "What is being said in this audio?",
                    "Transcribe the exact words from the audio",
                    "What is the main message of this recording?"
                ]

                for query in test_queries:
                    logger.info(f"\nProcessing query: {query}")
                    response = rag.query(query)
                    logger.info(f"Response: {response}")
            else:
                logger.error(f"Failed to load audio file: {test_file}")

        except Exception as e:
            logger.error(f"Error processing {test_file}: {str(e)}")

    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}")

def main():
    """Run audio RAG tests."""
    logger.info("Starting audio RAG tests...")
    test_audio_rag()
    logger.info("\nCompleted audio RAG tests")

if __name__ == "__main__":
    main()