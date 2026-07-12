from pydantic import BaseModel, Field
from typing import List
from litellm import completion

class CodeIssue(BaseModel):
    file_path: str = Field(description="Name of the affected file")
    line_number: str = Field(description="Approximate line location or code block target")
    issue_type: str = Field(description="Category: Security, Bug, Performance, Style")
    explanation: str = Field(description="Detailed explanation of the flaw and optimization fix")

class PullRequestReview(BaseModel):
    overall_score: int = Field(description="Code health indicator score from 1 to 10")
    critical_flaws: List[CodeIssue] = Field(description="List of detected logic bugs or security faults")
    suggested_docstrings: str = Field(description="Generated clean PEP 257 docstrings for new methods")

def execute_review_graph(raw_diff: str) -> str:
    """Executes code analysis and maps results into clean markdown formatting"""
    
    # FIX: Instruct the model exactly how to map the JSON keys at the absolute root level
    prompt = f"""
    You are an expert principal software architecture reviewer. 
    Analyze the provided unified git diff input and return your complete evaluation strictly as a valid JSON object.
    
    CRITICAL: The JSON object must contain these exact keys at the absolute root level. Do not wrap this data inside a top-level "evaluation", "report", or "result" key.
    
    JSON Schema Template:
    {{
        "overall_score": <int between 1 and 10>,
        "critical_flaws": [
            {{
                "file_path": "<string>",
                "line_number": "<string>",
                "issue_type": "<string>",
                "explanation": "<string>"
            }}
        ],
        "suggested_docstrings": "<string containing clean PEP 257 docstrings for new methods>"
    }}
    
    Git Diff Target Input:
    {raw_diff}
    """
    
    response = completion(
        model="openrouter/openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    raw_content = response.choices[0].message.content.strip()
    
    # Clean out structural markdown code blocks if the LLM returned them
    if raw_content.startswith("```json"):
        raw_content = raw_content.replace("```json", "", 1).rstrip("```").strip()
    elif raw_content.startswith("```"):
        raw_content = raw_content.replace("```", "", 1).rstrip("```").strip()
        
    # Validate the cleaned data string directly against the Pydantic template
    result = PullRequestReview.model_validate_json(raw_content)
    
    # Build clean markdown response payload
    markdown_report = f"## 🤖 Automated Code Review Report (Score: {result.overall_score}/10)\n\n"
    
    if result.critical_flaws:
        markdown_report += "### ⚠️ Detected Code Faults\n"
        for issue in result.critical_flaws:
            markdown_report += f"* **[{issue.issue_type}]** in `{issue.file_path}`:\n  {issue.explanation}\n\n"
    else:
        markdown_report += "✅ No critical structural code flaws detected.\n\n"
        
    if result.suggested_docstrings:
        markdown_report += "### 📝 Auto-Generated Documentation Extensions\n"
        markdown_report += f"```python\n{result.suggested_docstrings}\n```\n"
        
    return markdown_report