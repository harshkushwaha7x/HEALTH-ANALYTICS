"""
Synthetic data generator for Health Analytics.
Creates realistic patient records with lab values, imaging, genomics, and clinical notes.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os


# Sample data pools
FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Christopher', 'Karen', 'Charles', 'Nancy', 'Daniel', 'Lisa'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White'
]

BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

CONDITIONS = [
    'Type 2 Diabetes Mellitus',
    'Essential Hypertension',
    'Hyperlipidemia',
    'Obesity',
    'Coronary Artery Disease',
    'Chronic Kidney Disease Stage 3',
    'Depression',
    'Anxiety Disorder',
    'Osteoarthritis',
    'GERD',
    'Asthma',
    'Hypothyroidism'
]

MEDICATIONS = [
    'Metformin 500mg BID',
    'Lisinopril 10mg daily',
    'Atorvastatin 20mg daily',
    'Metoprolol 25mg BID',
    'Aspirin 81mg daily',
    'Omeprazole 20mg daily',
    'Levothyroxine 50mcg daily',
    'Amlodipine 5mg daily',
    'Gabapentin 300mg TID',
    'Losartan 50mg daily'
]

SYMPTOMS = [
    'intermittent chest discomfort',
    'occasional shortness of breath',
    'mild fatigue',
    'joint stiffness',
    'sleep disturbances',
    'frequent urination',
    'increased thirst',
    'mild headaches'
]

CLINICAL_NOTE_TEMPLATES = [
    """Patient presents for routine follow-up. Currently managing {conditions}. 
Current medications include {medications}. 
Patient reports {symptoms}. 
Vital signs: BP {bp}, HR {hr}, Weight {weight} lbs.
Lab results reviewed. A1C at {a1c}%, showing {a1c_trend} from previous.
Plan: Continue current medications. Follow-up in 3 months. Dietary counseling provided.""",

    """Follow-up visit for chronic disease management. 
Active conditions: {conditions}.
Medication list: {medications}.
Chief complaint: {symptoms}.
Physical exam: VS stable. BP {bp}, pulse {hr}.
Assessment: Patient's {primary_condition} is {status}.
Plan: Maintain current regimen. Repeat labs in 6 weeks.""",

    """Comprehensive health evaluation.
Medical history significant for {conditions}.
Current medications: {medications}.
Review of systems: Reports {symptoms}.
Vitals today: Blood pressure {bp}, heart rate {hr}, BMI {bmi}.
Recent A1C: {a1c}% - {a1c_interpretation}.
Cholesterol panel reviewed - LDL {ldl}, HDL {hdl}.
Impression: Overall health status is {overall_status}.
Recommendations: {recommendations}"""
]


def generate_patient(patient_id: int, seed: int = None) -> Dict[str, Any]:
    """Generate a synthetic patient with demographics."""
    if seed is not None:
        random.seed(seed + patient_id)
    
    gender = random.choice(['Male', 'Female'])
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Generate age between 25 and 85
    age = random.randint(25, 85)
    birth_year = datetime.now().year - age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    
    return {
        'id': patient_id,
        'name': f'{first_name} {last_name}',
        'date_of_birth': f'{birth_year}-{birth_month:02d}-{birth_day:02d}',
        'gender': gender,
        'age': age,
        'email': f'{first_name.lower()}.{last_name.lower()}@email.com',
        'phone': f'+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}',
        'address': f'{random.randint(100,9999)} {random.choice(["Main", "Oak", "Maple", "Cedar", "Pine"])} {random.choice(["St", "Ave", "Blvd", "Dr"])}',
        'blood_type': random.choice(BLOOD_TYPES),
        'emergency_contact': f'{random.choice(FIRST_NAMES)} {last_name}'
    }


def generate_lab_history(patient_id: int, num_records: int = 10, 
                         patient_profile: str = 'normal', seed: int = None) -> List[Dict[str, Any]]:
    """Generate historical lab values for a patient.
    
    Args:
        patient_id: Patient identifier
        num_records: Number of historical records to generate
        patient_profile: 'normal', 'prediabetic', 'diabetic', 'cardiac_risk'
        seed: Random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed + patient_id)
    
    records = []
    base_date = datetime.now() - timedelta(days=365 * 2)  # Start 2 years ago
    
    # Set baseline values based on profile
    profiles = {
        'normal': {
            'a1c': (5.0, 5.5, 0.1),  # (base, variation, trend)
            'glucose': (85, 95, 2),
            'ldl': (80, 100, 3),
            'hdl': (55, 65, 2),
            'triglycerides': (100, 130, 5),
            'bp_sys': (110, 120, 3),
            'bp_dia': (70, 78, 2)
        },
        'prediabetic': {
            'a1c': (5.8, 6.2, 0.15),
            'glucose': (105, 120, 5),
            'ldl': (110, 130, 5),
            'hdl': (40, 50, 3),
            'triglycerides': (150, 180, 10),
            'bp_sys': (125, 135, 5),
            'bp_dia': (80, 88, 3)
        },
        'diabetic': {
            'a1c': (7.0, 8.5, 0.2),
            'glucose': (140, 180, 15),
            'ldl': (130, 160, 8),
            'hdl': (35, 45, 2),
            'triglycerides': (180, 250, 15),
            'bp_sys': (135, 150, 8),
            'bp_dia': (85, 95, 5)
        },
        'cardiac_risk': {
            'a1c': (5.5, 6.0, 0.1),
            'glucose': (95, 110, 3),
            'ldl': (150, 190, 10),
            'hdl': (30, 40, 2),
            'triglycerides': (200, 300, 20),
            'bp_sys': (145, 165, 10),
            'bp_dia': (90, 100, 5)
        }
    }
    
    profile = profiles.get(patient_profile, profiles['normal'])
    
    for i in range(num_records):
        record_date = base_date + timedelta(days=i * (730 // num_records))
        trend_factor = i / num_records  # Gradual progression
        
        def gen_value(key):
            low, high, trend = profile[key]
            base = random.uniform(low, high)
            return round(base + (trend * trend_factor * random.choice([-1, 1])), 1)
        
        # Generate A1C
        records.append({
            'patient_id': patient_id,
            'lab_type': 'A1C',
            'value': gen_value('a1c'),
            'unit': '%',
            'reference_low': 4.0,
            'reference_high': 5.6,
            'recorded_at': record_date.isoformat()
        })
        
        # Generate Glucose
        records.append({
            'patient_id': patient_id,
            'lab_type': 'GLUCOSE',
            'value': gen_value('glucose'),
            'unit': 'mg/dL',
            'reference_low': 70,
            'reference_high': 100,
            'recorded_at': record_date.isoformat()
        })
        
        # Generate Cholesterol (less frequent)
        if i % 2 == 0:
            records.append({
                'patient_id': patient_id,
                'lab_type': 'LDL',
                'value': gen_value('ldl'),
                'unit': 'mg/dL',
                'reference_low': 0,
                'reference_high': 100,
                'recorded_at': record_date.isoformat()
            })
            
            records.append({
                'patient_id': patient_id,
                'lab_type': 'HDL',
                'value': gen_value('hdl'),
                'unit': 'mg/dL',
                'reference_low': 40,
                'reference_high': 999,
                'recorded_at': record_date.isoformat()
            })
            
            records.append({
                'patient_id': patient_id,
                'lab_type': 'TRIGLYCERIDES',
                'value': gen_value('triglycerides'),
                'unit': 'mg/dL',
                'reference_low': 0,
                'reference_high': 150,
                'recorded_at': record_date.isoformat()
            })
        
        # Generate BP
        records.append({
            'patient_id': patient_id,
            'lab_type': 'BP_SYSTOLIC',
            'value': gen_value('bp_sys'),
            'unit': 'mmHg',
            'reference_low': 90,
            'reference_high': 120,
            'recorded_at': record_date.isoformat()
        })
        
        records.append({
            'patient_id': patient_id,
            'lab_type': 'BP_DIASTOLIC',
            'value': gen_value('bp_dia'),
            'unit': 'mmHg',
            'reference_low': 60,
            'reference_high': 80,
            'recorded_at': record_date.isoformat()
        })
    
    # Add status to each record
    for record in records:
        value = record['value']
        ref_low = record['reference_low']
        ref_high = record['reference_high']
        
        if value < ref_low:
            record['status'] = 'LOW'
        elif value > ref_high:
            record['status'] = 'HIGH'
        else:
            record['status'] = 'NORMAL'
    
    return records


def generate_genomics_data(patient_id: int, risk_level: str = 'low', 
                           seed: int = None) -> List[Dict[str, Any]]:
    """Generate synthetic genomics data with variants.
    
    Args:
        patient_id: Patient identifier
        risk_level: 'low', 'moderate', or 'high'
    """
    if seed is not None:
        random.seed(seed + patient_id)
    
    # Gene variant database
    variants_pool = {
        'low_risk': [
            {'gene': 'MTHFR', 'variant': 'C677T', 'classification': 'BENIGN', 
             'pathogenicity_score': 0.1, 'conditions': ['Vitamin B12 metabolism']},
            {'gene': 'CYP2D6', 'variant': '*4', 'classification': 'VUS', 
             'pathogenicity_score': 0.2, 'conditions': ['Drug metabolism variant']},
        ],
        'moderate_risk': [
            {'gene': 'APOE', 'variant': 'E4/E4', 'classification': 'LIKELY_PATHOGENIC', 
             'pathogenicity_score': 0.5, 'conditions': ['Alzheimer disease risk', 'Cardiovascular risk']},
            {'gene': 'F5', 'variant': 'Leiden', 'classification': 'PATHOGENIC', 
             'pathogenicity_score': 0.6, 'conditions': ['Factor V Leiden thrombophilia']},
        ],
        'high_risk': [
            {'gene': 'BRCA1', 'variant': '185delAG', 'classification': 'PATHOGENIC', 
             'pathogenicity_score': 0.85, 'conditions': ['Breast Cancer', 'Ovarian Cancer']},
            {'gene': 'BRCA2', 'variant': '6174delT', 'classification': 'PATHOGENIC', 
             'pathogenicity_score': 0.80, 'conditions': ['Breast Cancer', 'Pancreatic Cancer']},
            {'gene': 'TP53', 'variant': 'R248W', 'classification': 'PATHOGENIC', 
             'pathogenicity_score': 0.90, 'conditions': ['Li-Fraumeni Syndrome', 'Various Cancers']},
            {'gene': 'MLH1', 'variant': 'c.350C>T', 'classification': 'PATHOGENIC', 
             'pathogenicity_score': 0.75, 'conditions': ['Lynch Syndrome', 'Colorectal Cancer']},
        ]
    }
    
    # Select variants based on risk level
    variants = []
    
    # Always add some low risk variants
    low_variants = random.sample(variants_pool['low_risk'], min(2, len(variants_pool['low_risk'])))
    variants.extend(low_variants)
    
    if risk_level in ['moderate', 'high']:
        mod_variants = random.sample(variants_pool['moderate_risk'], 1)
        variants.extend(mod_variants)
    
    if risk_level == 'high':
        high_variants = random.sample(variants_pool['high_risk'], random.randint(1, 2))
        variants.extend(high_variants)
    
    # Format for database
    result = []
    for v in variants:
        result.append({
            'patient_id': patient_id,
            'gene': v['gene'],
            'variant': v['variant'],
            'chromosome': str(random.randint(1, 22)),
            'position': random.randint(10000, 100000000),
            'reference_allele': random.choice(['A', 'C', 'G', 'T']),
            'alternate_allele': random.choice(['A', 'C', 'G', 'T']),
            'classification': v['classification'],
            'pathogenicity_score': v['pathogenicity_score'],
            'associated_conditions': v['conditions']
        })
    
    return result


def generate_clinical_note(patient_id: int, patient_data: Dict[str, Any],
                          lab_values: Dict[str, float], seed: int = None) -> Dict[str, Any]:
    """Generate a synthetic clinical note."""
    if seed is not None:
        random.seed(seed + patient_id)
    
    # Select random conditions and medications
    num_conditions = random.randint(1, 4)
    num_medications = random.randint(2, 5)
    num_symptoms = random.randint(1, 3)
    
    conditions = random.sample(CONDITIONS, num_conditions)
    medications = random.sample(MEDICATIONS, num_medications)
    symptoms = random.sample(SYMPTOMS, num_symptoms)
    
    # Get lab values or use defaults
    a1c = lab_values.get('A1C', 5.8)
    ldl = lab_values.get('LDL', 110)
    hdl = lab_values.get('HDL', 50)
    bp_sys = lab_values.get('BP_SYSTOLIC', 125)
    bp_dia = lab_values.get('BP_DIASTOLIC', 80)
    
    # Determine trends and status
    if a1c < 5.7:
        a1c_trend = 'stable within normal limits'
        a1c_interpretation = 'within normal range'
    elif a1c < 6.5:
        a1c_trend = 'elevated - pre-diabetic range'
        a1c_interpretation = 'indicates pre-diabetes'
    else:
        a1c_trend = 'elevated - diabetic range'
        a1c_interpretation = 'indicates diabetes'
    
    overall_status = random.choice(['stable', 'improving', 'requires monitoring'])
    recommendations = random.choice([
        'Continue current management. Lifestyle modifications encouraged.',
        'Medication adjustment may be needed. Follow-up in 4 weeks.',
        'Referral to specialist for further evaluation.'
    ])
    
    # Generate note using template
    template = random.choice(CLINICAL_NOTE_TEMPLATES)
    
    note_content = template.format(
        conditions=', '.join(conditions),
        medications=', '.join(medications),
        symptoms=', '.join(symptoms),
        bp=f'{int(bp_sys)}/{int(bp_dia)}',
        hr=random.randint(65, 95),
        weight=random.randint(140, 220),
        a1c=a1c,
        a1c_trend=a1c_trend,
        a1c_interpretation=a1c_interpretation,
        ldl=int(ldl),
        hdl=int(hdl),
        bmi=round(random.uniform(22, 35), 1),
        primary_condition=conditions[0] if conditions else 'chronic conditions',
        status=random.choice(['well-controlled', 'improving', 'stable', 'requiring adjustment']),
        overall_status=overall_status,
        recommendations=recommendations
    )
    
    return {
        'patient_id': patient_id,
        'note_type': random.choice(['PROGRESS', 'FOLLOW_UP', 'CONSULTATION']),
        'content': note_content,
        'conditions': conditions,
        'medications': medications,
        'symptoms': symptoms,
        'note_date': datetime.now().isoformat()
    }


def generate_imaging_study(patient_id: int, finding_type: str = 'normal',
                          seed: int = None) -> Dict[str, Any]:
    """Generate synthetic imaging study metadata."""
    if seed is not None:
        random.seed(seed + patient_id)
    
    modalities = ['XRAY', 'CT', 'MRI']
    body_parts = {
        'XRAY': ['CHEST', 'SPINE', 'KNEE', 'HAND'],
        'CT': ['CHEST', 'ABDOMEN', 'BRAIN', 'SPINE'],
        'MRI': ['BRAIN', 'SPINE', 'KNEE', 'SHOULDER']
    }
    
    findings_by_type = {
        'normal': {
            'findings': ['No acute abnormality detected', 'Normal study', 'Unremarkable examination'],
            'score_range': (0.05, 0.2)
        },
        'mild': {
            'findings': ['Minor degenerative changes', 'Small benign-appearing lesion', 'Mild cardiomegaly'],
            'score_range': (0.2, 0.4)
        },
        'concerning': {
            'findings': ['Suspicious nodule identified', 'Mass requiring follow-up', 'Significant abnormality'],
            'score_range': (0.5, 0.8)
        }
    }
    
    modality = random.choice(modalities)
    body_part = random.choice(body_parts[modality])
    finding_info = findings_by_type.get(finding_type, findings_by_type['normal'])
    
    score_low, score_high = finding_info['score_range']
    
    return {
        'patient_id': patient_id,
        'modality': modality,
        'body_part': body_part,
        'findings': random.choice(finding_info['findings']),
        'abnormality_score': round(random.uniform(score_low, score_high), 3),
        'study_date': (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
    }


def generate_complete_patient_dataset(num_patients: int = 5, 
                                       seed: int = 42) -> Dict[str, Any]:
    """Generate a complete dataset with multiple patients and all data types."""
    random.seed(seed)
    
    dataset = {
        'patients': [],
        'lab_results': [],
        'genomics_data': [],
        'clinical_notes': [],
        'imaging_studies': []
    }
    
    # Define patient profiles for variety
    profiles = [
        ('normal', 'low', 'normal'),
        ('prediabetic', 'moderate', 'mild'),
        ('diabetic', 'moderate', 'mild'),
        ('cardiac_risk', 'low', 'normal'),
        ('diabetic', 'high', 'concerning')
    ]
    
    for i in range(num_patients):
        patient_id = i + 1
        profile_idx = i % len(profiles)
        lab_profile, genomics_risk, imaging_type = profiles[profile_idx]
        
        # Generate patient
        patient = generate_patient(patient_id, seed)
        dataset['patients'].append(patient)
        
        # Generate lab history
        labs = generate_lab_history(patient_id, num_records=10, 
                                   patient_profile=lab_profile, seed=seed)
        dataset['lab_results'].extend(labs)
        
        # Get latest lab values for clinical note
        latest_labs = {}
        for lab in labs:
            if lab['lab_type'] not in latest_labs:
                latest_labs[lab['lab_type']] = lab['value']
        
        # Generate genomics
        genomics = generate_genomics_data(patient_id, risk_level=genomics_risk, seed=seed)
        dataset['genomics_data'].extend(genomics)
        
        # Generate clinical notes
        for j in range(3):  # 3 notes per patient
            note = generate_clinical_note(patient_id, patient, latest_labs, seed=seed+j)
            dataset['clinical_notes'].append(note)
        
        # Generate imaging study
        imaging = generate_imaging_study(patient_id, finding_type=imaging_type, seed=seed)
        dataset['imaging_studies'].append(imaging)
    
    return dataset


def save_dataset_to_files(dataset: Dict[str, Any], output_dir: str):
    """Save generated dataset to JSON files."""
    os.makedirs(output_dir, exist_ok=True)
    
    for data_type, data in dataset.items():
        file_path = os.path.join(output_dir, f'{data_type}.json')
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f'Saved {len(data)} records to {file_path}')


if __name__ == '__main__':
    # Generate sample dataset
    print("Generating synthetic health data...")
    dataset = generate_complete_patient_dataset(num_patients=5, seed=42)
    
    # Save to files
    output_dir = os.path.join(os.path.dirname(__file__), 'data')
    save_dataset_to_files(dataset, output_dir)
    
    print("\nDataset generation complete!")
    print(f"- {len(dataset['patients'])} patients")
    print(f"- {len(dataset['lab_results'])} lab results")
    print(f"- {len(dataset['genomics_data'])} genomic variants")
    print(f"- {len(dataset['clinical_notes'])} clinical notes")
    print(f"- {len(dataset['imaging_studies'])} imaging studies")
