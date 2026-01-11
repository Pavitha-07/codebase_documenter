import os
import shutil
from worker import celery_app
from ai_engine import clone_repository, generate_docs, llm

@celery_app.task(bind=True)
def analyze_repo_task(self, repo_url: str):
    """
    Background task to clone, analyze, and document a GitHub repository.
    """
    try:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(backend_dir, "generated_docs")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        repo_name = repo_url.split("/")[-1].replace(".git", "")
        file_path = os.path.join(output_dir, f"{repo_name}_docs.md")

        self.update_state(state='PROGRESS', meta={'status': 'Cloning Repository...'})
        print(f" Starting process for: {repo_url}")
        local_path = clone_repository(repo_url)

    
        self.update_state(state='PROGRESS', meta={'status': 'AI analyzing every file...'})
        docs_dict = generate_docs(local_path)

        if not docs_dict:
            return {"status": "Failed", "error": "No valid code files found to analyze."}

        
        self.update_state(state='PROGRESS', meta={'status': 'Writing project overview...'})
        print(" Generating Master Summary...")
        
        file_list = list(docs_dict.keys())
        summary_prompt = f"""
        You are a technical writer. Based on this list of files from the '{repo_name}' project:
        {file_list}
        
        Please write:
        1. A high-level overview of what this project does without any emojis.
        2. A 'Quick Start' or 'How to Run' guide based on the file structure without any emojis.
        """
        
        summary_response = llm.invoke(summary_prompt)
        summary_text = summary_response.content.split("</think>")[-1].strip()

        
        full_markdown = f"#  Documentation: {repo_name}\n\n"
        full_markdown += f"**Source:** {repo_url}\n\n"
        full_markdown += f"##  Project Overview\n{summary_text}\n\n"
        full_markdown += "---\n\n"
        full_markdown += "##  Detailed File Analysis\n\n"

        for path, explanation in docs_dict.items():
            full_markdown += f"###  `{path}`\n"
            full_markdown += f"{explanation}\n\n"
            full_markdown += "---\n"

        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_markdown)

        print(f" SUCCESS: File saved at {file_path}")

        
        return {
            "status": "Completed", 
            "file_saved_at": file_path,
            "total_files": len(docs_dict),
            "preview": full_markdown[:1000] 
        }

    except Exception as e:
        print(f" ERROR in Task: {str(e)}")
        return {"status": "Failed", "error": str(e)}