import tkinter as tk
import threading
import os

class AnimatedGIF:
    def __init__(self, root, gif_path):
        self.root = root
        self.gif_path = gif_path
        self.frames = []
        self.current_frame = 0
        self.animating = False
        
        # Load all frames of the GIF
        try:
            frame = 0
            while True:
                self.frames.append(tk.PhotoImage(file=gif_path, format=f"gif -index {frame}"))
                frame += 1
        except tk.TclError:
            # No more frames
            pass
        
        self.label = tk.Label(root, bg='black', borderwidth=0, highlightthickness=0)
        self.label.pack()
        
        if self.frames:
            self.start_animation()
    
    def start_animation(self):
        if not self.animating:
            self.animating = True
            self.animate()
    
    def stop_animation(self):
        self.animating = False
    
    def animate(self):
        if self.animating and self.frames:
            try:
                self.label.config(image=self.frames[self.current_frame])
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.root.after(100, self.animate)  # 100ms delay between frames
            except tk.TclError:
                # Handle case where tkinter has been destroyed
                self.animating = False

# Global variables for tkinter GUI
root = None
animated_gif = None
gui_thread = None
current_gif_name = None
requested_gif_name = None

def cleanup_gui():
    """Clean up the existing GUI thread and window"""
    global root, animated_gif
    try:
        if root:
            # Stop animation first
            if animated_gif:
                animated_gif.stop_animation()
            # Schedule destruction on the GUI thread using after()
            root.after(0, lambda: root.quit())
            # Don't call destroy() from different thread
            root = None
            animated_gif = None
    except (tk.TclError, AttributeError):
        # Handle case where tkinter has already been destroyed
        root = None
        animated_gif = None

def change_gif(new_gif_name):
    global animated_gif, current_gif_name
    if root and animated_gif and current_gif_name != new_gif_name:
        try:
            gif_path = os.path.join(os.path.dirname(__file__), new_gif_name)
            new_frames = []
            frame = 0
            while True:
                try:
                    new_frames.append(tk.PhotoImage(file=gif_path, format=f"gif -index {frame}"))
                    frame += 1
                except tk.TclError:
                    break
            
            if new_frames:
                animated_gif.frames = new_frames
                animated_gif.current_frame = 0
                current_gif_name = new_gif_name
                print(f"Changed to: {new_gif_name}")
        except Exception as e:
            print(f"Error changing GIF: {e}")

def check_for_gif_change():
    global requested_gif_name, current_gif_name
    if requested_gif_name and requested_gif_name != current_gif_name:
        change_gif(requested_gif_name)
        requested_gif_name = None
    
    if root:
        root.after(100, check_for_gif_change)

def setup_gui(file_name):
    global root, animated_gif, current_gif_name
    root = tk.Tk()
    root.overrideredirect(True)
    
    # Keeps the window in front of others
    root.attributes('-topmost', True)  # Stay on top
    root.focus_force()  # Force focus
    root.after(1, lambda: root.focus_force())  # Force focus after 1ms
    
    # Make background transparent - set a color key for transparency
    root.wm_attributes('-transparentcolor', 'black')  # Make black pixels transparent
    root.configure(bg='black')  # Set background to black (will be transparent)
    
    root.geometry("200x200+1100+625")  # width x height + x_offset + y_offset
    gif_path = os.path.join(os.path.dirname(__file__), f"gifs/{file_name}.gif")
    
    animated_gif = AnimatedGIF(root, gif_path)
    current_gif_name = f"gifs/{file_name}.gif"

    check_for_gif_change()
    
    root.mainloop()

def start_gui_thread(file_name="gengar"):
    global gui_thread, requested_gif_name
    print(f"Starting avatar: {file_name}")
    
    # If GUI is already running, just request a GIF change
    try:
        if root and root.winfo_exists():
            requested_gif_name = f"gifs/{file_name}.gif"
            print(f"Requested GIF change to: {file_name}")
            return gui_thread
    except tk.TclError:
        # Window was destroyed, need to start new one
        pass
    
    # Otherwise start a new GUI thread
    gui_thread = threading.Thread(target=setup_gui, args=(file_name,), daemon=True)
    gui_thread.start()
    
    return gui_thread

def request_gif_change(file_name):
    global requested_gif_name
    requested_gif_name = f"gifs/{file_name}.gif"

def stop_avatar():
    cleanup_gui()
    
def is_avatar_running():
    global root
    try:
        return root is not None and root.winfo_exists()
    except (tk.TclError, AttributeError):
        return False