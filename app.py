# Warning control
import warnings
warnings.filterwarnings('ignore')


import fitz  # PyMuPDF for PDF processing
import docx  # python-docx for DOCX processing
import gradio as gr
import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool


os.environ['OPENAI_API_KEY'] = os.getenv("openaikey")
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o-mini'
os.environ["SERPER_API_KEY"] = os.getenv("serper_key")



def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file using PyMuPDF."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file using python-docx."""
    doc = docx.Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return "\n".join(fullText)

def extract_text_from_resume(file_path):
    """Determines file type and extracts text."""
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format."



# Agent 1: Resume Strategist
resume_feedback = Agent(
    role="Professional Resume Advisor",
    goal="Give feedback on the resume to make it stand out in the job market.",
    verbose=True,
    backstory="With a strategic mind and an eye for detail, you excel at providing feedback on resumes to highlight the most relevant skills and experiences."
    )


# Task for Resume Strategist Agent: Align Resume with Job Requirements
resume_feedback_task = Task(
    description=(
        """Give feedback on the resume to make it stand out for recruiters. 
        Review every section, inlcuding the summary, work experience, skills, and education. Suggest to add relevant sections if they are missing.  
        Also give an overall score to the resume out of 10.  This is the resume: {resume}"""
    ),
    expected_output="The overall score of the resume followed by the feedback in bullet points.",
    agent=resume_feedback
)

# Agent 2: Resume Strategist
resume_advisor = Agent(
    role="Professional Resume Writer",
    goal="Based on the feedback recieved from Resume Advisor, make changes to the resume to make it stand out in the job market.",
    verbose=True,
    backstory="With a strategic mind and an eye for detail, you excel at refining resumes based on the feedback to highlight the most relevant skills and experiences."
)

# Task for Resume Strategist Agent: Align Resume with Job Requirements
resume_advisor_task = Task(
    description=(
        """Rewrite the resume based on the feedback to make it stand out for recruiters. You can adjust and enhance the resume but don't make up facts. 
        Review and update every section, including the summary, work experience, skills, and education to better reflect the candidates abilities. This is the resume: {resume}"""
    ),
    expected_output= "Resume in markdown format that effectively highlights the candidate's qualifications and experiences",
    # output_file="improved_resume.md",
    context=[resume_feedback_task],
    agent=resume_advisor
)

search_tool = SerperDevTool()


# Agent 3: Researcher
job_researcher = Agent(
    role = "Senior Recruitment Consultant",
    goal = "Find the 5 most relevant, recently posted jobs based on the improved resume recieved from resume advisor and the location preference",
    tools = [search_tool],
    verbose = True,
    backstory = """As a senior recruitment consultant your prowess in finding the most relevant jobs based on the resume and location preference is unmatched. 
    You can scan the resume efficiently, identify the most suitable job roles and search for the best suited recently posted open job positions at the preffered location."""
    )

research_task = Task(
    description = """Find the 5 most relevant recent job postings based on the resume recieved from resume advisor and location preference. This is the preferred location: {location} . 
    Use the tools to gather relevant content and shortlist the 5 most relevant, recent, job openings""",
    expected_output=(
        "A bullet point list of the 5 job openings, with the appropriate links and detailed description about each job, in markdown format" 
    ),
#    output_file="relevant_jobs.md",
    agent=job_researcher
)


crew = Crew(
    agents=[resume_feedback, resume_advisor, job_researcher],
    tasks=[resume_feedback_task, resume_advisor_task, research_task],
    verbose=True
)



def resume_agent(file_path, location):
    resume_text = extract_text_from_resume(file_path)

    result = crew.kickoff(inputs={"resume": resume_text, "location": location})

        # Extract outputs
    feedback = resume_feedback_task.output.raw.strip("```markdown").strip("```").strip()
    improved_resume = resume_advisor_task.output.raw.strip("```markdown").strip("```").strip()
    job_roles = research_task.output.raw.strip("```markdown").strip("```").strip()

    return feedback, improved_resume, job_roles



# with gr.Blocks() as demo:
#     gr.Markdown("# Resume Feedback and Job Matching Tool")
    
#     with gr.Row():
#         with gr.Column():
#             resume_upload = gr.File(label="Upload Your Resume (PDF or DOCX)")
#             location_input = gr.Textbox(label="Preferred Location", placeholder="e.g., San Francisco")
#             submit_button = gr.Button("Submit")
        
#         with gr.Column():
#             feedback_output = gr.Markdown(label="Resume Feedback")
#             improved_resume_output = gr.Markdown(label="Improved Resume")
#             job_roles_output = gr.Markdown(label="Relevant Job Roles")

#     # Define the click event for the submit button
#     def format_outputs(feedback, improved_resume, job_roles):
#         # Add bold headings to each section
#         feedback_with_heading = f"**RESUME FEEDBACK:**\n\n{feedback}"
#         improved_resume_with_heading = f"**IMPROVED RESUME:**\n\n{improved_resume}"
#         job_roles_with_heading = f"**RELEVANT JOB ROLES:**\n\n{job_roles}"
#         return feedback_with_heading, improved_resume_with_heading, job_roles_with_heading

#     submit_button.click(
#         resume_agent,
#         inputs=[resume_upload, location_input],
#         outputs=[feedback_output, improved_resume_output, job_roles_output]
#     ).then(
#         format_outputs,
#         inputs=[feedback_output, improved_resume_output, job_roles_output],
#         outputs=[feedback_output, improved_resume_output, job_roles_output]
#     )

# demo.launch()


# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# Resume Feedback and Job Matching Tool")
    gr.Markdown("*Expected Runtime: 1 Min*")
    
    with gr.Column():
        with gr.Row():
            resume_upload = gr.File(label="Upload Your Resume (PDF or DOCX)", height=120)
            location_input = gr.Textbox(label="Preferred Location", placeholder="e.g., San Francisco")
            submit_button = gr.Button("Submit")
        
        with gr.Column():
            feedback_output = gr.Markdown(label="Resume Feedback")
            improved_resume_output = gr.Markdown(label="Improved Resume")
            job_roles_output = gr.Markdown(label="Relevant Job Roles")

    # Define the click event for the submit button
    def format_outputs(feedback, improved_resume, job_roles):
        # Add bold headings to each section
        feedback_with_heading = f"## Resume Feedback:**\n\n{feedback}"
        improved_resume_with_heading = f"## Improved Resume:\n\n{improved_resume}"
        job_roles_with_heading = f"## Relevant Job Roles:\n\n{job_roles}"
        return feedback_with_heading, improved_resume_with_heading, job_roles_with_heading

#     submit_button.click(
#         resume_agent,
#         inputs=[resume_upload, location_input],
#         outputs=[feedback_output, improved_resume_output, job_roles_output],
#         show_progress=True
#     ).then(
#         format_outputs,
#         inputs=[feedback_output, improved_resume_output, job_roles_output],
#         outputs=[feedback_output, improved_resume_output, job_roles_output]
#     )

# demo.launch()

    submit_button.click(
        lambda: gr.update(value="Processing..."),
        inputs=[],
        outputs=submit_button
    ).then(
        resume_agent,
        inputs=[resume_upload, location_input],
        outputs=[feedback_output, improved_resume_output, job_roles_output]
    ).then(
        format_outputs,
        inputs=[feedback_output, improved_resume_output, job_roles_output],
        outputs=[feedback_output, improved_resume_output, job_roles_output]
    ).then(
        lambda: gr.update(value="Submit"),
        inputs=[],
        outputs=submit_button
    )

demo.queue()
demo.launch()


        