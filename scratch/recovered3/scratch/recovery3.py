import json
import os
import re

transcript_path = r"C:\Users\aizat\.gemini\antigravity-ide\brain\b89436de-e424-4fb3-a3f9-0ed9024b9f6a\.system_generated\logs\transcript.jsonl"
os.makedirs("C:/Users/aizat/deployment/gamuda/scratch/recovered3", exist_ok=True)

for line in open(transcript_path, 'r', encoding='utf-8'):
    if "write_to_file" not in line: continue
    try:
        entry = json.loads(line)
        if entry.get("type") != "PLANNER_RESPONSE": continue
        for call in (entry.get("tool_calls") or []):
            if "write_to_file" in call.get("name", ""):
                args = call.get("args")
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except: pass
                
                if isinstance(args, dict):
                    path = args.get("TargetFile", "")
                    code = args.get("CodeContent", "")
                    if path and code:
                        # Clean path
                        path = path.replace("\\\\", "/").replace("\\", "/").replace('\"', '').replace('\'', '')
                        # Keep original case for filename, but use lower for matching
                        
                        path_clean = re.sub(r'/+', '/', path)
                        
                        if "deployment/gamuda" in path_clean.lower() and not "brain/" in path_clean.lower():
                            # Find index of deployment/gamuda/ case-insensitively
                            idx = path_clean.lower().find("deployment/gamuda/")
                            rel = path_clean[idx + len("deployment/gamuda/"):]
                            
                            dest = f"C:/Users/aizat/deployment/gamuda/scratch/recovered3/{rel}"
                            os.makedirs(os.path.dirname(dest), exist_ok=True)
                            
                            code = code.replace("\\
", "\
").repl
<truncated 591 bytes>