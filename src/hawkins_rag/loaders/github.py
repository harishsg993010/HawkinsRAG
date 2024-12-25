"""GitHub content loader implementation."""
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional, cast
from github import Github, GithubException, UnknownObjectException
from requests.exceptions import RequestException
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class GithubLoader(BaseLoader):
    """Loader for GitHub content."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize GitHub loader with configuration."""
        super().__init__(config)
        config = config or {}

        if 'token' not in config:
            raise ValueError(
                "GithubLoader requires a personal access token in config['token']. "
                "Create one at https://github.com/settings/tokens"
            )

        try:
            logger.info("Initializing GitHub client...")
            self.client = Github(
                login_or_token=config['token'],
                timeout=30,
                retry=3,
                per_page=100  # Increase items per page for efficiency
            )
            self._test_connection()
        except Exception as e:
            logger.error(f"Failed to initialize GitHub client: {str(e)}")
            raise ValueError(f"GitHub client initialization failed: {str(e)}")

    def _test_connection(self) -> None:
        """Test GitHub connection with timeout."""
        start_time = time.time()
        timeout = 30  # 30 seconds timeout
        while True:
            try:
                user = self.client.get_user().login
                logger.info(f"Successfully authenticated with GitHub as user: {user}")

                # Check rate limit
                rate_limit = self.client.get_rate_limit()
                logger.info(f"GitHub API Rate Limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
                break
            except GithubException as e:
                if e.status == 401:
                    raise ValueError("Invalid GitHub token. Please check your credentials.")
                elif e.status == 403:
                    raise ValueError("GitHub token lacks required permissions or rate limit exceeded.")
                elif time.time() - start_time > timeout:
                    raise ValueError("GitHub authentication timed out")
                time.sleep(1)
            except RequestException as e:
                if time.time() - start_time > timeout:
                    raise ValueError("GitHub authentication timed out")
                time.sleep(1)

    def _handle_rate_limit(self) -> None:
        """Handle GitHub API rate limiting."""
        try:
            rate_limit = self.client.get_rate_limit()
            if rate_limit.core.remaining == 0:
                wait_time = (rate_limit.core.reset - time.time()).total_seconds()
                if wait_time > 0:
                    logger.warning(f"Rate limit reached. Waiting {wait_time:.0f} seconds...")
                    time.sleep(min(wait_time + 1, 30))  # Wait max 30 seconds
        except Exception as e:
            logger.warning(f"Error checking rate limit: {str(e)}")

    def _get_file_content(self, repo_name: str, file_path: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Get content of a specific file with retries and timeout."""
        max_retries = 3
        retry_count = 0
        start_time = time.time()
        timeout = 60  # 60 seconds total timeout

        while retry_count < max_retries:
            try:
                if time.time() - start_time > timeout:
                    raise ValueError(f"Timeout fetching file content after {timeout} seconds")

                self._handle_rate_limit()
                logger.info(f"Fetching file {file_path} from {repo_name} (attempt {retry_count + 1})")

                try:
                    repo = self.client.get_repo(repo_name)
                except UnknownObjectException:
                    raise ValueError(f"Repository not found or not accessible: {repo_name}")
                except GithubException as e:
                    if e.status == 404:
                        raise ValueError(f"Repository not found or not accessible: {repo_name}")
                    raise

                default_branch = repo.default_branch
                try:
                    file_content = repo.get_contents(
                        file_path, 
                        ref=branch or default_branch
                    )
                except UnknownObjectException:
                    raise ValueError(f"File not found: {file_path} in {repo_name}")
                except GithubException as e:
                    if e.status == 404:
                        raise ValueError(f"File not found: {file_path} in {repo_name}")
                    raise

                if not file_content or file_content.type != "file":
                    raise ValueError(f"Path {file_path} is not a valid file")

                content = file_content.decoded_content.decode('utf-8')
                metadata = {
                    "path": file_content.path,
                    "sha": file_content.sha,
                    "url": file_content.html_url,
                    "type": file_content.type,
                    "size": file_content.size,
                    "last_modified": file_content.last_modified if hasattr(file_content, 'last_modified') else None,
                    "branch": branch or default_branch
                }

                logger.info(f"Successfully fetched file {file_path} from {repo_name}")
                return {
                    "content": content,
                    "meta_data": metadata
                }

            except GithubException as e:
                if e.status == 403:  # Rate limit exceeded
                    self._handle_rate_limit()
                elif e.status in [404, 409]:  # Not found or conflict
                    raise ValueError(str(e))
                else:
                    retry_count += 1
                    if retry_count == max_retries:
                        logger.error(f"GitHub API error after {max_retries} retries: {str(e)}")
                        raise ValueError(f"Failed to get file content: {str(e)}")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    continue
            except Exception as e:
                logger.error(f"Error fetching file content: {str(e)}")
                raise ValueError(f"Failed to get file content: {str(e)}")

        raise ValueError("Failed to fetch file content after maximum retries")

    def load(self, source: str) -> Dict[str, Any]:
        """Load GitHub content based on source specification."""
        try:
            if not source.startswith("repo:"):
                raise ValueError(
                    'Invalid source format. Use "repo:username/repo[/path][@branch]" format'
                )

            repo_query = source[5:]  # Remove 'repo:' prefix
            parts = repo_query.split("@")
            branch = parts[1] if len(parts) > 1 else None
            repo_parts = parts[0].split("/", 2)

            if len(repo_parts) < 2:
                raise ValueError("Invalid repository format. Use username/repo[/path]")

            repo_name = "/".join(repo_parts[:2])
            path = repo_parts[2] if len(repo_parts) > 2 else None

            logger.info(f"Loading from repository: {repo_name} (branch: {branch}, path: {path})")

            if not path:
                return cast(Dict[str, Any], {
                    "content": "", 
                    "meta_data": {
                        "source": source, 
                        "error": "No file path specified",
                        "type": "github",
                        "repository": repo_name
                    }
                })

            start_time = time.time()
            result = self._get_file_content(repo_name, path, branch)
            load_time = time.time() - start_time
            logger.info(f"Content loaded in {load_time:.2f} seconds")

            content = result["content"]
            metadata = result["meta_data"]

            # Generate document ID
            doc_id = hashlib.sha256(
                f"{repo_name}/{path}".encode()
            ).hexdigest()[:16]

            return cast(Dict[str, Any], {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "github",
                    "repository": repo_name,
                    "load_time": load_time,
                    **metadata
                }
            })

        except Exception as e:
            logger.error(f"Error in GitHub loader: {str(e)}")
            raise ValueError(f"GitHub loader failed: {str(e)}")

    def _search_code(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub code."""
        try:
            results = []
            code_results = self.client.search_code(query)

            for item in code_results:
                try:
                    content = item.decoded_content.decode('utf-8')
                    metadata = {
                        "url": item.html_url,
                        "repository": item.repository.full_name,
                        "path": item.path,
                        "sha": item.sha
                    }
                    results.append({
                        "content": content,
                        "meta_data": metadata
                    })
                except Exception as e:
                    logger.warning(f"Failed to process code result {item.html_url}: {str(e)}")
                    continue

            return results
        except GithubException as e:
            logger.error(f"GitHub API error in code search: {str(e)}")
            raise ValueError(f"GitHub code search failed: {str(e)}")

# For backward compatibility and explicit exports
__all__ = ['GithubLoader']