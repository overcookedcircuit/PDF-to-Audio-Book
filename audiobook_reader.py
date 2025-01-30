import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import fitz  # PyMuPDF
import pyttsx3
import threading

class AudiobookReader:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Audiobook Reader")
        self.root.geometry("500x400")

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")
        self.speaking = False  # Playback control

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # File Selection Button
        self.btn_select_file = tk.Button(self.root, text="Select PDF File", command=self.select_pdf, font=("Arial", 12))
        self.btn_select_file.pack(pady=10)

        # Label for Selected File
        self.lbl_file = tk.Label(self.root, text="No file selected", font=("Arial", 10))
        self.lbl_file.pack(pady=5)

        # Voice Selection Dropdown
        self.lbl_voice = tk.Label(self.root, text="Select Voice:", font=("Arial", 12))
        self.lbl_voice.pack(pady=5)

        self.voice_var = tk.StringVar()
        self.voice_dropdown = ttk.Combobox(self.root, textvariable=self.voice_var, state="readonly")
        self.voice_dropdown["values"] = [voice.name for voice in self.voices]
        self.voice_dropdown.pack(pady=5)
        self.voice_dropdown.current(0)  # Default voice

        # Control Buttons
        self.btn_play = tk.Button(self.root, text="Play", command=self.play_audio, font=("Arial", 12))
        self.btn_play.pack(pady=5)

        self.btn_pause = tk.Button(self.root, text="Pause", command=self.pause_audio, font=("Arial", 12))
        self.btn_pause.pack(pady=5)

        self.btn_stop = tk.Button(self.root, text="Stop", command=self.stop_audio, font=("Arial", 12))
        self.btn_stop.pack(pady=5)

    def select_pdf(self):
        """Open file dialog and select a PDF"""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.lbl_file.config(text=f"Selected: {file_path.split('/')[-1]}")
            self.text = self.extract_text_from_pdf(file_path)

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from the selected PDF"""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text

    def play_audio(self):
        """Play the audiobook"""
        if not hasattr(self, 'text') or not self.text:
            messagebox.showerror("Error", "Please select a valid PDF file first!")
            return
        
        self.speaking = True
        self.engine.setProperty("voice", self.voices[self.voice_dropdown.current()].id)

        def run_tts():
            self.engine.say(self.text)
            self.engine.runAndWait()

        threading.Thread(target=run_tts, daemon=True).start()

    def pause_audio(self):
        """Pause playback (workaround by stopping)"""
        self.engine.stop()
        self.speaking = False

    def stop_audio(self):
        """Stop playback completely"""
        self.engine.stop()
        self.speaking = False

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = AudiobookReader(root)
    root.mainloop()
