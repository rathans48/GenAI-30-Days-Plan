import os
import json
from typing import List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

# --- 1. TOOL ENGINES (PURE NATIVE PYTHON) ---

def read_unread_inbox_emails() -> list:
    """Queries the mock incoming email database to pull raw customer data structures."""
    return [
        {
            "id": "msg_001",
            "sender": "client.success@enterprise.com",
            "subject": "CRITICAL: Database connection leak detected in production login loop",
            "body": "Hi DevMind support team, we notice our connection pool exhaustion spiking on login routes since yesterday. It drops completely every 4 hours. Please open a tracking issue in our repo."
        },
        {
            "id": "msg_002",
            "sender": "marketing.lead@growth.io",
            "subject": "Question about pricing tables",
            "body": "Can you let me know if there's a bulk discount for an engineering team of 50 users?"
        }
    ]

def create_github_repository_issue(repo_slug: str, title: str, body: str, labels: List[str]) -> dict:
    """Provisions and opens a tracking issue in the targeted repository layout."""
    print(f"\n⚡ [TOOL EXECUTION] Connecting to GitHub API standard routing layer...")
    print(f"⚡ Target Repository: '{repo_slug}'")
    print(f"⚡ Issue Title: {title}")
    print(f"⚡ Assigned Labels: {labels}")
    
    return {
        "status": "success",
        "issue_number": 402,
        "url": f"https://github.com/{repo_slug}/issues/402",
        "state": "open"
    }

# --- 2. ORCHESTRATION CONFIGURATION ---

llm = ChatOpenAI(
    model="openrouter/free",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.0
)

if __name__ == "__main__":
    print("🚀 Initializing Hybrid Tool-Integrated Engineering Router Agent...")
    
    # SYSTEM TURN 1: Programmatically capture data
    print("\n🎬 [STEP 1] Fetching inbox records via native Python execution boundary...")
    raw_emails = read_unread_inbox_emails()
    print(f"✅ Ingested {len(raw_emails)} inbox messages cleanly.")

    # SYSTEM TURN 2: Pass data to LLM for specialized extraction
    print("\n🎬 [STEP 2] Passing records to LLM for bug extraction and payload layout...")
    
    t2_system = (
        "You are DevMind's core triage processing unit.\n"
        "Your task is to analyze the provided inbox JSON data and check for critical engineering system bugs.\n"
        "If a bug is found, you must output a clean text block using the exact structure below:\n\n"
        "TITLE: <write a clean engineering title here>\n"
        "BODY: <write a clean description of the bug here>\n\n"
        "If no critical engineering bug is found, output exactly: 'NO_BUG_DETECTED'.\n"
        "Do not include any JSON brackets, markdown blocks, or extra conversational text."
    )
    
    llm_analysis = llm.invoke([
        SystemMessage(content=t2_system),
        HumanMessage(content=f"Analyze these raw emails and execute formatting rules:\n{json.dumps(raw_emails)}")
    ]).content

    print(f"\n🤖 LLM Analysis Result:\n{llm_analysis.strip()}")

    # SYSTEM TURN 3: Parse simple plain-text keys and map back to Python tool boundaries
    print("\n🎬 [STEP 3] Parsing response strings and routing to GitHub execution gate...")
    
    if "NO_BUG_DETECTED" in llm_analysis:
        print("🛑 No engineering defects found. Halting routing loop pipeline safely.")
        exit()
        
    try:
        # Use clean line-splitting to extract the values effortlessly
        title_line = [line for line in llm_analysis.split('\n') if line.startswith("TITLE:")][0]
        body_line = [line for line in llm_analysis.split('\n') if line.startswith("BODY:")][0]
        
        extracted_title = title_line.replace("TITLE:", "").strip()
        extracted_body = body_line.replace("BODY:", "").strip()
        
        # Fire tool deterministically via Python
        github_metadata = create_github_repository_issue(
            repo_slug="rathan/devmind-core",
            title=extracted_title,
            body=extracted_body,
            labels=["bug", "critical"]
        )
        
    except Exception as e:
        print(f"❌ Structural Parsing Error: Could not slice string lines. Details: {e}")
        exit()

    # SYSTEM TURN 4: Final user confirmation report synthesis
    print("\n🎬 [STEP 4] Synthesizing final sync closure summary report...")
    
    t4_system = (
        "You have completed the ticket triage. Write a friendly, professional final status message "
        "confirming that the issue was opened on GitHub. Include the issue tracking number and URL link.\n"
        f"Operation Details: {json.dumps(github_metadata)}"
    )
    
    final_report = llm.invoke([SystemMessage(content=t4_system)]).content
    
    print("\n" + "="*60)
    print("🎯 FINAL SYSTEM SYNC REPORT:")
    print("="*60 + "\n")
    print(final_report)