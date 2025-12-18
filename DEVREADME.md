# Developer Guide (DEVREADME)

## Overview
gPPTX is a Python application that generates PowerPoint presentations from text files using AI (Ollama).

## Project Structure
*   **main.py**: The entry point. It creates the Graphical User Interface (GUI) where you select files.
*   **backend/**: Contains the "brain" of the application.
    *   `generator.py`: Reads your files, sends text to AI, and builds the PPTX slides.
    *   `ai_client.py`: Talks to Ollama (the AI model running locally).
    *   `utils.py`: Simple tools to read text from files.
*   **requirements.py**: A script to help you install necessary libraries.
*   **INSTALL.txt**: Step-by-step installation guide.

## Logic Explained (For Beginners)
1.  **Input**: The user selects `.txt`, `.md`, or `.yaml` files in the app.
2.  **Processing**:
    *   The app reads all the text from these files.
    *   It sends this text to the AI (Ollama) with a specific request: "Please structure this into slides with titles and bullet points in JSON format."
3.  **Generation**:
    *   The AI replies with the structured data.
    *   The app takes this data and uses `python-pptx` to create slides.
    *   It applies the Red Background and Bold Text style.
    *   It adds the specific footer to the final slide.
4.  **Output**: The app saves the `.pptx` file to your chosen location.

## How to Run
1.  Follow the steps in `INSTALL.txt` to set up Python and Ollama.
2.  Run `python main.py`.
