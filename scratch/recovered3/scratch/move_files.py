import os
import shutil

src_dir = "C:/Users/aizat/deployment/gamuda/scratch/recovered2"
dest_dir = "C:/Users/aizat/deployment/gamuda"

for file in os.listdir(src_dir):
    if not file.endswith(".txt"): continue
    # backend_app_agents_graph.py.txt
    rel_path = file[:-4].replace('_', '/')
    
    # Special cases where folders had underscores in them? None in this project.
    # Wait, __init__.py becomes __init__.py, which had underscores! 
    # But replacing _ with / makes it //init//.py.
    # Let me just rename them manually or handle it properly.
