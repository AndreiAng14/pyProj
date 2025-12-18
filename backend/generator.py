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

    def _apply_slide_master_style(self, slide):
        """
        Applies the specific design: Red background.
        """
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 0, 0)  # Red Background

    def _add_text_bold(self, text_frame, text):
        """
        Adds text with Bold styling.
        """
        p = text_frame.add_paragraph()
        p.text = text
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(255, 255, 255) # White text for better contrast on red

    def generate_presentation(self, input_files, output_file, image_path=None):
        # 1. Read Content
        full_content = ""
        for file_path in input_files:
            try:
                content = read_file_content(file_path)
                full_content += f"\n--- Content from {os.path.basename(file_path)} ---\n{content}\n"
            except Exception as e:
                print(f"Skipping file {file_path}: {e}")

        if not full_content:
            return "No content found in selected files."

        # 2. Get Structure from AI
        prompt = (
            "You are a presentation assistant. Analyze the following text and extract key points for a PowerPoint presentation. "
            "Return ONLY a JSON object with this structure: "
            "{'slides': [{'title': 'Slide Title', 'content': ['bullet 1', 'bullet 2']}]}. "
            "Do not add any markdown formatting like ```json. Just raw JSON. "
            f"\n\nTEXT:\n{full_content}"
        )
        
        print("Sending request to Ollama...")
        response_text = self.client.generate_text(prompt)
        
        # Clean response if it contains markdown code blocks
        clean_response = response_text.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(clean_response)
            slides_data = data.get("slides", [])
        except json.JSONDecodeError:
            # Fallback if valid JSON isn't returned
            print("AI response was not valid JSON. Creating generic slides.")
            slides_data = [{"title": "Presentation Content", "content": [line for line in response_text.split('\n') if line.strip()]}]

        # 3. Create PPTX
        for slide_info in slides_data:
            slide_layout = self.prs.slide_layouts[1] # Bullet content layout
            slide = self.prs.slides.add_slide(slide_layout)
            self._apply_slide_master_style(slide)

            # Title
            title = slide.shapes.title
            title.text = slide_info.get("title", "Untitled")
            title.text_frame.paragraphs[0].font.bold = True
            title.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

            # Content
            content_shape = slide.placeholders[1]
            tf = content_shape.text_frame
            tf.clear() # Clear default empty paragraph
            
            for point in slide_info.get("content", []):
                self._add_text_bold(tf, point)
            
            # Add User Image if provided
            if image_path and os.path.exists(image_path):
                # Add image to corner
                try:
                    self.prs.slides[self.prs.slides.index(slide)].shapes.add_picture(
                        image_path, Inches(7.5), Inches(5.5), width=Inches(2)
                    )
                except Exception as e:
                    print(f"Could not add image: {e}")

        # 4. Add Disclaimer Slide (Final Footer)
        blank_layout = self.prs.slide_layouts[6] 
        end_slide = self.prs.slides.add_slide(blank_layout)
        self._apply_slide_master_style(end_slide)
        
        txBox = end_slide.shapes.add_textbox(Inches(1), Inches(3), Inches(8), Inches(2))
        tf = txBox.text_frame
        p = tf.add_paragraph()
        p.text = "Facut cu iubire de catre gPPTX, ATENTIE gPPTX POATE AVEA ERORI, SE RECOMANDA VERIFICAREA FISIERULUI FINAL!"
        p.font.bold = True
        p.font.size = Pt(24)
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

        # 5. Save
        try:
            self.prs.save(output_file)
            return f"Presentation saved successfully to {output_file}"
        except Exception as e:
            return f"Error saving file: {e}"
