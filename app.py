import os
import fitz
import docx
import gradio as gr
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

# Initialize tools
search_tool = SerperDevTool()

# Resume Extraction Functions
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return "\n".join(fullText)

def extract_text_from_resume(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

# CrewAI Setup
def setup_crewai(resume_text, location):
    # Set up agents
    resume_feedback = Agent(
        role="Professional Resume Advisor",
        goal="Give feedback on resumes to make them stand out",
        verbose=True,
        backstory="Expert in resume optimization with keen eye for detail"
    )

    resume_advisor = Agent(
        role="Professional Resume Writer",
        goal="Rewrite resumes based on feedback",
        verbose=True,
        backstory="Skilled at enhancing resume content and structure"
    )

    job_researcher = Agent(
        role="Senior Recruitment Consultant",
        goal="Find relevant job openings",
        tools=[search_tool],
        verbose=True,
        backstory="Expert in job market analysis and opportunities"
    )

    # Define tasks
    feedback_task = Task(
        description=f"Analyze this resume and provide feedback: {resume_text}",
        expected_output="Bullet-point feedback with overall score/10",
        agent=resume_feedback
    )

    rewrite_task = Task(
        description="Improve the resume based on feedback",
        expected_output="Markdown formatted improved resume",
        agent=resume_advisor,
        context=[feedback_task]
    )

    research_task = Task(
        description=f"Find relevant jobs in {location}",
        expected_output="Markdown list of top 5 job opportunities with links",
        agent=job_researcher
    )

    # Create and run crew
    crew = Crew(
        agents=[resume_feedback, resume_advisor, job_researcher],
        tasks=[feedback_task, rewrite_task, research_task],
        verbose=True
    )
    
    return crew.kickoff()

# Gradio Interface
def process_resume(file, location):
    try:
        # Extract text
        resume_text = extract_text_from_resume(file.name)
        
        # Process with CrewAI
        result = setup_crewai(resume_text, location)
        
        # Parse results
        feedback = result[0].output.raw
        improved_resume = result[1].output.raw
        jobs = result[2].output.raw
        
        return feedback, improved_resume, jobs
    
    except Exception as e:
        return str(e), "", ""

with gr.Blocks() as demo:
    gr.Markdown("# AI Resume Assistant 🤖")
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="Upload Resume (PDF/DOCX)")
            location_input = gr.Textbox(label="Preferred Job Location")
            submit_btn = gr.Button("Process Resume")
        
        with gr.Column():
            feedback_output = gr.Textbox(label="Feedback", interactive=False)
            improved_resume_output = gr.Markdown(label="Improved Resume")
            jobs_output = gr.Markdown(label="Recommended Jobs")
    
    submit_btn.click(
        fn=process_resume,
        inputs=[file_input, location_input],
        outputs=[feedback_output, improved_resume_output, jobs_output]
    )

if __name__ == "__main__":
    demo.launch()