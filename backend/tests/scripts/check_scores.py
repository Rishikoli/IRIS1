
import pandas as pd
import os
import glob
import warnings

warnings.filterwarnings('ignore')

# Directory containing reports
reports_dir = "/home/aditya/Downloads/IRIS/backend/reports"

# Find all xlsx files
xlsx_files = glob.glob(os.path.join(reports_dir, "*.xlsx"))

print(f"Found {len(xlsx_files)} reports. Checking for scores...")

found_match = False

for file_path in xlsx_files:
    try:
        company_name = os.path.basename(file_path).split('_')[3]
        xls = pd.ExcelFile(file_path)
        
        # Check all sheets for "Overall Compliance Score" or similar
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Convert to string and search for score
            # Looking for a cell that might contain the score
            # Let's try to find a row with "Overall Compliance Score"
            
            # Simple string search in the dataframe content
            # This is robust against layout changes
            mask = df.astype(str).apply(lambda x: x.str.contains('Overall Compliance Score', case=False, na=False)).any(axis=1)
            
            if mask.any():
                # Get the row
                row = df[mask].iloc[0]
                # Try to find the number in that row
                # Assuming the score is in the next column or valid number
                row_str = row.astype(str).tolist()
                for item in row_str:
                    try:
                        score = float(item)
                        # Filter out the row label itself if it was converted to nan/float somehow or just check value
                        if score <= 100:
                            print(f"Company: {company_name}, Score: {score}, File: {os.path.basename(file_path)}")
                            if score == 75.0:
                                print(f"*** MATCH FOUND: {company_name} ***")
                                found_match = True
                    except ValueError:
                        continue
            
            # Also check specifically for just "75" if the above fails but we suspect it's there
            # (less reliable)

    except Exception as e:
        # print(f"Error reading {file_path}: {e}")
        pass

if not found_match:
    print("No exact match for 75 score found in existing reports.")
