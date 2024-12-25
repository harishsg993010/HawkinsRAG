"""Test script for Slack loader functionality."""
import os
import logging
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_slack_loader():
    """Test Slack loader with a sample channel."""
    # Initialize RAG with Slack configuration
    config = {
        "loader_config": {
            "slack": {
                "token": os.getenv("SLACK_BOT_TOKEN")
            }
        }
    }

    try:
        logger.info("Testing Slack loader...")
        rag = HawkinsRAG(config=config)

        # Test channels to process
        # Note: Replace these with your actual channel IDs
        test_channels = [
            "C1234567890",  # Replace with actual channel ID
            "#general"      # Test with channel name
        ]

        for channel in test_channels:
            try:
                logger.info(f"\nLoading messages from channel: {channel}")
                result = rag.load_document(channel, source_type="slack")
                logger.info(f"Slack loader test for {channel}: {'SUCCESS' if result else 'FAILED'}")

                if result:
                    # Test different types of queries
                    test_queries = [
                        "What are the recent discussions about?",
                        "Summarize the key points from the messages",
                        "What are the main topics discussed in threads?"
                    ]

                    for query in test_queries:
                        logger.info(f"\nTesting query: {query}")
                        response = rag.query(query)
                        logger.info(f"Query response: {response}")

            except Exception as e:
                logger.error(f"Error testing channel '{channel}': {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Slack loader test failed: {str(e)}")

def main():
    """Run Slack loader tests."""
    logger.info("Starting Slack loader tests...")
    test_slack_loader()
    logger.info("\nCompleted Slack loader tests")

if __name__ == "__main__":
    main()
