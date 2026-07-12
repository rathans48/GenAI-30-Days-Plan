import os
import httpx
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

async def process_pr_review(pr_data: dict):
    """Async background worker to fetch diff and run agent review loop"""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        diff_url = pr_data["pull_request"]["diff_url"]
        
        # FIX: Dynamically construct the correct timeline conversation comment path
        comments_url = f"{pr_data['pull_request']['issue_url']}/comments"
        
        print(f"🚀 [AGENT] Fetching code diff from: {diff_url}")
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3.diff"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(diff_url, headers=headers)
            if response.status_code != 200:
                print(f"❌ Failed to fetch diff. Status code: {response.status_code}")
                return
            
            raw_diff = response.text
            
            # Trigger Agent Sequence
            review_summary = execute_review_graph(raw_diff)
            
            # Post the markdown analysis back onto the PR
            post_headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            post_res = await client.post(comments_url, headers=post_headers, json={"body": review_summary})
            
            if post_res.status_code == 201:
                print("🎯 [SUCCESS] Review comment posted perfectly to GitHub PR!")
            else:
                print(f"❌ GitHub API post failed: {post_res.status_code} - {post_res.text}")
                
    except Exception as background_err:
        # Expose any hidden errors clearly in your Render console window
        print(f"❌ [BACKGROUND TASK CRASH]: {str(background_err)}")
        import traceback
        traceback.print_exc()

@app.post("/webhook")
async def github_webhook_listener(
    request: Request, 
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None)
):
    # Only evaluate active pull request updates
    if x_github_event != "pull_request":
        return {"status": "ignored", "reason": "Not a pull_request event"}
        
    payload = await request.json()
    action = payload.get("action")
    
    # Intercept when a PR is opened or new commits are pushed
    if action in ["opened", "synchronize"]:
        background_tasks.add_task(process_pr_review, payload)
        return {"status": "processing", "message": "Code review agent dispatched"}
        
    return {"status": "ignored", "reason": f"Action '{action}' not tracked"}