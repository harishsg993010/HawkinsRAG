"""Test web-based loaders (webpage, XML, RSS, beehive) with HawkinsRAG."""
import logging
from pathlib import Path
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_webpage_loader():
    """Test webpage loader with a simple webpage."""
    rag = HawkinsRAG()
    # Test with Python's official documentation
    url = "https://docs.python.org/3/"
    logger.info(f"\nTesting webpage loader with {url}")
    
    try:
        result = rag.load_document(url)
        logger.info(f"Webpage loader test: {'SUCCESS' if result else 'FAILED'}")
        
        if result:
            query = "What is this webpage about?"
            response = rag.query(query)
            logger.info(f"Query response: {response}")
    except Exception as e:
        logger.error(f"Error testing webpage loader: {str(e)}")

def test_rss_loader():
    """Test RSS loader with a public RSS feed."""
    rag = HawkinsRAG()
    # Test with Python's official blog RSS feed
    url = "https://blog.python.org/feeds/posts/default"
    logger.info(f"\nTesting RSS loader with {url}")
    
    try:
        result = rag.load_document(url, source_type="rss")
        logger.info(f"RSS loader test: {'SUCCESS' if result else 'FAILED'}")
        
        if result:
            query = "What are the recent blog posts about?"
            response = rag.query(query)
            logger.info(f"Query response: {response}")
    except Exception as e:
        logger.error(f"Error testing RSS loader: {str(e)}")

def test_xml_loader():
    """Test XML loader with a sample XML file."""
    rag = HawkinsRAG()
    # Create a sample XML file for testing
    test_xml = Path("test_data") / "test.xml"
    test_xml.parent.mkdir(exist_ok=True)
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <library>
        <book>
            <title>Python Programming</title>
            <author>John Doe</author>
            <year>2023</year>
        </book>
        <book>
            <title>Web Development</title>
            <author>Jane Smith</author>
            <year>2024</year>
        </book>
    </library>
    """
    
    try:
        with open(test_xml, "w") as f:
            f.write(xml_content)
        
        logger.info(f"\nTesting XML loader with {test_xml}")
        result = rag.load_document(str(test_xml), source_type="xml")
        logger.info(f"XML loader test: {'SUCCESS' if result else 'FAILED'}")
        
        if result:
            query = "What books are in the library?"
            response = rag.query(query)
            logger.info(f"Query response: {response}")
    except Exception as e:
        logger.error(f"Error testing XML loader: {str(e)}")
    finally:
        if test_xml.exists():
            test_xml.unlink()

def test_beehive_loader():
    """Test beehive loader with a simple website."""
    rag = HawkinsRAG()
    # Test with Python Package Index
    url = "https://pypi.org/project/hawkinsdb/"
    logger.info(f"\nTesting beehive loader with {url}")
    
    try:
        result = rag.load_document(url, source_type="beehive")
        logger.info(f"Beehive loader test: {'SUCCESS' if result else 'FAILED'}")
        
        if result:
            query = "What is this package about?"
            response = rag.query(query)
            logger.info(f"Query response: {response}")
    except Exception as e:
        logger.error(f"Error testing beehive loader: {str(e)}")

def main():
    """Run all web loader tests."""
    logger.info("Starting web loader tests...")
    
    test_webpage_loader()
    test_rss_loader()
    test_xml_loader()
    test_beehive_loader()
    
    logger.info("\nCompleted all web loader tests")

if __name__ == "__main__":
    main()
