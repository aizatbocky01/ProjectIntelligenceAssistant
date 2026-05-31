import os
import glob

for f in glob.glob("backend/**/*.py", recursive=True):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # If the file starts with a newline or some text followed by """ within the first few lines, 
    # but doesn't start with """, it's probably missing its opening quotes due to stripping.
    lines = content.split('\n')
    if len(lines) > 2 and not content.startswith('"""'):
        # Check if one of the first few lines is just """
        if lines[1].strip() == '"""' or lines[2].strip() == '"""' or lines[3].strip() == '"""':
            print(f"Fixing {f}")
            with open(f, 'w', encoding='utf-8') as file:
                file.write('"""' + content)
