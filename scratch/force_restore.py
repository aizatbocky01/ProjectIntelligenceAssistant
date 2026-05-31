import json
import os

transcript_path = r"C:\Users\aizat\.gemini\antigravity-ide\brain\b89436de-e424-4fb3-a3f9-0ed9024b9f6a\.system_generated\logs\transcript.jsonl"
os.makedirs("C:/Users/aizat/deployment/gamuda/scratch/recovered", exist_ok=True)

count = 0
for line in open(transcript_path, 'r', encoding='utf-8'):
    if "write_to_file" not in line: continue
    
    try:
        entry = json.loads(line)
        for call in entry.get("tool_calls", []):
            if "write_to_file" in call.get("name", ""):
                args = call.get("args", {})
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except: pass
                
                if isinstance(args, dict):
                    path = args.get("TargetFile", "")
                    code = args.get("CodeContent", "")
                    if path and code:
                        path = path.strip('\"\'').replace("\\", "/")
                        if "deployment/gamuda" in path.lower() and not "brain/" in path.lower():
                            rel = path.lower().split("deployment/gamuda/")[-1]
                            dest = f"C:/Users/aizat/deployment/gamuda/scratch/recovered/{rel.replace('/','_')}.txt"
                            code = code.strip('\"\'')
                            if code.startswith("```python\\
"):
                                code = code[10:-3]
                            code = code.replace("\\
", "\
").replace("\\\"", "\"").replace("\\\\", "\\")
                            with open(dest, "w", encoding="utf-8") as out:
                                out.write(code)
                            count += 1
                            print(f"Recovered {rel}")
    except Exception as e:
        pass

print(f"Total recovered: {count}")
