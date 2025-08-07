import subprocess
import time
import ctypes
from ctypes import wintypes

# Windows Virtual Key Codes for media keys
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD

# Windows API constants
KEYEVENTF_KEYUP = 0x0002

def send_key(vk_code):
    """Send a virtual key using Windows API"""
    try:
        user32 = ctypes.windll.user32
        user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
        print(f"Sent virtual key: {hex(vk_code)}")
        return True
    except Exception as e:
        print(f"Error sending key: {e}")
        return False

def play_pause():
    """Toggle play/pause for Spotify"""
    send_key(VK_MEDIA_PLAY_PAUSE)

def next_track():
    """Skip to next track"""
    send_key(VK_MEDIA_NEXT_TRACK)

def previous_track():
    """Go to previous track"""
    send_key(VK_MEDIA_PREV_TRACK)

def volume_up():
    """Increase volume"""
    send_key(VK_VOLUME_UP)

def volume_down():
    """Decrease volume"""
    send_key(VK_VOLUME_DOWN)

def mute():
    """Mute/unmute"""
    send_key(VK_VOLUME_MUTE)

if __name__ == "__main__":
    # Test the functions
    print("Testing Spotify controls...")
    play_pause()
