import os
import git
import shutil
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="deepseek/deepseek-r1-0528:free", 
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

def clone_repository(repo_url: str):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    local_path = os.path.join(os.getcwd(), "temp_repos", repo_name)
    
    if os.path.exists(local_path):
        shutil.rmtree(local_path)
        
    print(f"Cloning {repo_url}...")
    git.Repo.clone_from(repo_url, local_path)
    return local_path

def get_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None

def generate_docs(repo_path: str):
    documentation = {}
    
    ignore_list = {'.git', '__pycache__', '.venv', 'node_modules', 'venv', '.idea', '.vscode'}
    valid_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.md', '.html', '.css'}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ignore_list]
        
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in valid_extensions:
                relative_path = os.path.relpath(os.path.join(root, file), repo_path)
                
                full_path = os.path.join(root, file)
                code = get_file_content(full_path)
                
                if code:
                    print(f" AI Analyzing structure: {relative_path}...")
                    
                    prompt = f"""
                    You are a Lead Architect. Analyze this file: {relative_path}
                    
                    Provide:
                    1. **Purpose**: What does this file do?
                    2. **Key Logic**: Summary of main functions/classes and don't include any emojis.
                    3. **Integration**: How does it relate to the rest of the app?
                
                    CODE:
                    {code[:3500]} 
                    """
                    
                    try:
                        response = llm.invoke(prompt)
                        clean_content = response.content.split("</think>")[-1].strip()
                        documentation[relative_path] = clean_content
                    except Exception as e:
                        print(f"Error analyzing {relative_path}: {e}")
    
    return documentation