import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

styles = getSampleStyleSheet()
style_normal = styles['Normal']
style_heading = styles['Heading1']
style_subheading = styles['Heading2']

def create_pdf(filename, title, content_paragraphs):
    filepath = os.path.join(data_dir, filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    
    story.append(Paragraph(title, style_heading))
    story.append(Spacer(1, 12))
    
    for para in content_paragraphs:
        if isinstance(para, str):
            story.append(Paragraph(para, style_normal))
            story.append(Spacer(1, 12))
        elif isinstance(para, tuple) and para[0] == "sub":
            story.append(Paragraph(para[1], style_subheading))
            story.append(Spacer(1, 6))
        elif isinstance(para, list):
            # assume it's a table data
            t = Table(para)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(t)
            story.append(Spacer(1, 12))
            
    doc.build(story)
    print(f"Created {filename}")

# 1. Project Status Report 1
create_pdf(
    "Project_Alpha_Status_Report_Q1.pdf",
    "Project Alpha - Q1 Status Report",
    [
        "Date: March 31, 2026",
        "Author: John Doe, Project Manager",
     
<truncated 3521 bytes>