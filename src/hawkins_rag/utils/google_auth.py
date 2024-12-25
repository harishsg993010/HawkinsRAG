"""Google OAuth configuration and utilities."""
import os
from typing import Dict, Any, Optional
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def get_google_oauth_config() -> Dict[str, Any]:
    """Get Google OAuth configuration from environment variables."""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError(
            "Google OAuth credentials not found. Please set GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET environment variables."
        )

    # Get Replit domain for proper OAuth redirect
    repl_domain = os.environ.get('REPL_SLUG', '') + '.' + os.environ.get('REPL_OWNER', '') + '.repl.co'
    redirect_uri = f"https://{repl_domain}"

    logger.info("""
    ==========================================================
    Google OAuth Authorization Process
    ==========================================================
    1. You will be redirected to Google's authorization page
    2. Sign in with your Google account
    3. Grant the requested permissions
    4. The authorization will complete automatically

    Note: This is a one-time process. Your credentials will be
    saved locally for future use.
    ==========================================================
    """)

    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'auth_uri': "https://accounts.google.com/o/oauth2/auth",
        'token_uri': "https://oauth2.googleapis.com/token",
        'redirect_uri': redirect_uri,
        'scope': [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
    }

def handle_oauth_error(error: Exception) -> str:
    """Handle OAuth-related errors and provide user-friendly messages."""
    error_msg = str(error)

    if "invalid_grant" in error_msg.lower():
        return (
            "Authorization failed. Please ensure you've granted the necessary permissions "
            "and try again. If the error persists, you may need to remove the saved "
            "token file and reauthorize."
        )
    elif "unauthorized_client" in error_msg.lower():
        return (
            "Client authorization failed. Please verify that your Google OAuth credentials "
            "are correct and that you've enabled the necessary Google Cloud APIs."
        )
    elif "access_denied" in error_msg.lower():
        return (
            "Access was denied. Please grant the requested permissions to allow the "
            "application to access your Google account data."
        )
    else:
        return (
            f"An error occurred during authorization: {error_msg}\n"
            "Please try again or check your credentials."
        )

def initialize_oauth_flow(token_path: str, scopes: list) -> Optional[Dict[str, Any]]:
    """Initialize and handle the OAuth flow."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        config = get_google_oauth_config()

        # Configure the OAuth flow with proper redirect URI
        flow = InstalledAppFlow.from_client_config(
            {
                'web': {
                    'client_id': config['client_id'],
                    'client_secret': config['client_secret'],
                    'auth_uri': config['auth_uri'],
                    'token_uri': config['token_uri'],
                    'redirect_uris': [config['redirect_uri']],
                    'javascript_origins': [config['redirect_uri']]
                }
            },
            scopes,
            redirect_uri=config['redirect_uri']
        )

        logger.info("Starting OAuth authorization flow...")
        # Use port 8080 and allow all hosts for Replit environment
        creds = flow.run_local_server(
            host='0.0.0.0',
            port=8080,
            open_browser=False,
            success_message="Authorization successful! You can close this window."
        )

        # Save the credentials
        import pickle
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

        logger.info("Authorization successful! Credentials saved.")
        return creds

    except Exception as e:
        error_msg = handle_oauth_error(e)
        logger.error(error_msg)
        return None