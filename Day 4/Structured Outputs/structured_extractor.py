import os
import json
from enum import Enum
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment configurations
load_dotenv(".env")

class ProjectDifficulty(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class TechnicalSkill(BaseModel):
    name: str = Field(description="The formal name of the language, tool, or framework.")
    proficiency: str = Field(description="Self-taught, academic, or production exposure.")

class ProjectBreakdown(BaseModel):
    title: str = Field(description="The clean title of the development project.")
    difficulty: ProjectDifficulty = Field(description="The calculated engineering complexity.")
    languages_used: List[str] = Field(description="Array of programming languages identified.")
    core_summary: str = Field(description="A concise one-sentence description of the system architecture.")

# Master schema model class
class DeveloperProfile(BaseModel):
    developer_name: Optional[str] = Field(default="Unknown", description="Extract full legal name if available.")
    primary_focus: str = Field(description="The primary technical focus area, e.g., Backend, Embedded, Data Science.")
    skills_inventory: List[TechnicalSkill] = Field(description="List of all detected technologies.")
    portfolio: List[ProjectBreakdown] = Field(description="Array of all valid software projects found.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def extract_profile_data(unstructured_text):
    print("Sending text data to parsing engine via Strict OpenRouter JSON Schema...")
    try:
        # Generate the baseline JSON schema properties from our Pydantic structure
        json_schema = DeveloperProfile.model_json_schema()
        
        response = client.chat.completions.create(
            model="openrouter/free", 
            messages=[
                {
                    "role": "system",
                    "content": "You are a core metadata parsing engine. Extract structural details from the user text input. Respond ONLY with a raw JSON structure matching the schema specification precisely."
                },
                {"role": "user", "content": unstructured_text}
            ],
            # Use the strict open-specification json_schema enforcement layer
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "DeveloperProfileSchema",
                    "strict": True, # Enforces strict property matching
                    "schema": json_schema
                }
            }
        )
        
        # Capture text string from network output channel
        raw_json_string = response.choices[0].message.content
        parsed_dict = json.loads(raw_json_string)
        
        # Instantiate and validate through Pydantic to ensure type safety
        validated_profile = DeveloperProfile(**parsed_dict)
        return validated_profile

    except Exception as e:
        print(f"Schema Validation or Generation Failure: {e}")
        return None

if __name__ == "__main__":
    sample_resume_dump = """
    Greetings, I am a software engineer focused on distributed systems engineering and automated 
    data analytics pipelines. My technical expertise spans developing full-stack web architectures, 
    designing cloud-native infrastructure, and implementing scalable microservices. In terms of past 
    work, I designed a high-throughput E-Commerce Transaction Engine using Go, leveraging the Gin 
    framework, gRPC protocols, and highly optimized PostgreSQL relational storage instances. Additionally, 
    I engineered an automated log parsing utility in Python utilizing asynchronous loops and complex 
    regex filters to handle stream processing for network observability platforms.
    """
    
    profile = extract_profile_data(sample_resume_dump)
    
    if profile:
        print("\n=== SYSTEM INGESTION COMPLETE (Type-Safe Python Object) ===")
        print(f"Developer Name: {profile.developer_name}")
        print(f"Primary Focus:  {profile.primary_focus}")
        
        print("\n--- Verified Skills ---")
        for skill in profile.skills_inventory:
            print(f" • {skill.name} ({skill.proficiency})")
            
        print("\n--- Project Portfolio Matrix ---")
        for proj in profile.portfolio:
            print(f"\n📁 Project: {proj.title} [{proj.difficulty.value}]")
            print(f"   Languages: {', '.join(proj.languages_used)}")
            print(f"   Summary:   {proj.core_summary}")