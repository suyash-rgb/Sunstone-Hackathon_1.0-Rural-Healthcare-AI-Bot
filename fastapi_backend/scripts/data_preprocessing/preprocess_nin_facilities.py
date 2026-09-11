import pandas as pd
import numpy as np
import os
import re

def clean_phone(val):
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    if val_str in ['\\N', 'NA', '0', '1', '9999999999', '123456', '', ' ']:
        return None
    if 'e+' in val_str.lower():
        try:
            f_val = float(val_str)
            val_str = str(int(f_val))
        except Exception:
            pass
    if val_str.endswith('.0'):
        val_str = val_str[:-2]
    val_clean = re.sub(r'[^0-9\-+]', '', val_str)
    return val_clean if len(val_clean) >= 5 else None

def clean_coord(val):
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    if val_str in ['\\N', 'NA', '0', '0.0', '', ' ']:
        return None
    try:
        f = float(val_str)
        return round(f, 6)
    except Exception:
        return None

def clean_pin(val):
    if pd.isna(val) or val is None:
        return None
    v = str(val).strip()
    if v.endswith('.0'):
        v = v[:-2]
    if '.' in v:
        v = v.split('.')[0]
    return v if len(v) == 6 and v.isdigit() else None

def get_tier_level(facility_type):
    if pd.isna(facility_type):
        return '4_specialized'
    ft = str(facility_type).strip()
    
    tier1 = ['SubCentre', 'Primary Health Centre', 'Urban Health Centre', 'Urban Health Posts', 'Dispensaries', 'Ayush Dispensaries', 'M&CW Center', 'Maternity Home']
    tier2 = ['Community Health Center', 'Sub-District Hospital', 'District Hospital', 'Civil Hospital/General Hospital', '<100 Bedded Hospital', '100-500 Bedded Hospital', 'Referral Hospital', 'Post Partum Unit', 'Women Hospital']
    tier3 = ['Medical Colleges Hospital', '>500 Bedded Hospital']
    
    if ft in tier1:
        return '1_primary'
    elif ft in tier2:
        return '2_secondary'
    elif ft in tier3:
        return '3_tertiary'
    else:
        return '4_specialized'

def preprocess():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_path = os.path.join(base_dir, 'datasets', 'nin-health-facilities.csv')
    output_path = os.path.join(base_dir, 'datasets', 'cleaned_nin_health_facilities.csv')
    
    print(f"Loading raw dataset from {input_path}...")
    df = pd.read_csv(input_path, encoding='latin1', low_memory=False)
    print(f"Original row count: {len(df)}")
    
    text_cols = ['Health Facility Name', 'Address', 'street', 'landmark', 'locality', 'Facility Type', 'State_Name', 'District_Name', 'Taluka_Name', 'Block_Name']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['\\N', 'NA', 'nan', 'NaN', 'None', ''], np.nan)
            
    if 'State_Name' in df.columns:
        df['State_Name'] = df['State_Name'].str.strip()
        df['State_Name'] = df['State_Name'].replace({'Telengana': 'Telangana'})
        
    print("Mapping Facility Tiers...")
    df['tier_level'] = df['Facility Type'].apply(get_tier_level)
    
    print("Cleaning landline numbers...")
    df['landline_number'] = df['landline_number'].apply(clean_phone)
    
    print("Validating spatial coordinates...")
    df['latitude'] = df['latitude'].apply(clean_coord)
    df['longitude'] = df['longitude'].apply(clean_coord)
    
    invalid_mask = (df['latitude'] < 6.0) | (df['latitude'] > 38.0) | (df['longitude'] < 68.0) | (df['longitude'] > 98.0)
    print(f"Setting {invalid_mask.sum()} out-of-bounds coordinates to NULL...")
    df.loc[invalid_mask, 'latitude'] = np.nan
    df.loc[invalid_mask, 'longitude'] = np.nan
    
    if 'pincode' in df.columns:
        df['pincode'] = df['pincode'].apply(clean_pin)
        
    if 'altitude' in df.columns:
        df = df.drop(columns=['altitude'])
        
    print(f"Valid coordinates count: {df['latitude'].notna().sum()} / {len(df)}")
    print(f"Saving preprocessed dataset to {output_path}...")
    
    # Force string format for pincode to prevent float export
    df.to_csv(output_path, index=False, encoding='utf-8')
    print("Preprocessing completed successfully!")

if __name__ == '__main__':
    preprocess()
