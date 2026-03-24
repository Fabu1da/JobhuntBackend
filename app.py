from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from jobspy import scrape_jobs
from dotenv import load_dotenv
from sqlmodel import select

from backend.models.users import plan
from .agent import generate_cover_letter, generate_message_to_recruiter
from backend.models.engine import SessionDep, create_db_and_tables
from backend.authentication import login as auth_login, register as auth_register, subscribe
from backend.schemas import ScoreRequest, BatchScoreRequest, AnalyzeCvRequest, LoginRequest, RegisterRequest, RefreshTokenRequest, PlanRequest, SubscribeRequest, JobEvaluation

from backend.ai_prompts.prompts import CV_ANALYSIS_PROMPT, CV_VISION_PROMPT, evaluation_jobs


import httpx
import os
import re
import json

# Load environment variables from .env file
load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY', '')
model = os.environ.get('model', '')


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get('/api/jobs')
async def get_jobs(query: str, location: str, results: int, posted_within_hours: int):
    
    search_term = query
    location = location
    results_wanted = results

    sites = ['indeed', 'linkedin', 'glassdoor', 'google', 'bayt']  
    
    try:
        print(f"Scraping jobs from: {sites}")
        jobs = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=posted_within_hours,
            country_indeed=location,
            description_format='markdown',
            linkedin_fetch_description=True,
            proxies=None,
            ca_cert=None,
            verbose=1

        )

        print(jobs.head(2))  # Print first 2 jobs for debugging
        
        print(f"Successfully scraped {len(jobs)} jobs")
        
        # Log detailed info about scraped jobs
        if len(jobs) > 0:
            print(f"Available columns: {jobs.columns.tolist()}")
            print(f"\n=== FIRST JOB DETAILS ===")
            first_job = jobs.iloc[0]
            for col in jobs.columns:
                value = first_job.get(col, '')
                if col == 'description':
                    print(f"{col}: {str(value)[:100]}... (length: {len(str(value))})")
                else:
                    print(f"{col}: {value}")
            
        jobs_list = []
        for _, row in jobs.iterrows():
            # Clean description: handle None, nan, and other null values
            desc = row.get('description', '')
            if desc is None or str(desc).lower().strip() in ['nan', 'none', '']:
                desc = ''
            else:
                desc = str(desc)

            jobs_list.append({
                'id': str(_),
                'title': str(row.get('title', '')),
                'company': str(row.get('company', '')),
                'location': str(row.get('location', '')),
                'site': str(row.get('site', '')),
                'job_url': str(row.get('job_url', '')),
                'description': desc,
                'date_posted': str(row.get('date_posted', '')),
                'job_type': str(row.get('job_type', '')),
                'salary_range': f"{row.get('min_amount', '')} - {row.get('max_amount', '')} {row.get('currency', '')}".strip(' -'),
            })

        return {'jobs': jobs_list, 'total': len(jobs_list)}

    except Exception as e:
        print(f"\n=== ERROR SCRAPING JOBS ===")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {'error': str(e), 'jobs': [], 'total': 0}


@app.post('/api/analyzeCv')
async def analyze_cv(request: AnalyzeCvRequest):
   
    print(f"\n=== ANALYZE CV REQUEST ===")
    print(f"API Key present: {bool(api_key)}")
    print(f"Model: {model}")
    print(f"PDF Images provided: {bool(request.pdf_images and len(request.pdf_images) > 0)}")
    if request.pdf_images:
        print(f"Number of PDF images: {len(request.pdf_images)}")
    print(f"CV text length: {len(request.cv_text)}")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        return {
            "name": "Unknown",
            "title": "Professional",
            "experience": "Not specified",
            "skills": [],
            "education": "Not specified",
            "location": "Not specified",
            "summary": "API key not configured. Set OPENAI_API_KEY in .env file."
        }
    
    try:
        async with httpx.AsyncClient() as client:
            # Use vision API if PDF images are provided
            if request.pdf_images and len(request.pdf_images) > 0:
                print(f"Using vision API with {len(request.pdf_images)} page images...")
                content = [{"type": "text", "text": CV_VISION_PROMPT}]
                # Add each page as an image
                for img_base64 in request.pdf_images:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}",
                            "detail": "high"
                        }
                    })
                messages = [{"role": "user", "content": content}]
            else:
                # Fallback to text-based analysis
                print("Using text-based analysis...")
                prompt = CV_ANALYSIS_PROMPT.format(cv_text=request.cv_text[:3000])
                messages = [{"role": "user", "content": prompt}]
            
            res = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": model,
                    "max_tokens": 500,
                    "messages": messages
                },
                timeout=60.0
            )
            data = res.json()
            
            # Check for API errors
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown API error")
                print(f"OpenAI API error: {error_msg}")
                # If vision fails, fallback to text
                if request.pdf_images and request.cv_text:
                    print("Vision failed, falling back to text analysis...")
                    prompt = CV_ANALYSIS_PROMPT.format(cv_text=request.cv_text[:3000])
                    res = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        },
                        json={
                            "model": model,
                            "max_tokens": 500,
                            "messages": [{"role": "user", "content": prompt}]
                        },
                        timeout=30.0
                    )
                    data = res.json()
                    if "error" in data:
                        return {
                            "name": "Unknown",
                            "title": "Professional",
                            "experience": "Not specified",
                            "skills": [],
                            "education": "Not specified",
                            "location": "Not specified",
                            "summary": f"API error: {error_msg[:100]}"
                        }
                else:
                    return {
                        "name": "Unknown",
                        "title": "Professional",
                        "experience": "Not specified",
                        "skills": [],
                        "education": "Not specified",
                        "location": "Not specified",
                        "summary": f"API error: {error_msg[:100]}"
                    }
            
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"API response: {text[:200]}...")
            clean = re.sub(r'```json|```', '', text).strip()
            return json.loads(clean)
    except Exception as e:
        print(f"Error analyzing CV: {e}")
        return {
            "name": "Unknown",
            "title": "Professional",
            "experience": "Not specified",
            "skills": [],
            "education": "Not specified",
            "location": "Not specified",
            "summary": f"Error: {str(e)[:100]}"
        }


@app.post('/api/scoreJob')
async def score_job(request: ScoreRequest):
    profile = request.profile
    job = request.job
    



    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": model,
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": evaluation_jobs(profile, [job])}]
                },
                timeout=30.0
            )
            print(f"\n=== SCORE JOB RESPONSE ===")
            print(f"Status: {res.status_code}")
            data = res.json()
            print(f"Response data: {json.dumps(data, indent=2)[:500]}")
            text = data.get("choices", [{}])[0].get("message", {}).get("content", '[{"score": 50, "summary": "Unable to evaluate."}]')
            print(f"Extracted text: {text[:200]}")
            clean = re.sub(r'```json|```', '', text).strip()
            print(f"Cleaned text: {clean[:200]}")
            raw_result = json.loads(clean)
            # Validate with Pydantic (extract first result from array)
            validated = JobEvaluation(**raw_result[0] if isinstance(raw_result, list) else raw_result)
            result = validated.model_dump()
            print(f"Parsed and validated result: {result}")
            return result
    except Exception as e:
        print(f"\n=== ERROR SCORING JOB ===")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {"score": 0, "summary": "Could not evaluate this listing.", "matched_skills": [], "missing_skills": []}


@app.post('/api/scoreJobs')
async def score_jobs_batch(request: BatchScoreRequest):
    """Score multiple jobs in batches to prevent JSON parsing errors"""
    profile = request.profile
    jobs = request.jobs
    batch_size = 5  # Score 5 jobs per API call to keep response manageable

    try:
        # Split jobs into smaller batches
        job_batches = [jobs[i:i + batch_size] for i in range(0, len(jobs), batch_size)]
        
        print(f"\n=== BATCH SCORE REQUEST ===")
        print(f"Scoring {len(jobs)} jobs in {len(job_batches)} batches of max {batch_size} jobs")
        
        all_scores = []
        
        async with httpx.AsyncClient() as client:
            for batch_idx, job_batch in enumerate(job_batches):
                print(f"\nProcessing batch {batch_idx + 1}/{len(job_batches)}")
                
                res = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": model,
                        "max_tokens": 4000,
                        "messages": [{"role": "user", "content": evaluation_jobs(profile, job_batch)}]
                    },
                    timeout=120.0
                )
                
                print(f"Status code: {res.status_code}")
                data = res.json()
                
                if "error" in data:
                    print(f"API Error: {data['error']}")
                    return {"error": f"API Error in batch {batch_idx + 1}: {data['error']}"}
                
                text = data.get("choices", [{}])[0].get("message", {}).get("content", '[]')
                print(f"Response content length: {len(text)}")
                print(f"First 200 chars: {text[:200]}")
                
                # Clean markdown code blocks
                clean = re.sub(r'```json|```', '', text).strip()
                
                try:
                    raw_scores = json.loads(clean)
                except json.JSONDecodeError as je:
                    print(f"JSON Parse Error in batch {batch_idx + 1}: {str(je)}")
                    print(f"Last 500 chars of response: {clean[-500:]}")
                    # Return partial results with error for failed batch
                    return {
                        "error": f"JSON parsing failed for batch {batch_idx + 1}",
                        "partial_scores": all_scores,
                        "details": str(je)
                    }
                
                # Validate each score with Pydantic
                batch_scores = [JobEvaluation(**score).model_dump() for score in raw_scores]
                print(f"Parsed and validated {len(batch_scores)} scores in this batch")
                all_scores.extend(batch_scores)
        
        # Create a dict for quick lookup
        scores_dict = {s["id"]: s for s in all_scores}
        print(f"Created scores dict with {len(scores_dict)} total scores")
        
        # Return scores in the same order as input jobs
        result = []
        for job in jobs:
            if job.id in scores_dict:
                result.append(scores_dict[job.id])
                print(f"Job {job.id}: Found in scores")
            else:
                result.append({"id": job.id, "score": 0, "summary": "Could not evaluate.", "matched_skills": [], "missing_skills": []})
                print(f"Job {job.id}: NOT found in scores, using default")
        
        print(f"\nFinal scored results ({len(result)} jobs): {result[:2]}...")
        return result
    except Exception as e:
        print(f"\n=== ERROR IN BATCH SCORING ===")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        
        if "ReadTimeout" in type(e).__name__:
            print("API request timed out - the OpenAI API took too long to respond.")
            print("This could mean: API is overloaded, network is slow, or prompt is too large.")
        
        import traceback
        print(f"Full traceback:")
        print(traceback.format_exc())
        # Return default scores for all jobs on error
        return [{"id": job.id, "score": 50, "summary": "Could not evaluate this listing.", "matched_skills": [], "missing_skills": []} for job in jobs]



@app.post('/api/generateCoverLetter')
async def generate_cover_letter_endpoint(request: ScoreRequest):
    profile = request.profile
    job = request.job
    
    try:
        # Convert profile to dict
        profile_data = {
            'name': profile.name,
            'title': profile.title,
            'experience': profile.experience,
            'skills': profile.skills,
            'education': profile.education,
            'location': profile.location,
            'summary': profile.summary
        }
        
        # Convert job to dict
        job_data = {
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'description': job.description
        }
        
        # Call the agent to generate cover letter
        cover_letter = await generate_cover_letter(profile_data, job_data)
        
        print(f"\n=== COVER LETTER GENERATED ===")
        print(f"For: {profile.name} - {job.title}")
        print(f"Letter length: {len(cover_letter)} characters")
        
        return {"coverLetter": cover_letter}
        
    except Exception as e:
        print(f"\n=== ERROR GENERATING COVER LETTER ===")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {"coverLetter": f"Error generating cover letter: {str(e)[:100]}"}
    
@app.post('/api/generateMessageToRecruiter')
async def generate_message_to_recruiter_endpoint(request: ScoreRequest):
    profile = request.profile
    job = request.job
    
    try:
        # Convert profile to dict
        profile_data = {
            'name': profile.name,
            'title': profile.title,
            'experience': profile.experience,
            'skills': profile.skills,
            'education': profile.education,
            'location': profile.location,
            'summary': profile.summary
        }
        
        # Convert job to dict
        job_data = {
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'description': job.description
        }
        
        # Call the agent to generate message to recruiter
        message = await generate_message_to_recruiter(profile_data, job_data)
        
        print(f"\n=== MESSAGE TO RECRUITER GENERATED ===")
        print(f"For: {profile.name} - {job.title}")
        print(f"Message length: {len(message)} characters")
        
        return {"message": message}
        
    except Exception as e:
        print(f"\n=== ERROR GENERATING MESSAGE TO RECRUITER ===")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {"message": f"Error generating message to recruiter: {str(e)[:100]}"}

  
@app.get('/api/health')
async def health_check():
    return {"status": "healthy"}


@app.post('/api/login')
async def login_endpoint(request: LoginRequest, session: SessionDep):
    """Authenticate user with username and password."""
    print(f"\n=== LOGIN REQUEST ===")
    print(f"Username: {request.username}")
    username = request.username
    password = request.password
    return await auth_login(session, username, password)


@app.post('/api/register')
async def register_endpoint(request: RegisterRequest, session: SessionDep):
    """Register a new user with username, password, and email."""
    print(f"\n=== REGISTER REQUEST ===")
    print(f"Username: {request.username}")
    print(f"Email: {request.email}")
    username = request.username
    password = request.password
    email = request.email
    return await auth_register(session, username, password, email)

@app.post('/api/refreshToken')
async def refresh_token(request: RefreshTokenRequest):
    """Refresh JWT token - implementation depends on how you handle refresh tokens."""
    # This is a placeholder. You would need to implement logic to verify the refresh token,
    # check its validity, and issue a new access token.
    return {"token": "new_access_token", "refresh_token": "new_refresh_token"}

@app.get('/api/getplans')
async def get_plans(session: SessionDep):
    """Retrieve all available plans."""
    statement = select(plan)
    plans = session.exec(statement).all()
    return {"plans": plans}

@app.post('/api/plans')
async def create_plan(request: PlanRequest, session: SessionDep):
    """Create a new subscription plan."""
    new_plan = plan(name=request.name, price=request.price, features=request.features)
    session.add(new_plan)
    session.commit()
    session.refresh(new_plan)
    return {"plan": new_plan}

@app.post('/api/subscribe')
async def subscribe_endpoint(request: SubscribeRequest, session: SessionDep):
    """Subscribe a user to a plan."""
    print(f"Subscribing user {request.user_id} to plan {request.plan_id}")
    response = subscribe(session, request.user_id, request.plan_id, request.start_date, request.end_date)
    return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
