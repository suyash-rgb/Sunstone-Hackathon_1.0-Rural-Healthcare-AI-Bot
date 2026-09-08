import pandas as pd
import os
import re

# Define paths
input_filepath = r'd:\MCA Sage Uni\Hackathon 1.0\datasets\archive-IndianGovtSchemesData-July2026\structured.csv'
output_filepath = r'd:\MCA Sage Uni\Semester-3\Project Ideas\ArogyaMitra\fastapi_backend\datasets\health_schemes_565.xlsx'

def clean_for_excel(text):
    if not isinstance(text, str):
        return text
    # Remove illegal XML characters that openpyxl rejects
    # Excel only allows certain control characters: Tab (9), LF (10), CR (13)
    # The regex below matches any control character that is NOT Tab, LF, or CR
    illegal_xml_chars_re = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')
    return illegal_xml_chars_re.sub('', text)

def filter_health_schemes():
    print(f"Loading dataset from: {input_filepath}")
    try:
        # Load the original dataset
        df = pd.read_csv(input_filepath)
        print(f"Original dataset rows: {len(df)}")
        
        # Define the extended health keywords
        health_keywords = [
            'health', 'medical', 'hospital', 'maternal', 'pregnant', 'pregnancy', 
            'medicine', 'disability', 'ayushman', 'sanitation', 'wellness', 
            'disease', 'treatment', 'surgery', 'healthcare', 'nutrition', 
            'immunization', 'vaccine', 'clinic', 'patient', 'child care', 'maternity'
        ]
        
        # Create regex pattern ignoring case
        pattern = '|'.join(health_keywords)
        
        # Apply filter across relevant columns
        health_mask = (
            df['categories'].str.contains(pattern, case=False, na=False) |
            df['subcategories'].str.contains(pattern, case=False, na=False) |
            df['tags'].str.contains(pattern, case=False, na=False) |
            df['scheme_name'].str.contains(pattern, case=False, na=False)
        )
        
        # Filter dataframe
        health_df = df[health_mask].copy()
        print(f"Filtered health schemes count: {len(health_df)}")
        
        # Clean text columns to avoid openpyxl IllegalCharacterError
        print("Cleaning text for Excel export...")
        for col in health_df.select_dtypes(include=['object']).columns:
            health_df[col] = health_df[col].apply(clean_for_excel)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        
        # Save to Excel
        print(f"Saving to: {output_filepath}")
        health_df.to_excel(output_filepath, index=False, engine='openpyxl')
        
        print("Success! Health schemes dataset saved.")
        
    except Exception as e:
        print(f"Error processing dataset: {e}")

if __name__ == "__main__":
    filter_health_schemes()
