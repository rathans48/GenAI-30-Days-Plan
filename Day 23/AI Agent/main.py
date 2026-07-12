import os
import httpx
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

async def process_pr_review(pr_data: dict):
    """Async background worker to fetch diff and run agent review loop"""
    diff_url = pr_data["pull_request"]["diff_url"]
    comments_url = pr_data["pull_request"]["comments_url"]
    
    # Fetch the raw code diff from GitHub
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(diff_url, headers=headers)
        if response.status_code != 200:
            return
        
        raw_diff = response.text
        
        # Trigger Agent Node Sequence
        review_summary = execute_review_graph(raw_diff)
        
        # Post the markdown analysis back onto the PR
        post_headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        await client.post(comments_url, headers=post_headers, json={"body": review_summary})

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