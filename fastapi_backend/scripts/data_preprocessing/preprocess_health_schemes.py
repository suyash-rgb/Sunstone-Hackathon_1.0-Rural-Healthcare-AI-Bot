import pandas as pd
import os
import re

# Define file paths
input_filepath = r'd:\MCA Sage Uni\Semester-3\Project Ideas\ArogyaMitra\fastapi_backend\datasets\health_schemes_565.xlsx'
output_filepath = r'd:\MCA Sage Uni\Semester-3\Project Ideas\ArogyaMitra\fastapi_backend\datasets\health_schemes_565.xlsx'
final_renamed_filepath = r'd:\MCA Sage Uni\Semester-3\Project Ideas\ArogyaMitra\fastapi_backend\datasets\health_schemes.xlsx'

def clean_for_excel(text):
    if not isinstance(text, str):
        return text
    # Remove illegal XML characters that openpyxl rejects
    illegal_xml_chars_re = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')
    return illegal_xml_chars_re.sub('', text)

def filter_health_schemes():
    print(f"Loading dataset from: {input_filepath}")
    try:
        # Load dataset (supports both CSV and Excel)
        if input_filepath.endswith('.csv'):
            df = pd.read_csv(input_filepath)
        else:
            df = pd.read_excel(input_filepath)
        print(f"Original dataset rows: {len(df)}")
        
        # =========================================================================
        # SECTION 1: EXISTING INCLUSION FILTERING LOGIC (KEPT INTACT)
        # =========================================================================
        health_keywords = [
            'health', 'medical', 'hospital', 'maternal', 'pregnant', 'pregnancy', 
            'medicine', 'disability', 'ayushman', 'sanitation', 'wellness', 
            'disease', 'treatment', 'surgery', 'healthcare', 'nutrition', 
            'immunization', 'vaccine', 'clinic', 'patient', 'child care', 'maternity'
        ]
        
        pattern = '|'.join(health_keywords)
        
        health_mask = (
            df['categories'].astype(str).str.contains(pattern, case=False, na=False) |
            df['subcategories'].astype(str).str.contains(pattern, case=False, na=False) |
            df['tags'].astype(str).str.contains(pattern, case=False, na=False) |
            df['scheme_name'].astype(str).str.contains(pattern, case=False, na=False)
        )
        
        health_df = df[health_mask].copy()
        print(f"Filtered health schemes count (Section 1 Inclusion Filter): {len(health_df)}")
        
        # =========================================================================
        # SECTION 2: NEW EXCLUSION FILTERING LOGIC (ADDITIONAL EXCEPTIONS & CLEANUP)
        # =========================================================================
        explicit_exclusions = [
            "ULBs",
            "BC & EBC Girls Residential +2 High School",
            "Burial Ground-Provision of Burial Grounds and Pathway to Burial Grounds",
            "Big Loan Scheme",
            "Coaching Help Scheme for JEE-GUJCET-NEET Exams",
            "Composite Loan Scheme",
            "Chief Minister’s Shasakt Kisan Yojana CM-SKY",
            "Chief Minister's Adarsh Gram Yoiana 2017 cmagy",
            "CHIEF MINISTER  EMPLOYMENT GENERATION  PROGRAMME (CMEGP)",
            "CHIEF MINISTER EMPLOYMENT GENERATION PROGRAMME (CMEGP)",
            "Chief Minister’s Solar Rooftop Capital Incentive Scheme",
            "District Innovation And Challenge Fund",
            "Distribution of Soil Health Card",
            "EAFMAEC",
            "Educational Assistance for Medical and Engineering Courses",
            "Education Loan Scheme - Delhi ELS-DELHI",
            "Financial Assistance for Medical Treatment of Journalists",
            "Financial Assistance to SC Students Studying in Medical, Engineering and Diploma Course for Purchasing Educational Instrument",
            "Financial Assistance to Scheduled Tribe (Plains) Students for Coaching for Getting Admission into Medical/Engineering/IIT/etc.",
            "Financial Assistance to the Teachers/Lecturers Children who taken loan from Nationalised Banks for studying Medical/Engineering Courses",
            "Free Education Scholarship for Professional Courses (Engineering, Medical, Agriculture, Veterinary, and Law)",
            "Food Safety & Standards Authority Of India (FSSAI) Internship Scheme",
            "Go-Green Three Wheelers Scheme (GBOCWWB)",
            "Grant of Mahatma Gandhi Memorial Award for Clean Houses",
            "Fal Podharopan Yojana",
            "Generator Subsidy GS-TN",
            "Jal Jeevan Mission",
            "HSCST Fellowship Programme",
            "Kisan Suryoday Yojana (KSY)",
            "Low Tension Power Tariff (LTPT) Subsidy",
            "Mukhya Mantri Grihini Suvidha Yojana",
            "Maintenance Of Pregnant Desi/Indigenous Cow/Buffalo Ration Scheme For BPL Families Belonging To Scheduled Caste (SC) Category",
            "One Time Settlement (O.T.S.) Scheme",
            "Pratyaksh Hanstantrit Labh / Direct Benefits Transfer For LPG",
            "Pravasi Bharatiya Bima Yojana",
            "Pashu Bima Yojana",
            "Paramparagat Krishi Vikas Yojana",
            "Pradhan Mantri Awas Yojana - Urban",
            "Pradhan Mantri Ujjwala Yojana",
            "Maintenance Of Pregnant Desi Indigenous Cows Ration For BPL Families",
            "Power Subsidy Scheme",
            "Plastic Tunnel (Lo-Tunnel)",
            "RKVY Soil Health and Fertility - Soil Health Card",
            "RKVY Soil Health and Fertility Village level Soil Testing Lab",
            "West Bengal Incentive Scheme for Approved Industrial Park (SAIP) for MSMEs: Incentive for Common Effluent Treatment Plant (CETP)",
            "Scholarship for Engineering and Medical Education",
            "Special Livestock Insurance Scheme",
            "State Medical Scholarship (Scholarship Scheme for MBBS & Allied Courses, Nursing and Paramedical Students)",
            "Scheme on Promotion of Use of Liquid Fermented Organic Manure (LFOM) for Increasing Organic Carbon in Soil",
            "Solar Power Subsidy Scheme",
            "Stipend Scheme (P.B.O.C.W.W.B)",
            "Soil Testing Laboratory"
        ]

        def normalize_text(text):
            if not isinstance(text, str):
                return ""
            return re.sub(r'[^a-z0-9]', '', text.lower())

        normalized_explicit_exclusions = [normalize_text(x) for x in explicit_exclusions if normalize_text(x)]

        def should_exclude(row):
            scheme_name = str(row.get('scheme_name', ''))
            short_title = str(row.get('short_title', ''))
            brief_desc = str(row.get('brief_description', ''))
            desc = str(row.get('description', ''))
            benefits = str(row.get('benefits', ''))
            tags = str(row.get('tags', ''))
            
            norm_name = normalize_text(scheme_name)
            norm_title = normalize_text(short_title)
            norm_bdesc = normalize_text(brief_desc)
            
            # 1. Direct explicit exclusions matching against scheme_name, short_title, and brief_description
            for exc in normalized_explicit_exclusions:
                if exc in norm_name or norm_name in exc:
                    return True, f"Explicit list match ({exc})"
                if norm_title and (exc == norm_title or exc in norm_title):
                    return True, f"Explicit short_title match ({exc})"
                if exc == "ulbs" and "ulbs" in norm_bdesc:
                    return True, "Explicit list match (ULBs)"
            
            # 2. Exclude schemes with animal, animals, or livestock (EXCEPT swine fever medical aid)
            combined_text = f"{scheme_name} {brief_desc} {desc} {benefits} {tags}".lower()
            if re.search(r'\b(animal|animals|livestock)\b', combined_text):
                if "swine" in combined_text:
                    return False, ""  # Keep medical aid for swine fever
                return True, "Animal/Livestock rule match"
                
            return False, ""

        excluded_count = 0
        kept_rows = []

        for idx, row in health_df.iterrows():
            exclude_flag, reason = should_exclude(row)
            if exclude_flag:
                excluded_count += 1
            else:
                kept_rows.append(row)

        final_df = pd.DataFrame(kept_rows)
        print(f"Excluded schemes count: {excluded_count}")
        print(f"Final clean health schemes count (Section 2 Exclusion Filter): {len(final_df)}")
        
        # =========================================================================
        # SECTION 3: DATA PREPROCESSING (Null Handling & Formatting)
        # =========================================================================
        print("Preprocessing data (formatting and null handling)...")
        
        # 1. Ensure short_title columns are in UPPERCASE
        if 'short_title' in final_df.columns:
            final_df['short_title'] = final_df['short_title'].str.upper()
            
        # 3. slug column has all lowercases
        if 'slug' in final_df.columns:
            final_df['slug'] = final_df['slug'].str.lower()
            
        # 4. fill nulls for state with "Pan India" where level == "Central"
        if 'state' in final_df.columns and 'level' in final_df.columns:
            mask_central_null_state = (final_df['level'].str.strip().str.lower() == 'central') & (final_df['state'].isna())
            final_df.loc[mask_central_null_state, 'state'] = 'Pan India'
            
        # 5. for nulls in references column, use "https://www.myscheme.gov.in/schemes/<slug>"
        if 'references' in final_df.columns and 'slug' in final_df.columns:
            mask_null_ref = final_df['references'].isna()
            final_df.loc[mask_null_ref, 'references'] = "https://www.myscheme.gov.in/schemes/" + final_df.loc[mask_null_ref, 'slug']

        # 2. All header row follows CamelCase (e.g. scheme_name -> SchemeName)
        def to_camel_case(snake_str):
            components = str(snake_str).split('_')
            return ''.join(x.title() for x in components)
            
        final_df.columns = [to_camel_case(col) for col in final_df.columns]

        # Clean text columns to avoid openpyxl IllegalCharacterError
        print("Cleaning text for Excel export...")
        for col in final_df.select_dtypes(include=['object']).columns:
            final_df[col] = final_df[col].apply(clean_for_excel)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        
        # Save to health_schemes_565.xlsx first as output_filepath
        print(f"Saving to: {output_filepath}")
        final_df.to_excel(output_filepath, index=False, engine='openpyxl')
        
        # Rename file to health_schemes.xlsx after operation completes
        print(f"Renaming file to: {final_renamed_filepath}")
        if os.path.exists(final_renamed_filepath):
            os.remove(final_renamed_filepath)
        os.replace(output_filepath, final_renamed_filepath)
        
        print("Success! Cleaned health schemes dataset saved and renamed to health_schemes.xlsx.")
        
    except Exception as e:
        print(f"Error processing dataset: {e}")

if __name__ == "__main__":
    filter_health_schemes()
