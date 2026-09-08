import os
import time
import random
import json
import pandas as pd
from dotenv import load_dotenv
from seleniumbase import Driver

# Load environment variables from .env in fastapi_backend directory
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

GROQ_API_KEY = os.getenv("FASTAPI_GROK_API_KEY")
GROQ_MODEL = os.getenv("FASTAPI_GROK_MODEL")

client = None
if GROQ_API_KEY and GROQ_MODEL:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
    except ImportError:
        pass

# Define dataset path
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'health_schemes.xlsx')

# Target columns to enrich if missing (subcategories intentionally excluded to preserve nulls)
TARGET_COLUMNS = ['Documents', 'Benefits', 'ApplicationProcess', 'Beneficiaries', 'Department']

SECTION_HEADERS = ["Details", "Benefits", "Eligibility", "Application Process", "Documents Required", "Frequently Asked Questions", "Sources And References"]

FIELD_GUIDELINES = {
    'Beneficiaries': "Summarize target beneficiaries into standard, concise comma-separated categories (e.g., 'Individual', 'Family', 'All').",
    'Department': "Extract the governing Nodal Ministry, Department, or State/Central Nodal Authority managing the scheme.",
    'Benefits': "Summarize financial aid, medical coverage, health insurance, subsidies, or general assistance benefits in clean bullet points.",
    'Documents': "List all required application documents as clear bullet points.",
    'ApplicationProcess': "Summarize step-by-step instructions on how to apply."
}

def parse_myscheme_text(lines):
    """Extracts structured sections line-by-line directly from myscheme rendered page body text."""
    start_idx = 0
    for i, line in enumerate(lines):
        if "Check Eligibility" in line or ("Details" in line and i > 15):
            start_idx = i
            break

    current_section = None
    section_lines = {h: [] for h in SECTION_HEADERS}
    
    i = start_idx
    while i < len(lines):
        line_str = lines[i].strip()
        
        matched_header = None
        for h in SECTION_HEADERS:
            if line_str == h:
                matched_header = h
                break
        
        if matched_header:
            current_section = matched_header
            # Skip repeating header line if duplicate
            if i + 1 < len(lines) and lines[i+1].strip() == matched_header:
                i += 1
            # Skip mode badges under Application Process
            if i + 1 < len(lines) and lines[i+1].strip() in ["Online", "Offline"]:
                i += 1
                if i + 1 < len(lines) and lines[i+1].strip() == matched_header:
                    i += 1
        elif current_section:
            if line_str in ["Was this helpful?", "News and Updates", "Share", "©2026"]:
                break
            section_lines[current_section].append(line_str)
        i += 1

    result = {}
    for h, lns in section_lines.items():
        text_str = "\n".join([l for l in lns if l]).strip()
        result[h] = text_str if text_str else None

    return result

def extract_missing_fields_with_llm(full_text, missing_fields, scheme_name):
    """Uses Groq LLM to extract JSON structure for specified missing fields from webpage text."""
    if not client:
        print("  [!] Groq client not initialized (missing API key or package).")
        return None

    fields_to_request = {field: FIELD_GUIDELINES[field] for field in missing_fields if field in FIELD_GUIDELINES}
    guidelines_str = '\n'.join([f'- **{k}**: {v}' for k, v in fields_to_request.items()])
    
    prompt = f"""You are an expert Indian Government Welfare Schemes data extraction assistant.
You are processing webpage text scraped for the scheme: "{scheme_name}".

Extract ONLY the following missing fields:
{guidelines_str}

CRITICAL RULES:
1. Return ONLY a valid JSON object containing keys EXACTLY matching: {json.dumps(list(fields_to_request.keys()))}.
2. If a specific requested field cannot be determined from the webpage text, return null for that key.
3. DO NOT include extra keys not requested.

Webpage Content:
{full_text[:16000]}
"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=GROQ_MODEL,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            error_str = str(e)
            if 'Rate limit reached' in error_str or '429' in error_str:
                print(f"  [~] Rate limit hit. Waiting 35s before retry {attempt + 1}/{max_retries}...")
                time.sleep(35)
            else:
                print(f"  [!] Groq API Error for '{scheme_name}': {e}")
                return None
    return None

def is_cell_empty(val):
    if pd.isna(val) or val is None:
        return True
    if isinstance(val, str) and not val.strip():
        return True
    return False

def main(use_llm=False):
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}")
        return

    df = pd.read_excel(DATASET_PATH)
    
    rows_to_process = []
    for idx, row in df.iterrows():
        missing_fields = [col for col in TARGET_COLUMNS if is_cell_empty(row[col])]
        if missing_fields:
            rows_to_process.append((idx, row, missing_fields))
            
    print(f"Total schemes in dataset: {len(df)}")
    print(f"Found {len(rows_to_process)} schemes with missing target data.")
    
    if not rows_to_process:
        print("No missing data found! All target columns are populated.")
        return

    updated_schemes_count = 0
    driver = Driver(uc=True, headless=True)

    try:
        for count, (idx, row, missing_fields) in enumerate(rows_to_process, 1):
            slug = row['Slug']
            scheme_name = row['SchemeName']
            url = f"https://www.myscheme.gov.in/schemes/{slug}"
            print(f"\n[{count}/{len(rows_to_process)}] Scraping #{idx+1}: '{scheme_name}' ({slug})")
            
            try:
                driver.get(url)
                time.sleep(2.0)
                body_text = driver.find_element("tag name", "body").text
                
                if use_llm:
                    extracted = extract_missing_fields_with_llm(body_text, missing_fields, scheme_name)
                    parsed_map = {
                        'Benefits': extracted.get('Benefits') if extracted else None,
                        'ApplicationProcess': extracted.get('ApplicationProcess') if extracted else None,
                        'Documents': extracted.get('Documents') if extracted else None,
                        'Beneficiaries': extracted.get('Beneficiaries') if extracted else None,
                        'Department': extracted.get('Department') if extracted else None,
                    }
                else:
                    lines = body_text.split("\n")
                    parsed = parse_myscheme_text(lines)
                    parsed_map = {
                        'Benefits': parsed.get('Benefits'),
                        'ApplicationProcess': parsed.get('Application Process'),
                        'Documents': parsed.get('Documents Required'),
                    }

                row_updated = False
                for field in missing_fields:
                    val = parsed_map.get(field)
                    if val and str(val).strip() and str(val).strip().lower() not in ["null", "none"]:
                        if is_cell_empty(df.at[idx, field]):
                            df.at[idx, field] = str(val).strip()
                            print(f"  [+] Filled '{field}': {str(val)[:60]}...")
                            row_updated = True
                
                if row_updated:
                    updated_schemes_count += 1
                    df.to_excel(DATASET_PATH, index=False)
            except Exception as e:
                print(f"  [x] Error scraping {slug}: {e}")

            time.sleep(random.uniform(0.5, 1.0))

    finally:
        driver.quit()

    print(f"\nScraping session finished! Total schemes updated: {updated_schemes_count}")

if __name__ == '__main__':
    main()
