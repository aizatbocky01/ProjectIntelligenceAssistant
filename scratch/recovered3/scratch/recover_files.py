import json
import os
import ast

transcript_path = r"C:\Users\aizat\.gemini\antigravity-ide\brain\b89436de-e424-4fb3-a3f9-0ed9024b9f6a\.system_generated\logs\transcript.jsonl"
recovered_files = {}

# Pass 1: Extract from write_to_file
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
            
        if entry.get("source") == "MODEL" and entry.get("type") == "PLANNER_RESPONSE":
            for call in entry.get("tool_calls", []):
                if call.get("name") == "write_to_file":
                    args = call.get("args", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except:
                            pass
                    
                    path = args.get("TargetFile", "")
                    code = args.get("CodeContent", "")
                    
                    if isinstance(path, str) and isinstance(code, str) and path and code:
                        # Clean quotes
                        path = path.strip('\"\'')
                        path = path.replace("\\", "/").lower()
                        code = code.strip('\"\'')
                        if code.startswith("```python\
"):
                            code = code[10:-3]
                        elif code.startswith("```"):
                            code = code.split("\
", 1)[1][:-3]
                        # Sometimes code has escaped newlines if it wasn't parsed correctly
                        try:
                            code = ast.literal_eval('"' + code.replace('"', '\\"') + '"')
                        except:
                            pass
                        
                        recovered_files[path] = code

# Pass 2: Extract from view_file (to get the latest s
<truncated 3196 bytes>