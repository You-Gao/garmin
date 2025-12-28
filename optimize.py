import speech_recognition as sr

def callback(recognizer, audio):
    global COMMAND
    try:
        command = recognizer.recognize_google(audio).lower()
        print(command)
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        pass
    
# INITIALIZE RECOGNITION
r = sr.Recognizer()
m = sr.Microphone()

# Default settings
r.pause_threshold = 0.5
r.phrase_threshold = 0.2
r.non_speaking_duration = 0.5

print("Adjusting for ambient noise, please be quiet...")
with m as source:
    r.adjust_for_ambient_noise(source)
print("Ambient noise adjustment complete.")

stop_listening = None

while True:
    print("\n--- Current Settings ---")
    print(f"1. pause_threshold: {r.pause_threshold}")
    print(f"2. phrase_threshold: {r.phrase_threshold}")
    print(f"3. non_speaking_duration: {r.non_speaking_duration}")
    print("\nListening in the background. Speak a few commands to test.")
    
    # Start listening in the background
    stop_listening = r.listen_in_background(m, callback)
    
    # Test period
    input("Press Enter when you are ready to provide feedback...")
    
    # Stop listening
    if stop_listening:
        stop_listening(wait_for_stop=False)
        
    satisfied = input("Are the settings fluid? (y/n): ").lower()
    if satisfied == 'y':
        print("Great! Final settings are:")
        print(f" - pause_threshold: {r.pause_threshold}")
        print(f" - phrase_threshold: {r.phrase_threshold}")
        print(f" - non_speaking_duration: {r.non_speaking_duration}")
        # To keep listening with final settings, we can start it one last time
        print("\nNow listening with the final optimized settings...")
        r.listen_in_background(m, callback)
        # Keep the script running
        import time
        while True:
            time.sleep(0.1)

    while True:
        choice = input("Which parameter to adjust? (1, 2, 3) or 'r' to restart test: ")
        if choice in ['1', '2', '3']:
            try:
                value = float(input(f"Enter new value for parameter {choice}: "))
                if choice == '1':
                    r.pause_threshold = value
                elif choice == '2':
                    r.phrase_threshold = value
                elif choice == '3':
                    r.non_speaking_duration = value
                break 
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice.lower() == 'r':
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 'r'.")

