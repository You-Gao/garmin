
import win32gui
import win32con
import subprocess
import os

def make_window_active(window_name):
    # First, print all active windows for debugging
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            windows.append(win32gui.GetWindowText(hwnd))
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    print("Active windows:")
    for w in windows:
        print(f"- {w}")
    
    # First try exact match
    hwnd = win32gui.FindWindowEx(None, None, None, window_name)
    
    # If exact match fails, try partial match
    if not hwnd:
        def find_window_callback(hwnd, param):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_name.lower() in window_title.lower():
                    param.append(hwnd)
        
        found_windows = []
        win32gui.EnumWindows(find_window_callback, found_windows)
        if found_windows:
            hwnd = found_windows[0]  # Use the first match
    
    if hwnd:
        window_title = win32gui.GetWindowText(hwnd)
        print(f"Found window: {window_title}")
        
        # Try Komorebi focus command first (if komorebi is running)
        try:
            # Check if komorebi is running
            result = subprocess.run(['komorebic', 'query', 'focused-window'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print("Komorebi detected, trying komorebi focus...")
                # Try to focus using komorebi
                subprocess.run(['komorebic', 'focus-window', str(hwnd)], 
                             capture_output=True, timeout=2)
                print(f"Focused window via Komorebi: {window_title}")
                return
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            print("Komorebi not available or failed, using standard Windows API...")
        
        # Fallback to standard Windows API
        try:
            # Simple approach that works better with tiling window managers
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.BringWindowToTop(hwnd)
            
            # Try SetForegroundWindow last
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                # If that fails, just ensure it's visible
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            
            print(f"Activated window via Windows API: {window_title}")
            
        except Exception as e:
            print(f"Error activating window: {e}")
            # Final fallback - just try to make it visible
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                print(f"Made window visible (final fallback): {window_title}")
            except Exception as e2:
                print(f"All methods failed: {e2}")
    else:
        print(f"Window containing '{window_name}' not found.")

if __name__ == "__main__":
    # Example usage
    make_window_active("Google Chrome")
    # You can replace "Google Chrome" with any other window name you want to activate