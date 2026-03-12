from agents import Agent, ModelSettings, TResponseInputItem, Runner, RunConfig, trace
from pydantic import BaseModel

jobsuche = Agent(
  name="JobSuche",
  instructions="""You are an AI assistant that helps users create tailored cover letters for job applications.

Your task is to generate a professional and personalized cover letter using the job description and the candidate's resume provided in the conversation.

You must carefully analyze both inputs and create a cover letter that clearly explains why the candidate is a strong fit for the position.

Responsibilities:

1. Analyze the job description to identify:
- Required skills
- Key responsibilities
- Important qualifications
- Company values and keywords

2. Analyze the candidate's resume to identify:
- Relevant work experience
- Skills that match the job requirements
- Achievements and measurable results
- Education and certifications if relevant

3. Match the candidate's background with the requirements of the role.

4. Write a tailored cover letter that highlights the candidate’s most relevant experiences and strengths.

Cover Letter Structure:

Opening Paragraph
- Mention the position the candidate is applying for.
- Express enthusiasm for the company or role.
- Briefly introduce the candidate.

Body Paragraphs
- Highlight 2–3 relevant experiences from the resume.
- Connect the candidate’s skills and achievements to the job requirements.
- Use concrete examples when possible.

Closing Paragraph
- Reaffirm interest in the position.
- Mention willingness to discuss the opportunity further.
- End with a professional closing.

Style Guidelines:

- Length should be between 150 and 250 words.
- Use a professional, clear, and confident tone.
- Avoid repeating the resume word-for-word.
- Focus on how the candidate adds value to the company.
- Use concise and natural language.

Output Format:

Return only the cover letter text formatted like this:

Dear Hiring Manager,

[Generated cover letter]

Best regards,
[Candidate Name]

Important Rules:

- Do not invent experiences or qualifications.
- Only use information present in the resume.
- If the hiring manager name is not available, use \"Dear Hiring Manager\".
- Always tailor the letter specifically to the job description.""",
  model="gpt-4o-mini",
  model_settings=ModelSettings(
    temperature=1,
    top_p=1,
    max_tokens=2048,
    store=True
  )
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  with trace("Cover Letter Agent"):
    state = {

    }
    workflow = workflow_input.model_dump()
    conversation_history: list[TResponseInputItem] = [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": workflow["input_as_text"]
          }
        ]
      }
    ]
    jobsuche_result_temp = await Runner.run(
      jobsuche,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_69a6e7fc90bc8190a34e6cc6a583a3f906482cd9b8eb4d17"
      })
    )

    conversation_history.extend([item.to_input_item() for item in jobsuche_result_temp.new_items])

    jobsuche_result = {
      "output_text": jobsuche_result_temp.final_output_as(str)
    }
    return jobsuche_result


# Function to generate cover letter using the agent
async def generate_cover_letter(profile_data: dict, job_data: dict) -> str:
  """
  Generate a cover letter using the JobSuche agent.
  
  Args:
      profile_data: Dict with name, title, experience, skills, education, location, summary
      job_data: Dict with title, company, location, description
  
  Returns:
      Generated cover letter text
  """
  # Format the input as a combined text prompt for the agent
  profile_text = f"""Name: {profile_data.get('name', 'Candidate')}
Title: {profile_data.get('title', '')}
Experience: {profile_data.get('experience', '')}
Skills: {', '.join(profile_data.get('skills', []))}
Education: {profile_data.get('education', '')}
Location: {profile_data.get('location', '')}
Summary: {profile_data.get('summary', '')}"""

  job_text = f"""Job Title: {job_data.get('title', '')}
Company: {job_data.get('company', 'Unknown')}
Location: {job_data.get('location', 'Not specified')}
Description: {job_data.get('description', 'No description available')}"""

  input_text = f"""Please create a professional cover letter for this job application:

CANDIDATE PROFILE:
{profile_text}

JOB LISTING:
{job_text}

Generate a tailored cover letter that highlights the candidate's relevant experience."""

  # Call the agent with the formatted input
  workflow_input = WorkflowInput(input_as_text=input_text)
  result = await run_workflow(workflow_input)
  
  return result.get("output_text", "Failed to generate cover letter")


async def generate_message_to_recruiter(profile_data: dict, job_data: dict) -> str:
  """
  You are an AI assistant that helps users create a professional message to recruiters when applying for a job.
  this function uses the JobSuche agent to generate a concise and polite message expressing interest in the position and highlighting the candidate's relevant experience, based on the candidate's profile and the job listing.

  this message will be sent before the application is made, or when asking if the position is still open, or if the recruiter is available for a quick chat.
  this has to be short and concise, ideally no more than 100 words, and should be polite and professional.
   
  you should analyze the job description and check if there is a recruiter name mentioned, if not, use "Dear Hiring Manager" as the greeting.
  if exist,
  you should also check for his email or LinkedIn profile, and if exist, you should mention that you will reach out to him directly on LinkedIn or via email, and ask for the best way to contact him.

  
  Args:
      profile_data: Dict with name, title, experience, skills, education, location, summary
      job_data: Dict with title, company, location, description
  
  Returns:
      Generated message text
  """
  # Format the input as a combined text prompt for the agent
  profile_text = f"""Name: {profile_data.get('name', 'Candidate')}
Title: {profile_data.get('title', '')}
Experience: {profile_data.get('experience', '')}
Skills: {', '.join(profile_data.get('skills', []))}
Education: {profile_data.get('education', '')}
Location: {profile_data.get('location', '')}
Summary: {profile_data.get('summary', '')}""" 
  
  job_text = f"""Job Title: {job_data.get('title', '')}
Company: {job_data.get('company', 'Unknown')}
Location: {job_data.get('location', 'Not specified')}
Description: {job_data.get('description', 'No description available')}""" 
  
  input_text = f"""Please create a professional message to the recruiter for this job application:
CANDIDATE PROFILE:
{profile_text}  
JOB LISTING:
{job_text}  
Generate a concise and polite message expressing interest in the position and highlighting the candidate's relevant experience."""

  # Call the agent with the formatted input
  workflow_input = WorkflowInput(input_as_text=input_text)
  result = await Runner.run(
    jobsuche,
    input=[
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": input_text
          }
        ]
      }
    ],
    run_config=RunConfig(trace_metadata={
      "__trace_source__": "agent-builder",
      "workflow_id": "wf_69a6e7fc90bc8190a34e6cc6a583a3f906482cd9b8eb4d17"
    })
  )
  
  return result.final_output_as(str)