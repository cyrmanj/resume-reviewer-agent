# Resume Reviewer Agent

A simple AI-powered resume reviewer agent that analyzes PDF or DOCX resumes, gives feedback, and helps improve formatting & content.  
Built with Python, uses OpenAI + optional Serper for research/insights; exposes a simple UI with Gradio.

## Features

- Load resumes in PDF or DOCX format.  
- Analyze content (skills, grammar, formatting, structure).  
- Provide actionable feedback / suggestions.  
- Easy to extend — you can modify evaluation rules, analysis logic, or integrate other models/tools.

## Requirements

- Python 3.10+ (or your version)  
- Dependencies listed in `requirements.txt` (or install manually): e.g. `fitz`, `python-docx`, `gradio`, `crewai`, `crewai_tools`, etc.  
- An OpenAI API key (set via environment variable or `openai.txt` file).  
- (Optional) A Serper API key, if you want web-search based review/utilities.  

## Installation

```bash
# clone repo
git clone https://github.com/YOUR_USERNAME/resume-reviewer-agent.git
cd resume-reviewer-agent

# (optional) create virtual environment
python -m venv venv
source venv/bin/activate  # (macOS / Linux)
# or `venv\Scripts\activate` on Windows

# install dependencies
pip install -r requirements.txt
