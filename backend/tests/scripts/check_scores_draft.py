
import pandas as pd
import os
import glob

# Directory containing reports
reports_dir = "/home/aditya/Downloads/IRIS/backend/reports"

# Find all xlsx files
xlsx_files = glob.glob(os.path.join(reports_dir, "*.xlsx"))

print(f"Found {len(xlsx_files)} reports.")

for file_path in xlsx_files:
    try:
        # Read the Excel file - trying different sheets or looking for a score cell
        # Usually reports might have a Summary sheet
        xls = pd.ExcelFile(file_path)
        
        score_found = False
        company_name = os.path.basename(file_path).split('_')[3] # IRIS_Forensic_Report_COMPANY_...
        
        # Heuristic search for "Compliance Score" or similar
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Convert to string and search
            # Look for explicit 75 or "score"
            # Assuming format might be key-value
            
            # Let's just dump the dataframe str and search for "Score"
            df_str = df.to_string()
            if "Compliance Score" in df_str or "Overall Score" in df_str:
                # Try to extract exact value if easy, or just print the row
                # For now, let's just inspect the content if we find "Score"
                 pass
        
        # Since I cannot easily parse variable formats blindly, I will look for recent files and try to read a specific cell if I know the format.
        # But 'ComplianceAssessment' creates a dictionary. The Excel report generation likely puts it in a specific place.
        # Let's read `backend/src/utils/report_generator.py` (guessing) or similar to see structure.
        # Check `test_report_generation.py` to see how reports are made.
        pass

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

# Instead of complex parsing, I'll just check if I can find the report generator code to understand the output format.
