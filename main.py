import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from backend.generator import PPTXGenerator

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PPTXApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("gPPTX Generator")
        self.geometry("600x500")

        self.input_files = []
        self.image_path = None
        self.generator = PPTXGenerator()

        self._create_widgets()

    def _create_widgets(self):
        # Header
        self.header = ctk.CTkLabel(self, text="gPPTX Generator", font=("Roboto", 24, "bold"))
        self.header.pack(pady=20)

        # File Selection
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, fill="x", padx=20)

        self.btn_files = ctk.CTkButton(self.file_frame, text="Select Input Files (.md, .txt, .yaml)", command=self.select_files)
        self.btn_files.pack(pady=10)

        self.lbl_files = ctk.CTkLabel(self.file_frame, text="No files selected", text_color="gray")
        self.lbl_files.pack(pady=5)

        # Image Selection
        self.image_frame = ctk.CTkFrame(self)
        self.image_frame.pack(pady=10, fill="x", padx=20)

        self.btn_image = ctk.CTkButton(self.image_frame, text="Select Image (Optional)", command=self.select_image)
        self.btn_image.pack(pady=10)

        self.lbl_image = ctk.CTkLabel(self.image_frame, text="No image selected", text_color="gray")
        self.lbl_image.pack(pady=5)

        # Generate Button
        self.btn_generate = ctk.CTkButton(self, text="Generate Presentation", command=self.start_generation, fg_color="green", height=50)
        self.btn_generate.pack(pady=30, padx=20, fill="x")

        # Status
        self.lbl_status = ctk.CTkLabel(self, text="Ready", text_color="white")
        self.lbl_status.pack(pady=10)

    def select_files(self):
        filetypes = (
            ('All supported', '*.txt *.md *.yaml *.yml'),
            ('Text files', '*.txt'),
            ('Markdown files', '*.md'),
            ('YAML files', '*.yaml *.yml')
        )
        filenames = filedialog.askopenfilenames(title='Open files', initialdir='/', filetypes=filetypes)
        if filenames:
            self.input_files = filenames
            display_text = "\n".join([os.path.basename(f) for f in filenames])
            self.lbl_files.configure(text=f"Selected: {len(filenames)} files\n{display_text}", text_color="white")

    def select_image(self):
        filetypes = (('Images', '*.png *.jpg *.jpeg'), ('All files', '*.*'))
        filename = filedialog.askopenfilename(title='Open image', initialdir='/', filetypes=filetypes)
        if filename:
            self.image_path = filename
            self.lbl_image.configure(text=f"Image: {os.path.basename(filename)}", text_color="white")

    def start_generation(self):
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select at least one input file.")
            return

        # Ask for save location
        output_file = filedialog.asksaveasfilename(
            defaultextension=".pptx",
            filetypes=[("PowerPoint", "*.pptx")],
            title="Save Presentation As"
        )
        
        if not output_file:
            return

        self.lbl_status.configure(text="Generating... Please wait.", text_color="yellow")
        self.btn_generate.configure(state="disabled")

        # Run in thread to not freeze GUI
        thread = threading.Thread(target=self._run_generator, args=(output_file,))
        thread.start()

    def _run_generator(self, output_file):
        try:
            result = self.generator.generate_presentation(self.input_files, output_file, self.image_path)
            self.lbl_status.configure(text="Done!", text_color="green")
            messagebox.showinfo("Success", result)
        except Exception as e:
            self.lbl_status.configure(text="Error!", text_color="red")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_generate.configure(state="normal")

if __name__ == "__main__":
    app = PPTXApp()
    app.mainloop()
