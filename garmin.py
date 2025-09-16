import ctypes
import time
import speech_recognition as sr
import os
import keyboard
import psutil

import helpers.mistral as mistral
import helpers.avatar as avatar
import helpers.win32 as win32
import helpers.spotify as spotify

def kill_other_terminals():
    """Kill all Windows Terminal processes except the one running this script"""
    current_pid = os.getpid()
    try:
        # Get all WindowsTerminal processes
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            if proc.info['name'] and 'WindowsTerminal' in proc.info['name']:
                # Check if this terminal is running our Python process or is parent of it
                try:
                    # Get all descendants of the terminal process
                    terminal_proc = psutil.Process(proc.info['pid'])
                    descendants = terminal_proc.children(recursive=True)
                    
                    # Check if our current process is among the descendants
                    is_our_terminal = any(child.pid == current_pid for child in descendants)
                    
                    if not is_our_terminal:
                        # This terminal is not running our script, kill it
                        terminal_proc.terminate()
                        print(f"Terminated terminal process PID: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
    except Exception as e:
        print(f"Error killing terminals: {e}")
        # Fallback to killing all terminals
        os.system("taskkill /f /im WindowsTerminal.exe")

# DEFINE COMMANDS HERE
COMMANDS = {
    ("hate", "game"): lambda command: keyboard.send('alt+f4'),
    ("clip", "that"): lambda command: print("Making a clip..."),
    
    # OPEN/CLOSE COMMANDS
    ("open", "chrome"): lambda command: os.system(r'start "" "C:\Program Files\Google\Chrome\Application\chrome.exe"'),
    ("close", "chrome"): lambda command: os.system("taskkill /f /im chrome.exe"),
    ("open", "notepad"): lambda command: os.system(r'start "" "C:\Windows\System32\notepad.exe"'),
    ("close", "notepad"): lambda command: os.system("taskkill /f /im notepad.exe"),
    ("open", "code"): lambda command: os.system(r'start "" "C:\Users\commo\AppData\Local\Programs\Microsoft VS Code\Code.exe"'),
    ("close", "code"): lambda command: os.system("taskkill /f /im Code.exe"),
    ("open", "habitica"): lambda command: os.system(r'start "" "https://habitica.com"'),
    ("close", "habitica"): lambda command: print("Habitica is a web app, no process to close."),
    ("open", "spotify"): lambda command: os.system(r'start "" "C:\Users\commo\AppData\Roaming\Spotify\Spotify.exe"'),
    ("close", "spotify"): lambda command: os.system("taskkill /f /im Spotify.exe"),
    ("open", "discord"): lambda command: os.system(r'start "" "C:\Users\commo\AppData\Local\Discord\Update.exe" --processStart Discord.exe'),
    ("close", "discord"): lambda command: os.system("taskkill /f /im Discord.exe"),
    ("open", "steam"): lambda command: os.system(r'start "" "C:\Program Files (x86)\Steam\Steam.exe"'),
    ("close", "steam"): lambda command: os.system("taskkill /f /im Steam.exe"),
    
    # GOTOs (A bit buggy if using with Komorebic)
    ("go", "to", "chrome"): lambda command: win32.make_window_active("Google Chrome"),
    ("go", "to", "notepad"): lambda command: win32.make_window_active("Notepad"),
    ("go", "to", "code"): lambda command: win32.make_window_active("Visual Studio Code"),
    ("go", "to", "spotify"): lambda command: win32.make_window_active("Spotify"),
    ("go", "to", "discord"): lambda command: win32.make_window_active("Discord"),
    ("go", "to", "steam"): lambda command: win32.make_window_active("Steam"),
    
    # GOOGLE CHROME
    ("google",): lambda command: os.system(rf'start "" "https://www.google.com/search?q={command}"') if command.startswith("google") else None,

    # SPOTIFY 
    ("play", "music"): lambda command: spotify.play_pause(),
    ("pause", "music"): lambda command: spotify.play_pause(),
    ("stop", "music"): lambda command: spotify.play_pause(),
    ("next", "song"): lambda command: spotify.next_track(),
    ("skip", "song"): lambda command: spotify.next_track(),
    ("previous", "song"): lambda command: spotify.previous_track(),
    ("last", "song"): lambda command: spotify.previous_track(),
    ("volume", "up"): lambda command: spotify.volume_up(),
    ("volume", "down"): lambda command: spotify.volume_down(),
    ("mute", "music"): lambda command: spotify.mute(),
    ("play", "by"): lambda command: spotify.play_artist_song(command.split("by ")[1].strip(), command.split("play ")[1].split(" by ")[0].strip()),
    ("play",): lambda command: spotify.play_artist(command.replace("play ", "")),
    ("clear", "q"): lambda command: spotify.clear_queue(),

    # MISTRAL
    ("question",): lambda command: mistral.call_mistral_with_question(command), 
    ("thanks",): lambda command: kill_other_terminals(),  # Close all terminals except current one
}
COMMAND = "" 

def action(command):
    global COMMAND
    COMMAND = command  # Store command globally for main loop
    for keywords, func in COMMANDS.items():
        contains_all = all(word in command for word in keywords)
        if contains_all:
            print(f"Executing command: {keywords}")
            func(command)
            return
    return

def callback(recognizer, audio):
    global COMMAND
    try:
        command = recognizer.recognize_google(audio).lower()
        COMMAND = command  # Update global command
        print(COMMAND)
        action(command)
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        pass

# INITIALIZE RECOGNITION
r = sr.Recognizer()
m = sr.Microphone()

r.pause_threshold = .5                      # How long to wait before considering speech ended
r.phrase_threshold = .2                     # Minimum audio length to consider as speech
r.non_speaking_duration = .5                # Minimum silence duration to split phrases

with m as source: r.adjust_for_ambient_noise(source)
r.listen_in_background(m, callback)

# HIDE CONSOLE
import sys,ctypes 

if sys.platform == "win32":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# MAIN LOOP to UPDATE AVATAR ANIMATION AND RESPOND TO COMMANDS
last_animation = None
while True:
    if any(word in COMMAND for word in ["what", "who", "where", "when", "why", "how"]):
        if last_animation != "thinking":
            avatar.start_gui_thread("thinking")
            last_animation = "thinking"
    elif "open" in COMMAND or "close" in COMMAND:
        if last_animation != "active":
            avatar.start_gui_thread("active")
            last_animation = "active"
    elif "thanks" in COMMAND:
        if last_animation != "happy":
            avatar.start_gui_thread("happy")
            last_animation = "happy"
    elif any(word in COMMAND for word in ["hate", "close"]):
        if last_animation != "angry":
            avatar.start_gui_thread("angry")
            last_animation = "angry"
    else:
        if last_animation != "idle":
            avatar.start_gui_thread("idle")
            last_animation = "idle"

    time.sleep(1) 
    