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
        goal="Give feedback on the resume to make it stand out in the job market.",
        verbose=True,
        backstory="With a strategic mind and an eye for detail, you excel at providing feedback on resumes to highlight the most relevant skills and experiences."
    )

    resume_advisor = Agent(
        role="Professional Resume Writer",
        goal="Based on the feedback recieved from Resume Advisor, make changes to the resume to make it stand out in the job market.",
        verbose=True,
        backstory= "With a strategic mind and an eye for detail, you excel at refining resumes based on the feedback to highlight the most relevant skills and experiences."
    )

    job_researcher = Agent(
        role="Senior Recruitment Consultant",
        goal="Find the 5 most relevant, recently posted jobs based on the improved resume recieved from resume advisor and the location preference",
        tools=[search_tool],
        verbose=True,
        backstory="""As a senior recruitment consultant your prowess in finding the most relevant jobs based on the resume and location preference is unmatched. 
    You can scan the resume efficiently, identify the most suitable job roles and search for the best suited recently posted open job positions at the preffered location."""
    )

    # Define tasks
    feedback_task = Task(
        description= """Give feedback on the resume to make it stand out for recruiters. 
        Review every section, inlcuding the summary, work experience, skills, and education. Suggest to add relevant sections if they are missing.  
        Also give an overall score to the resume out of 10.  This is the resume: {resume_text}""",
        expected_output="The overall score of the resume followed by the feedback in bullet points.",
        agent=resume_feedback
    )

    rewrite_task = Task(
        description= """Rewrite the resume based on the feedback to make it stand out for recruiters. You can adjust and enhance the resume but don't make up facts. 
        Review and update every section, including the summary, work experience, skills, and education to better reflect the candidates abilities. This is the resume: {resume_text}""",
        expected_output="Resume in markdown format that effectively highlights the candidate's qualifications and experiences",
        agent=resume_advisor,
        context=[feedback_task]
    )

    research_task = Task(
        description="""Find the 5 most relevant recent job postings based on the resume recieved from resume advisor and location preference. This is the preferred location: {location} . 
    Use the tools to gather relevant content and shortlist the 5 most relevant, recent, job openings""",
        expected_output="A bullet point list of the 5 job openings, with the appropriate links and detailed description about each job, in markdown format", 
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
        feedback = feedback_task.output.raw.strip("```markdown").strip("```").strip()
        improved_resume = rewrite_task.output.raw.strip("```markdown").strip("```").strip()
        jobs = research_task.output.raw.strip("```markdown").strip("```").strip()
        
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