
import pandas as pd
import os
import glob
import warnings

warnings.filterwarnings('ignore')

reports_dir = "/home/aditya/Downloads/IRIS/backend/reports"
xlsx_files = glob.glob(os.path.join(reports_dir, "*.xlsx"))

print(f"Found {len(xlsx_files)} reports. Inspecting content...")

for file_path in xlsx_files:
    try:
        company_name = os.path.basename(file_path).split('_')[3]
        xls = pd.ExcelFile(file_path)
        
        found_in_file = False
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            # Search for any cell containing "Score"
            # df.stack() creates a Series of all values
            # str.contains check
            
            # Print any cell that has "Score" in it
            for idx, row in df.iterrows():
                for col in df.columns:
                    val = str(row[col])
                    if "score" in val.lower():
                        # Try to find a number in this row or next column
                        # print(f"File: {company_name}, Found '{val}' in sheet {sheet_name}")
                        
                        # Check neighboring cells for numbers
                        # If this cell is "Overall Compliance Score", check next col
                        if "overall compliance score" in val.lower():
                            print(f"\n[POTENTIAL] File: {company_name}, Sheet: {sheet_name}")
                            # Print the whole row
                            print(f"Row: {row.values}")
                            found_in_file = True
            
            if found_in_file: break

    except Exception as e:
        # print(f"Error {file_path}: {e}")
        pass
