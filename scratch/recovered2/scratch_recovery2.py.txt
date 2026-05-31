import json
import os
import re

transcript_path = r"C:\Users\aizat\.gemini\antigravity-ide\brain\b89436de-e424-4fb3-a3f9-0ed9024b9f6a\.system_generated\logs\transcript.jsonl"
os.makedirs("C:/Users/aizat/deployment/gamuda/scratch/recovered2", exist_ok=True)

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
                        path = path.replace("\\\\", "/").replace("\\", "/").replace('\"', '').replace('\'', '').lower()
                        # Clean multiple slashes
                        path = re.sub(r'/+', '/', path)
                        
                        if "deployment/gamuda" in path and not "brain/" in path:
                            rel = path.split("deployment/gamuda/")[-1]
                            dest = f"C:/Users/aizat/deployment/gamuda/scratch/recovered2/{rel.replace('/','_')}.txt"
                            code = code.replace("\\
", "\
").replace("\\\"", "\"").replace("\\\\", "\\").strip('\"\'')
                            if code.startswith("```python\
"):
                                code = code[10:-3]
                            elif code.startswith("```"):
                                code = code.split("\
", 1)[1][:-3]
                                
                   
<truncated 210 bytes>