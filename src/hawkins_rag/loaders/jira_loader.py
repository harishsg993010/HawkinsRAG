import hashlib
from typing import Any, Dict, List, Optional
from atlassian import Jira
from .base import BaseLoader

class JiraLoader(BaseLoader):
    """Loader for Jira issues and content."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Jira loader with configuration.
        
        Required config:
        - url: Jira instance URL
        - username: Jira username/email
        - password: Jira API token or password
        """
        if not config or not all(k in config for k in ['url', 'username', 'password']):
            raise ValueError(
                "JiraLoader requires 'url', 'username', and 'password' in config. "
                "Get API token from https://id.atlassian.com/manage/api-tokens"
            )

        try:
            self.jira = Jira(
                url=config['url'],
                username=config['username'],
                password=config['password']
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Jira client: {str(e)}")

    def _format_issue(self, issue: Dict[str, Any]) -> str:
        """Format a Jira issue into readable text."""
        fields = issue['fields']
        parts = [
            f"Key: {issue['key']}",
            f"Type: {fields['issuetype']['name']}",
            f"Status: {fields['status']['name']}",
            f"Summary: {fields['summary']}",
            f"Description: {fields.get('description', 'No description')}",
            "\nComments:"
        ]

        # Add comments
        comments = self.jira.get_issue_comments(issue['key'])
        for comment in comments:
            author = comment['author']['displayName']
            created = comment['created']
            body = comment['body']
            parts.append(f"[{created}] {author}: {body}")

        return "\n".join(parts)

    def load(self, source: str) -> Any:
        """Load content from Jira using JQL query.

        Args:
            source: JQL query string (e.g., "project = DEMO AND status = Open")

        Returns:
            Dict containing document ID and array of issue data
        """
        try:
            # Search for issues using JQL
            issues = self.jira.jql(source)
            
            if not issues['issues']:
                raise ValueError(f"No issues found matching query: {source}")

            data = []
            all_content = []

            for issue in issues['issues']:
                content = self._format_issue(issue)
                all_content.append(content)

                data.append({
                    "content": content,
                    "meta_data": {
                        "key": issue['key'],
                        "id": issue['id'],
                        "type": issue['fields']['issuetype']['name'],
                        "status": issue['fields']['status']['name'],
                        "created": issue['fields']['created'],
                        "updated": issue['fields']['updated'],
                        "assignee": (
                            issue['fields'].get('assignee', {}).get('displayName', 'Unassigned')
                        ),
                        "reporter": (
                            issue['fields'].get('reporter', {}).get('displayName', 'Unknown')
                        ),
                        "labels": issue['fields'].get('labels', []),
                        "query": source
                    }
                })

            # Generate document ID
            doc_id = hashlib.sha256(
                (source + "".join(all_content)).encode()
            ).hexdigest()

            return {
                "doc_id": doc_id,
                "data": data
            }

        except Exception as e:
            raise ValueError(f"Error loading from Jira: {str(e)}")
