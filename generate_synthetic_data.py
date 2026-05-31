"""
Script to generate synthetic PDF and CSV/Excel data for the Project Intelligence Assistant.
Run this script to populate the data folder.
"""
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# --------------------------------------------------------------------------- #
# Synthetic CSV/Excel Data
# --------------------------------------------------------------------------- #
def generate_financial_data():
    print("Generating synthetic financial data...")
    data = {
        "Project ID": ["PRJ-001", "PRJ-002", "PRJ-003", "PRJ-004", "PRJ-005"],
        "Project Name": ["Project Alpha", "Project Beta", "Project Gamma", "Project Delta", "Project Epsilon"],
        "Q1 2026 Budget": [500000, 750000, 1200000, 300000, 850000],
        "Q1 2026 Spend": [550000, 700000, 1250000, 280000, 920000],
        "Variance": [50000, -50000, 50000, -20000, 70000],
        "Status": ["Over Budget", "Under Budget", "Over Budget", "Under Budget", "Over Budget"]
    }
    df = pd.DataFrame(data)
    
    csv_path = "data/Q1_Financial_Summary_2026.csv"
    df.to_csv(csv_path, index=False)
    print(f"Created {csv_path}")
    
    # Optionally save as Excel too
    # excel_path = "data/financial_summary_portfolio.xlsx"
    # df.to_excel(excel_path, index=False)
    # print(f"Created {excel_path}")

# --------------------------------------------------------------------------- #
# Synthetic PDF Data
# --------------------------------------------------------------------------- #
def generate_pdf(filename: str, title: str, paragraphs: list):
    path = os.path.join("data", filename)
    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))
    
    # Body
    for para in paragraphs:
        story.append(Paragraph(para, styles['Normal']))
        story.append(Spacer(1, 12))
        
    doc.build(story)
    print(f"Created {path}")

def generate_reports():
    print("Generating synthetic PDF reports...")
    
    # Alpha Status
    generate_pdf(
        "Project_Alpha_Status_Report_Q1.pdf",
        "Project Alpha - Q1 Status Report",
        [
            "Project Alpha is a strategic initiative aimed at upgrading the core infrastructure of the downtown transport hub.",
            "As of Q1 2026, the project is experiencing delays. Supply chain disruptions have caused a 3-week delay in the delivery of critical steel components.",
            "Additionally, unexpected foundational issues during excavation have increased the risk of a 15% budget overrun.",
            "Mitigation plan: The procurement team is sourcing alternative local suppliers for steel, and the engineering team has proposed a revised foundational design to reduce excavation costs."
        ]
    )
    
    # Beta Status
    generate_pdf(
        "Project_Beta_Status_Report_April.pdf",
        "Project Beta - April Status Update",
        [
            "Project Beta involves the development of a new residential complex in the northern suburbs.",
            "The project is currently tracking ahead of schedule and is at 45% completion as of April.",
            "Favorable weather conditions have allowed concrete pouring to proceed faster than anticipated.",
            "The budget is currently in good standing, with savings realized from bulk material purchasing."
        ]
    )
    
    # Risk Register
    generate_pdf(
        "Global_Risk_Register_2026.pdf",
        "2026 Global Risk Register",
        [
            "This document outlines the highest priority risks across all active portfolios.",
            "1. Macroeconomic volatility: Inflation in raw material costs continues to threaten the profit margins of fixed-price contracts.",
            "2. Labor shortages: A lack of skilled electrical contractors in the region is affecting the timelines of Project Gamma and Project Epsilon.",
            "3. Regulatory changes: The upcoming environmental compliance regulations require an immediate audit of all ongoing sites by Q3."
        ]
    )

if __name__ == "__main__":
    generate_financial_data()
    generate_reports()
    print("Synthetic data generation complete.")