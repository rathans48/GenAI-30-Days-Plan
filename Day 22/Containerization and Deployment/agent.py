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
    
    prompt = f"""
    You are an expert principal software architecture reviewer. Analyze the following unified git diff input:
    
    {raw_diff}
    
    Identify potential bugs, architectural flaws, missing resource cleanup wrappers, or performance bottlenecks. 
    Additionally, generate clean docstrings for any newly introduced functions or modules.
    """
    
    # Force JSON structured schema extraction using LiteLLM/OpenRouter
    response = completion(
        model="openrouter/openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format=PullRequestReview
    )
    
    # Parse output schema straight into formatting generators
    result = PullRequestReview.model_validate_json(response.choices[0].message.content)
    
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