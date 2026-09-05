import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


PROFILE = """
Candidate profile:

Education:
- B.E. Electronics and Communication Engineering
- MSc Cloud Computing, National College of Ireland

Certifications:
- AWS Certified Solutions Architect – Associate
- HashiCorp Terraform Associate

Technical skills:
- AWS
- Terraform
- Ansible
- Docker
- Kubernetes
- Helm
- Jenkins
- GitHub Actions
- GitLab CI/CD
- Python
- Bash
- Linux
- REST APIs
- FastAPI
- Redis
- Prometheus
- Grafana
- CloudWatch
- MySQL
- AI/LLM tooling
- Networking fundamentals
- Hardware/electronics troubleshooting
- Raspberry Pi
- Sensors
- Microcontrollers

Target resumes:
A = Cloud / DevOps / AWS
B = Software / Python / Automation
C = IT Support / Technical Support / QA
D = Data Centre / Infrastructure
"""


def analyze_job(job_description):

    prompt = f"""
You are an expert technical recruiter.

Analyze the following job against the candidate profile.

{PROFILE}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON using exactly this structure:

{{
    "eligible": true,
    "match_score": 85,
    "recommended_resume": "A",
    "job_category": "Cloud/DevOps",
    "seniority_match": true,
    "education_match": true,
    "technical_match": 90,
    "location_match": true,
    "visa_concern": false,
    "key_matches": [
        "AWS",
        "Terraform",
        "Docker"
    ],
    "key_gaps": [
        "3 years professional experience"
    ],
    "reason": "Strong match because..."
}}

Rules:

- match_score must be an integer from 0 to 100.
- Do NOT invent candidate experience.
- Do NOT assume professional experience from personal projects.
- Certifications and education can count as relevant qualifications.
- If the job requires something the candidate clearly does not have, identify it as a gap.
- Choose only A, B, C, or D.
- Be conservative about eligibility.
"""


    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    text = interaction.output_text.strip()

    # Remove markdown code fences if Gemini adds them
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)


if __name__ == "__main__":

    test_job = """
    Junior Cloud Engineer

    Dublin, Ireland

    We are looking for a Junior Cloud Engineer to join our infrastructure
    team.

    Requirements:
    - Knowledge of AWS
    - Experience with Terraform
    - Familiarity with Docker and Kubernetes
    - Linux administration
    - Python or Bash scripting
    - Understanding of networking
    - Good communication skills

    Responsibilities:
    - Deploy and maintain AWS infrastructure
    - Automate infrastructure using Terraform
    - Support CI/CD pipelines
    - Monitor cloud infrastructure
    - Troubleshoot production issues

    Graduate and junior candidates are welcome.
    """

    result = analyze_job(test_job)

    print("\n=== AI JOB ANALYSIS ===")
    print(json.dumps(result, indent=4))