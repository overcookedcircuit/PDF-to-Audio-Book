import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import fitz  # PyMuPDF
import pyttsx3
import threading
import queue

class AudiobookReader:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Audiobook Reader")
        self.root.geometry("500x350")
        self.root.configure(bg="#eed6e2")  # Pink-ish background

        # Set custom window icon
        try:
            self.root.iconbitmap("icon.ico")  # Change to your icon file
        except Exception as e:
            print("Error loading icon:", e)

        # Initialize TTS Engine
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")

        self.speaking = False  
        self.paused = False  
        self.current_text = ""  
        self.position = 0  # Keep track of where the reading stopped

        # Queue for handling speech
        self.speech_queue = queue.Queue()

        self.create_widgets()

    def create_widgets(self):
        # File Selection Button
        self.btn_select_file = ttk.Button(self.root, text="Select PDF File", command=self.select_pdf)
        self.btn_select_file.pack(pady=25)

        # Label for Selected File
        self.lbl_file = tk.Label(self.root, text="No file selected", bg="#eed6e2", font=("Arial", 10))
        self.lbl_file.pack(pady=5)

        # Voice Selection (Side-by-Side Layout)
        voice_frame = tk.Frame(self.root, bg="#eed6e2")
        voice_frame.pack(pady=10)

        self.lbl_voice = tk.Label(voice_frame, text="Select Voice:", bg="#eed6e2", font=("Arial", 12))
        self.lbl_voice.grid(row=0, column=0, padx=5)

        self.voice_var = tk.StringVar()
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly", width=30)
        self.voice_dropdown["values"] = [voice.name for voice in self.voices]
        self.voice_dropdown.grid(row=0, column=1, padx=5)
        self.voice_dropdown.current(0)  # Default voice

        # Control Button Frame (Side-by-Side Layout)
        btn_frame = tk.Frame(self.root, bg="#eed6e2")
        btn_frame.pack(pady=30)

        self.btn_play = ttk.Button(btn_frame, text="▶ Play", command=self.play_audio, width=10)
        self.btn_play.grid(row=10, column=0, padx=15)

        self.btn_pause = ttk.Button(btn_frame, text="⏸ Pause", command=self.pause_audio, width=10)
        self.btn_pause.grid(row=10, column=1, padx=15)

        self.btn_stop = ttk.Button(btn_frame, text="⏹ Stop", command=self.stop_audio, width=10)
        self.btn_stop.grid(row=10, column=2, padx=15)

    def select_pdf(self):
        """Open file dialog and select a PDF"""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.lbl_file.config(text=f"Selected: {file_path.split('/')[-1]}")
            self.text = self.extract_text_from_pdf(file_path)
            self.current_text = self.text  # Store the text

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from the selected PDF"""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text

    def speak_text(self):
        """Handles text-to-speech playback"""
        while not self.speech_queue.empty():
            text_chunk = self.speech_queue.get()
            self.engine.say(text_chunk)
            self.engine.runAndWait()
            self.speech_queue.task_done()

    def play_audio(self):
        """Play or Resume the audiobook"""
        if not hasattr(self, 'text') or not self.text:
            messagebox.showerror("Error", "Please select a valid PDF file first!")
            return

        self.speaking = True
        self.engine.setProperty("voice", self.voices[self.voice_dropdown.current()].id)

        # If paused, resume from last position
        if self.paused:
            text_to_read = self.current_text[self.position:]
            self.paused = False
        else:
            text_to_read = self.current_text

        # Split the text into smaller chunks (improves performance)
        chunk_size = 200  # Adjust this for better performance
        for i in range(0, len(text_to_read), chunk_size):
            self.speech_queue.put(text_to_read[i:i+chunk_size])

        # Start a new thread to process the speech queue
        if not hasattr(self, 'tts_thread') or not self.tts_thread.is_alive():
            self.tts_thread = threading.Thread(target=self.speak_text, daemon=True)
            self.tts_thread.start()

    def pause_audio(self):
        """Pause playback by stopping and saving position"""
        if self.speaking:
            self.engine.stop()
            self.paused = True
            self.speaking = False

            # Save position in text where it stopped
            self.position = len(self.current_text) - len(self.speech_queue.queue) * 200  # Approximate position

    def stop_audio(self):
        """Completely stop playback and reset"""
        self.engine.stop()
        self.speaking = False
        self.paused = False
        self.position = 0  # Reset position
        with self.speech_queue.mutex:
            self.speech_queue.queue.clear()  # Clear the queue to prevent resuming

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = AudiobookReader(root)
    root.mainloop()
