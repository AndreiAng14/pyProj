import os
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from .utils import read_file_content
from .ai_client import OllamaClient

class PPTXGenerator:
    def __init__(self, model="gemma3:270m"):
        self.client = OllamaClient(model=model)
        self.prs = Presentation()

    def generate_presentation(self, input_files, output_file, image_path=None):
        # 1. Read Content
        full_content = ""
        for file_path in input_files:
            try:
                content = read_file_content(file_path)
                full_content += content + "\n"
            except Exception as e:
                print(f"Skipping file {file_path}: {e}")

        if not full_content.strip():
            return "No content found in selected files."

        # 2. Get Text from AI (Simple approach from t1.ipynb)
        # Just send the content as the prompt.
        prompt = full_content.strip()
        
        print("Sending request to Ollama...")
        print(f"\n[DEBUG] PROMPT SENT:\n{prompt}\n")
        response_text = self.client.generate_text(prompt)
        print(f"\n[DEBUG] RAW RESPONSE:\n{response_text}\n")
        
        # 3. Create PPTX from the raw text
        # Splitting content into multiple slides to prevent overflow
        MAX_LINES_PER_SLIDE = 8
        
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        
        # Calculate needed slides
        if not lines:
            lines = ["No content generated."]
            
        # Create first slide
        slide_layout = self.prs.slide_layouts[1]
        current_slide = self.prs.slides.add_slide(slide_layout)
        
        # Title logic
        base_title = full_content.strip().split('\n')[0][:50]
        if len(full_content.strip()) > 50:
             base_title += "..."
        
        title = current_slide.shapes.title
        title.text = base_title
        
        content_shape = current_slide.placeholders[1]
        tf = content_shape.text_frame
        tf.clear()
        
        current_line_count = 0
        
        for i, line in enumerate(lines):
            # Check if we need a new slide
            if current_line_count >= MAX_LINES_PER_SLIDE:
                current_slide = self.prs.slides.add_slide(slide_layout)
                title = current_slide.shapes.title
                title.text = f"{base_title} (cont.)"
                
                content_shape = current_slide.placeholders[1]
                tf = content_shape.text_frame
                tf.clear()
                current_line_count = 0
            
            # Add paragraph
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(18)
            current_line_count += 1
            
            # Check for very long lines that might wrap and take up more space
            # Rough estimate: > 80 chars counts as 2 lines
            if len(line) > 80:
                current_line_count += int(len(line) / 80)

        # Add User Image only to the FIRST slide
        if image_path and os.path.exists(image_path):
             # Logic to find the first slide created in this batch
             # Ideally we attach it to the first slide we made above
            first_slide_index = self.prs.slides.index(current_slide) - (len(self.prs.slides.index(current_slide)) if hasattr(self.prs.slides, 'index') else 0) 
             # Actually safer to just grab the one we started with. 
             # But current_slide variable changed. 
             # Let's rely on finding standard slide 1 (if it's the only one match).
             # Simplification: Insert on the very first slide of the generated batch.
             # Since we are generating the whole deck here, prs.slides[0] is likely the first.
        try:
                self.prs.slides[0].shapes.add_picture(
                    image_path, Inches(7.5), Inches(5.5), width=Inches(2)
                )
        except Exception as e:
                print(f"Could not add image: {e}")

        # 4. Disclaimer Slide
        blank_layout = self.prs.slide_layouts[6] 
        end_slide = self.prs.slides.add_slide(blank_layout)
        
        txBox = end_slide.shapes.add_textbox(Inches(1), Inches(3), Inches(8), Inches(2))
        tf = txBox.text_frame
        p = tf.add_paragraph()
        p.text = "Facut cu iubire de catre gPPTX!\n ATENTIE gPPTX POATE AVEA ERORI, SE RECOMANDA VERIFICAREA FISIERULUI FINAL!"
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = RGBColor(255, 0, 0) # Red color
        p.alignment = PP_ALIGN.CENTER

        # Save
        try:
            self.prs.save(output_file)
            return f"Presentation saved successfully to {output_file}"
        except Exception as e:
            return f"Error saving file: {e}"
