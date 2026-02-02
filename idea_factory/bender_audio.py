"""Helper function to trigger Bender audio playback."""

import os
import requests


def play_bender_audio(text: str) -> bool:
    """
    Send text to Bender app for TTS playback.
    
    Args:
        text: Text to convert to speech and play
    
    Returns:
        True if successful, False otherwise
    """
    bender_url = os.getenv('BENDER_URL', 'http://bender.rmn.pp.ua')
    endpoint = f"{bender_url}/audio/play"
    
    try:
        response = requests.post(
            endpoint,
            json={"text": text},
            timeout=2  # Don't wait too long, this is non-blocking
        )
        return response.status_code == 200
    except Exception as e:
        # Silently fail - audio is optional
        print(f"Failed to play Bender audio: {e}")
        return False
