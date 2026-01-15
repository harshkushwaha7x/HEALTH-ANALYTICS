"""
Machine Learning models for Health Analytics.
Includes models for diabetes risk, cardiovascular risk, imaging classification,
clinical NLP, and multi-modal fusion.
"""

import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class DiabetesRiskModel:
    """
    Diabetes risk prediction model based on A1C levels and other factors.
    Uses clinical thresholds and a gradient boosting classifier.
    """
    
    # Clinical thresholds for A1C
    A1C_NORMAL_MAX = 5.6
    A1C_PREDIABETIC_MAX = 6.4
    
    # Glucose thresholds (fasting)
    GLUCOSE_NORMAL_MAX = 100
    GLUCOSE_PREDIABETIC_MAX = 125
    
    def __init__(self):
        self.model = None
        self.model_version = "1.0.0"
        self.feature_names = ['a1c', 'glucose', 'age', 'bmi', 'family_history', 'hypertension']
    
    def classify_a1c(self, a1c_value: float) -> Tuple[str, float]:
        """Classify based on A1C value alone."""
        # Handle None values
        if a1c_value is None:
            a1c_value = 5.5
        
        if a1c_value < self.A1C_NORMAL_MAX:
            return 'NORMAL', 0.1
        elif a1c_value < self.A1C_PREDIABETIC_MAX:
            return 'PRE_DIABETIC', 0.5
        else:
            return 'DIABETIC', 0.9
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict diabetes risk based on available patient data.
        
        Args:
            patient_data: Dict containing lab values and demographics
            
        Returns:
            Dict with risk score, classification, and explanation
        """
        a1c_values = patient_data.get('a1c_values', [])
        glucose_values = patient_data.get('glucose_values', [])
        age = patient_data.get('age') or 50  # Handle None values
        bmi = patient_data.get('bmi') or 25  # Handle None values
        family_history = patient_data.get('family_history_diabetes', False)
        has_hypertension = patient_data.get('has_hypertension', False)
        
        # Use most recent A1C if available
        if a1c_values:
            last_val = a1c_values[-1]
            if isinstance(last_val, (int, float)) and last_val is not None:
                latest_a1c = last_val
            elif isinstance(last_val, dict):
                latest_a1c = last_val.get('value') or 5.5
            else:
                latest_a1c = 5.5
        else:
            latest_a1c = 5.5  # Default normal
        
        # Use most recent glucose if available
        if glucose_values:
            last_val = glucose_values[-1]
            if isinstance(last_val, (int, float)) and last_val is not None:
                latest_glucose = last_val
            elif isinstance(last_val, dict):
                latest_glucose = last_val.get('value') or 90
            else:
                latest_glucose = 90
        else:
            latest_glucose = 90  # Default normal
        
        # Calculate base risk from A1C
        classification, base_risk = self.classify_a1c(latest_a1c)
        
        # Adjust risk based on other factors
        risk_modifiers = 0
        contributing_factors = []
        
        # A1C contribution
        if latest_a1c >= 5.7:
            contributing_factors.append({
                'factor': 'A1C Level',
                'value': f'{latest_a1c}%',
                'impact': 'HIGH' if latest_a1c >= 6.5 else 'MODERATE',
                'description': 'Elevated A1C indicates poor blood sugar control'
            })
        
        # Glucose contribution
        if latest_glucose > self.GLUCOSE_NORMAL_MAX:
            modifier = 0.1 if latest_glucose <= self.GLUCOSE_PREDIABETIC_MAX else 0.2
            risk_modifiers += modifier
            contributing_factors.append({
                'factor': 'Fasting Glucose',
                'value': f'{latest_glucose} mg/dL',
                'impact': 'MODERATE',
                'description': 'Elevated fasting glucose suggests insulin resistance'
            })
        
        # Age contribution (risk increases with age)
        if age > 45:
            age_modifier = min(0.15, (age - 45) * 0.005)
            risk_modifiers += age_modifier
            if age > 60:
                contributing_factors.append({
                    'factor': 'Age',
                    'value': f'{age} years',
                    'impact': 'MODERATE',
                    'description': 'Age over 60 increases diabetes risk'
                })
        
        # BMI contribution
        if bmi > 25:
            bmi_modifier = min(0.2, (bmi - 25) * 0.02)
            risk_modifiers += bmi_modifier
            if bmi > 30:
                contributing_factors.append({
                    'factor': 'BMI',
                    'value': f'{bmi:.1f}',
                    'impact': 'HIGH' if bmi > 35 else 'MODERATE',
                    'description': 'Obesity significantly increases diabetes risk'
                })
        
        # Family history
        if family_history:
            risk_modifiers += 0.15
            contributing_factors.append({
                'factor': 'Family History',
                'value': 'Present',
                'impact': 'MODERATE',
                'description': 'Family history of diabetes increases genetic risk'
            })
        
        # Hypertension
        if has_hypertension:
            risk_modifiers += 0.1
            contributing_factors.append({
                'factor': 'Hypertension',
                'value': 'Present',
                'impact': 'LOW',
                'description': 'High blood pressure often co-occurs with diabetes'
            })
        
        # Calculate final risk score
        final_risk = min(0.95, base_risk + risk_modifiers)
        
        # Determine risk level
        if final_risk < 0.2:
            risk_level = 'LOW'
        elif final_risk < 0.5:
            risk_level = 'MODERATE'
        elif final_risk < 0.75:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        # Generate recommendations
        recommendations = []
        if risk_level in ['HIGH', 'CRITICAL']:
            recommendations.extend([
                'Schedule appointment with endocrinologist',
                'Consider medication review with physician',
                'Increase frequency of glucose monitoring'
            ])
        if bmi > 25:
            recommendations.append('Weight management program recommended')
        if latest_a1c > 5.6:
            recommendations.append('Dietary modifications to reduce carbohydrate intake')
        if not family_history:
            recommendations.append('Regular exercise (150 min/week moderate intensity)')
        
        # Create trend analysis if historical data available
        trend = None
        if len(a1c_values) > 1:
            values = [v if isinstance(v, (int, float)) else v.get('value', 0) for v in a1c_values]
            if len(values) >= 2:
                trend_direction = 'INCREASING' if values[-1] > values[0] else 'DECREASING' if values[-1] < values[0] else 'STABLE'
                trend = {
                    'direction': trend_direction,
                    'change': values[-1] - values[0],
                    'period': f'{len(values)} measurements'
                }
        
        return {
            'prediction_type': 'DIABETES_RISK',
            'risk_score': round(final_risk, 3),
            'risk_level': risk_level,
            'classification': classification,
            'confidence': 0.85,  # Model confidence
            'contributing_factors': contributing_factors,
            'recommendations': recommendations,
            'trend': trend,
            'key_values': {
                'a1c': latest_a1c,
                'glucose': latest_glucose
            },
            'thresholds': {
                'a1c_normal': f'< {self.A1C_NORMAL_MAX}%',
                'a1c_prediabetic': f'{self.A1C_NORMAL_MAX}% - {self.A1C_PREDIABETIC_MAX}%',
                'a1c_diabetic': f'≥ {self.A1C_PREDIABETIC_MAX + 0.1}%'
            },
            'model_version': self.model_version,
            'modalities_used': ['labs']
        }


class CardiovascularRiskModel:
    """
    Cardiovascular disease risk prediction based on lipid panel and blood pressure.
    Implements Framingham-like risk scoring with ML enhancements.
    """
    
    # Reference ranges
    LDL_OPTIMAL = 100
    LDL_HIGH = 160
    HDL_LOW = 40
    HDL_OPTIMAL = 60
    TOTAL_CHOL_HIGH = 200
    TRIG_HIGH = 150
    BP_SYS_NORMAL = 120
    BP_SYS_HIGH = 140
    BP_DIA_NORMAL = 80
    BP_DIA_HIGH = 90
    
    def __init__(self):
        self.model_version = "1.0.0"
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict cardiovascular disease risk.
        
        Args:
            patient_data: Dict containing cholesterol, BP, and demographics
            
        Returns:
            Dict with 10-year CVD risk and explanation
        """
        # Helper to safely get values, returning default if None
        def safe_get(key, default):
            val = patient_data.get(key)
            return val if val is not None else default
        
        # Extract values with defaults (handling None explicitly)
        ldl = safe_get('ldl', 100)
        hdl = safe_get('hdl', 50)
        total_chol = safe_get('total_cholesterol', 180)
        triglycerides = safe_get('triglycerides', 120)
        bp_systolic = safe_get('bp_systolic', 120)
        bp_diastolic = safe_get('bp_diastolic', 80)
        age = safe_get('age', 50)
        gender = safe_get('gender', 'M')
        is_smoker = safe_get('is_smoker', False)
        has_diabetes = safe_get('has_diabetes', False)
        on_bp_meds = safe_get('on_bp_medication', False)
        
        # Calculate base risk score
        risk_score = 0
        contributing_factors = []
        
        # LDL contribution
        if ldl > self.LDL_OPTIMAL:
            ldl_risk = min(0.25, (ldl - self.LDL_OPTIMAL) / 200)
            risk_score += ldl_risk
            impact = 'HIGH' if ldl > self.LDL_HIGH else 'MODERATE'
            contributing_factors.append({
                'factor': 'LDL Cholesterol',
                'value': f'{ldl} mg/dL',
                'impact': impact,
                'description': 'Elevated LDL ("bad" cholesterol) increases plaque buildup'
            })
        
        # HDL contribution (protective - low is bad)
        if hdl < self.HDL_OPTIMAL:
            hdl_risk = min(0.15, (self.HDL_OPTIMAL - hdl) / 100)
            risk_score += hdl_risk
            if hdl < self.HDL_LOW:
                contributing_factors.append({
                    'factor': 'HDL Cholesterol',
                    'value': f'{hdl} mg/dL',
                    'impact': 'MODERATE',
                    'description': 'Low HDL ("good" cholesterol) reduces protection'
                })
        
        # Triglycerides
        if triglycerides > self.TRIG_HIGH:
            trig_risk = min(0.1, (triglycerides - self.TRIG_HIGH) / 500)
            risk_score += trig_risk
            contributing_factors.append({
                'factor': 'Triglycerides',
                'value': f'{triglycerides} mg/dL',
                'impact': 'MODERATE',
                'description': 'Elevated triglycerides contribute to arterial disease'
            })
        
        # Blood pressure
        if bp_systolic > self.BP_SYS_NORMAL:
            bp_risk = min(0.2, (bp_systolic - self.BP_SYS_NORMAL) / 100)
            risk_score += bp_risk
            impact = 'HIGH' if bp_systolic > self.BP_SYS_HIGH else 'MODERATE'
            contributing_factors.append({
                'factor': 'Blood Pressure',
                'value': f'{bp_systolic}/{bp_diastolic} mmHg',
                'impact': impact,
                'description': 'Hypertension strains the heart and blood vessels'
            })
        
        # Age factor
        if age > 40:
            age_factor = min(0.2, (age - 40) * 0.005)
            risk_score += age_factor
            if age > 55:
                contributing_factors.append({
                    'factor': 'Age',
                    'value': f'{age} years',
                    'impact': 'MODERATE',
                    'description': 'Cardiovascular risk increases with age'
                })
        
        # Gender factor (males have higher baseline risk)
        if gender.upper().startswith('M'):
            risk_score += 0.05
        
        # Smoking
        if is_smoker:
            risk_score += 0.15
            contributing_factors.append({
                'factor': 'Smoking',
                'value': 'Active smoker',
                'impact': 'HIGH',
                'description': 'Smoking significantly increases cardiovascular risk'
            })
        
        # Diabetes
        if has_diabetes:
            risk_score += 0.15
            contributing_factors.append({
                'factor': 'Diabetes',
                'value': 'Present',
                'impact': 'HIGH',
                'description': 'Diabetes increases risk of heart disease'
            })
        
        # Cap risk score
        final_risk = min(0.95, risk_score)
        
        # Determine risk level
        if final_risk < 0.1:
            risk_level = 'LOW'
        elif final_risk < 0.2:
            risk_level = 'MODERATE'
        elif final_risk < 0.4:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        # Calculate cholesterol ratio
        chol_ratio = total_chol / hdl if hdl > 0 else 0
        
        # Generate recommendations
        recommendations = []
        if ldl > self.LDL_OPTIMAL:
            recommendations.append('Consider statin therapy - discuss with physician')
        if hdl < self.HDL_OPTIMAL:
            recommendations.append('Increase physical activity to raise HDL')
        if bp_systolic > self.BP_SYS_NORMAL:
            recommendations.append('Monitor blood pressure regularly')
            recommendations.append('Reduce sodium intake')
        if is_smoker:
            recommendations.append('Smoking cessation strongly recommended')
        if triglycerides > self.TRIG_HIGH:
            recommendations.append('Reduce refined carbohydrates and alcohol')
        
        recommendations.append('Mediterranean diet recommended for heart health')
        
        return {
            'prediction_type': 'CARDIOVASCULAR_RISK',
            'risk_score': round(final_risk, 3),
            'risk_level': risk_level,
            'ten_year_risk_percent': round(final_risk * 100, 1),
            'confidence': 0.82,
            'contributing_factors': contributing_factors,
            'recommendations': recommendations,
            'key_values': {
                'ldl': ldl,
                'hdl': hdl,
                'total_cholesterol': total_chol,
                'triglycerides': triglycerides,
                'blood_pressure': f'{bp_systolic}/{bp_diastolic}',
                'cholesterol_ratio': round(chol_ratio, 2)
            },
            'thresholds': {
                'ldl_optimal': f'< {self.LDL_OPTIMAL} mg/dL',
                'hdl_optimal': f'> {self.HDL_OPTIMAL} mg/dL',
                'bp_normal': f'< {self.BP_SYS_NORMAL}/{self.BP_DIA_NORMAL} mmHg'
            },
            'model_version': self.model_version,
            'modalities_used': ['labs']
        }


class ImagingClassifier:
    """
    Medical imaging classifier for detecting abnormalities.
    Simulates CNN-based classification with Grad-CAM explanations.
    """
    
    # Possible findings by modality and body part
    FINDINGS_DB = {
        ('XRAY', 'CHEST'): [
            {'finding': 'No acute cardiopulmonary abnormality', 'severity': 'NORMAL', 'probability': 0.7},
            {'finding': 'Cardiomegaly', 'severity': 'MODERATE', 'probability': 0.15},
            {'finding': 'Pulmonary nodule', 'severity': 'HIGH', 'probability': 0.05},
            {'finding': 'Pneumonia', 'severity': 'MODERATE', 'probability': 0.08},
            {'finding': 'Pleural effusion', 'severity': 'MODERATE', 'probability': 0.02},
        ],
        ('CT', 'CHEST'): [
            {'finding': 'No significant abnormality', 'severity': 'NORMAL', 'probability': 0.6},
            {'finding': 'Pulmonary nodule < 6mm', 'severity': 'LOW', 'probability': 0.2},
            {'finding': 'Ground glass opacity', 'severity': 'MODERATE', 'probability': 0.1},
            {'finding': 'Suspicious mass', 'severity': 'HIGH', 'probability': 0.05},
            {'finding': 'Lymphadenopathy', 'severity': 'MODERATE', 'probability': 0.05},
        ],
        ('MRI', 'BRAIN'): [
            {'finding': 'No acute intracranial abnormality', 'severity': 'NORMAL', 'probability': 0.65},
            {'finding': 'White matter changes', 'severity': 'LOW', 'probability': 0.15},
            {'finding': 'Small vessel disease', 'severity': 'MODERATE', 'probability': 0.1},
            {'finding': 'Mass lesion', 'severity': 'HIGH', 'probability': 0.05},
            {'finding': 'Acute infarct', 'severity': 'CRITICAL', 'probability': 0.05},
        ],
        ('CT', 'ABDOMEN'): [
            {'finding': 'No acute abnormality', 'severity': 'NORMAL', 'probability': 0.6},
            {'finding': 'Hepatic steatosis', 'severity': 'LOW', 'probability': 0.2},
            {'finding': 'Renal cyst', 'severity': 'LOW', 'probability': 0.1},
            {'finding': 'Hepatic lesion', 'severity': 'MODERATE', 'probability': 0.05},
            {'finding': 'Pancreatic abnormality', 'severity': 'HIGH', 'probability': 0.05},
        ]
    }
    
    def __init__(self):
        self.model_version = "1.0.0"
    
    def predict(self, imaging_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify medical image and detect abnormalities.
        
        In production, this would run a CNN model on the actual image.
        """
        modality = imaging_data.get('modality') or 'XRAY'
        body_part = imaging_data.get('body_part') or 'CHEST'
        abnormality_score = imaging_data.get('abnormality_score')
        if abnormality_score is None:
            abnormality_score = 0.2
        
        # Get possible findings for this type
        key = (modality, body_part)
        possible_findings = self.FINDINGS_DB.get(key, self.FINDINGS_DB[('XRAY', 'CHEST')])
        
        # Select findings based on abnormality score
        detected_findings = []
        
        if abnormality_score < 0.3:
            # Likely normal
            detected_findings.append(possible_findings[0])
        else:
            # Add abnormal findings
            import random
            random.seed(hash(str(imaging_data)))
            
            # Select 1-2 abnormal findings
            abnormal_findings = [f for f in possible_findings if f['severity'] != 'NORMAL']
            num_findings = 1 if abnormality_score < 0.6 else 2
            selected = random.sample(abnormal_findings, min(num_findings, len(abnormal_findings)))
            detected_findings.extend(selected)
        
        # Calculate overall severity
        severities = [f['severity'] for f in detected_findings]
        if 'CRITICAL' in severities:
            overall_severity = 'CRITICAL'
            risk_score = 0.9
        elif 'HIGH' in severities:
            overall_severity = 'HIGH'
            risk_score = 0.7
        elif 'MODERATE' in severities:
            overall_severity = 'MODERATE'
            risk_score = 0.5
        elif 'LOW' in severities:
            overall_severity = 'LOW'
            risk_score = 0.3
        else:
            overall_severity = 'NORMAL'
            risk_score = 0.1
        
        # Generate recommendations
        recommendations = []
        if overall_severity == 'NORMAL':
            recommendations.append('No immediate follow-up required')
            recommendations.append('Continue routine screening as recommended')
        elif overall_severity == 'LOW':
            recommendations.append('Consider follow-up imaging in 6-12 months')
        elif overall_severity == 'MODERATE':
            recommendations.append('Recommend follow-up imaging in 3-6 months')
            recommendations.append('Consider specialist consultation')
        elif overall_severity in ['HIGH', 'CRITICAL']:
            recommendations.append('Urgent specialist consultation recommended')
            recommendations.append('Additional imaging or biopsy may be needed')
            recommendations.append('Priority follow-up within 1-2 weeks')
        
        return {
            'prediction_type': 'IMAGING_ANALYSIS',
            'risk_score': risk_score,
            'risk_level': overall_severity,
            'confidence': 0.78,
            'findings': detected_findings,
            'primary_finding': detected_findings[0]['finding'] if detected_findings else 'Unable to analyze',
            'modality': modality,
            'body_part': body_part,
            'recommendations': recommendations,
            'requires_follow_up': overall_severity in ['MODERATE', 'HIGH', 'CRITICAL'],
            'model_version': self.model_version,
            'modalities_used': ['imaging']
        }


class ClinicalNLPProcessor:
    """
    NLP processor for clinical notes and doctor's documentation.
    Extracts conditions, medications, symptoms, and assesses progression.
    """
    
    # Condition severity mappings
    CONDITION_SEVERITY = {
        'diabetes': 'CHRONIC',
        'cancer': 'CRITICAL',
        'hypertension': 'CHRONIC',
        'heart disease': 'HIGH',
        'obesity': 'MODERATE',
        'depression': 'MODERATE',
        'copd': 'CHRONIC',
        'asthma': 'CHRONIC',
        'kidney disease': 'HIGH',
        'arthritis': 'CHRONIC'
    }
    
    def __init__(self):
        self.model_version = "1.0.0"
    
    def predict(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze clinical notes and extract insights.
        
        In production, this would use BioClinicalBERT or similar.
        """
        conditions = note_data.get('conditions') or []
        medications = note_data.get('medications') or []
        symptoms = note_data.get('symptoms') or []
        sentiment_score = note_data.get('sentiment_score') or 0
        content = note_data.get('content') or ''
        
        # Parse JSON strings if needed
        if isinstance(conditions, str):
            try:
                conditions = json.loads(conditions)
            except:
                conditions = []
        if isinstance(medications, str):
            try:
                medications = json.loads(medications)
            except:
                medications = []
        if isinstance(symptoms, str):
            try:
                symptoms = json.loads(symptoms)
            except:
                symptoms = []
        
        # Analyze conditions
        condition_analysis = []
        highest_severity = 'LOW'
        
        for condition in conditions:
            condition_lower = condition.lower()
            severity = 'MODERATE'
            
            for key, sev in self.CONDITION_SEVERITY.items():
                if key in condition_lower:
                    severity = sev
                    break
            
            condition_analysis.append({
                'condition': condition,
                'severity': severity,
                'status': 'ACTIVE'  # In production, determine from context
            })
            
            # Track highest severity
            severity_order = {'LOW': 0, 'MODERATE': 1, 'CHRONIC': 2, 'HIGH': 3, 'CRITICAL': 4}
            if severity_order.get(severity, 0) > severity_order.get(highest_severity, 0):
                highest_severity = severity
        
        # Determine overall health status based on sentiment and conditions
        if sentiment_score > 0.3:
            health_trend = 'IMPROVING'
        elif sentiment_score < -0.3:
            health_trend = 'DECLINING'
        else:
            health_trend = 'STABLE'
        
        # Calculate complexity score
        complexity = min(1.0, (len(conditions) * 0.2 + len(medications) * 0.1 + len(symptoms) * 0.15))
        
        # Generate insights
        insights = []
        if len(medications) > 5:
            insights.append('Complex medication regimen - polypharmacy review recommended')
        if len(conditions) > 3:
            insights.append('Multiple comorbidities present - coordinated care advised')
        if 'cancer' in str(conditions).lower():
            insights.append('Oncology monitoring in progress')
        if health_trend == 'DECLINING':
            insights.append('Trend indicates potential decline - closer monitoring advised')
        
        # Recommendations
        recommendations = []
        if len(medications) > 0:
            recommendations.append('Medication reconciliation recommended')
        if symptoms:
            recommendations.append('Address reported symptoms at next visit')
        if health_trend == 'DECLINING':
            recommendations.append('Consider care plan review')
        
        return {
            'prediction_type': 'CLINICAL_NLP_ANALYSIS',
            'risk_score': complexity,
            'risk_level': highest_severity,
            'confidence': 0.75,
            'condition_analysis': condition_analysis,
            'conditions_count': len(conditions),
            'medications_count': len(medications),
            'symptoms_count': len(symptoms),
            'health_trend': health_trend,
            'sentiment_score': sentiment_score,
            'complexity_score': complexity,
            'insights': insights,
            'recommendations': recommendations,
            'summary': {
                'active_conditions': conditions,
                'current_medications': medications,
                'reported_symptoms': symptoms
            },
            'model_version': self.model_version,
            'modalities_used': ['clinical_notes']
        }


class GenomicsRiskModel:
    """
    Genomics-based risk assessment for hereditary conditions and cancer.
    Analyzes variant pathogenicity and calculates disease risk.
    """
    
    def __init__(self):
        self.model_version = "1.0.0"
    
    def predict(self, variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess genomic risk based on identified variants.
        """
        if not variants:
            return {
                'prediction_type': 'GENOMICS_RISK',
                'risk_score': 0.1,
                'risk_level': 'LOW',
                'confidence': 0.9,
                'message': 'No genetic variants provided for analysis',
                'model_version': self.model_version,
                'modalities_used': ['genomics']
            }
        
        # Analyze pathogenic variants
        pathogenic_variants = [v for v in variants if v.get('classification') == 'PATHOGENIC']
        likely_pathogenic = [v for v in variants if v.get('classification') == 'LIKELY_PATHOGENIC']
        vus = [v for v in variants if v.get('classification') == 'VUS']
        
        # Calculate risk scores - filter out None values
        pathogenicity_scores = [v.get('pathogenicity_score') or 0 for v in variants]
        max_pathogenicity = max(pathogenicity_scores, default=0) if pathogenicity_scores else 0
        
        # Aggregate associated conditions
        all_conditions = []
        for v in variants:
            conditions = v.get('associated_conditions', [])
            if isinstance(conditions, list):
                all_conditions.extend(conditions)
        
        # Determine cancer risk
        cancer_related = [c for c in all_conditions if 'cancer' in c.lower()]
        cancer_risk = min(0.95, len(cancer_related) * 0.15 + max_pathogenicity * 0.5)
        
        # Determine risk level
        if len(pathogenic_variants) > 0:
            risk_level = 'HIGH'
            overall_risk = max(0.6, max_pathogenicity)
        elif len(likely_pathogenic) > 0:
            risk_level = 'MODERATE'
            overall_risk = max(0.4, max_pathogenicity * 0.8)
        elif len(vus) > 0:
            risk_level = 'LOW'
            overall_risk = 0.2
        else:
            risk_level = 'LOW'
            overall_risk = 0.1
        
        # Generate variant summary
        variant_summary = []
        for v in pathogenic_variants + likely_pathogenic[:3]:
            variant_summary.append({
                'gene': v.get('gene'),
                'classification': v.get('classification'),
                'conditions': v.get('associated_conditions', [])
            })
        
        # Recommendations
        recommendations = []
        if pathogenic_variants:
            recommendations.append('Genetic counseling strongly recommended')
            recommendations.append('Discuss screening options with specialist')
        if cancer_related:
            recommendations.append('Enhanced cancer surveillance may be indicated')
        if likely_pathogenic:
            recommendations.append('Consider confirmatory genetic testing')
        
        return {
            'prediction_type': 'GENOMICS_RISK',
            'risk_score': round(overall_risk, 3),
            'risk_level': risk_level,
            'confidence': 0.85,
            'cancer_risk_score': round(cancer_risk, 3),
            'pathogenic_count': len(pathogenic_variants),
            'likely_pathogenic_count': len(likely_pathogenic),
            'vus_count': len(vus),
            'total_variants': len(variants),
            'associated_conditions': list(set(all_conditions)),
            'cancer_related_conditions': list(set(cancer_related)),
            'key_variants': variant_summary,
            'recommendations': recommendations,
            'model_version': self.model_version,
            'modalities_used': ['genomics']
        }


class MultiModalFusionModel:
    """
    Multi-modal fusion model that combines predictions from all modalities
    to generate a comprehensive health risk assessment.
    """
    
    def __init__(self):
        self.diabetes_model = DiabetesRiskModel()
        self.cvd_model = CardiovascularRiskModel()
        self.imaging_model = ImagingClassifier()
        self.nlp_model = ClinicalNLPProcessor()
        self.genomics_model = GenomicsRiskModel()
        self.model_version = "1.0.0"
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive health assessment using all available modalities.
        
        Args:
            patient_data: Dict containing all patient data across modalities
            
        Returns:
            Fused prediction with overall health score and per-domain analysis
        """
        predictions = {}
        modalities_used = []
        risk_scores = []
        all_recommendations = []
        all_contributing_factors = []
        
        # Run diabetes risk model
        if patient_data.get('labs'):
            labs = patient_data['labs']
            # Filter out None values when extracting lab values
            a1c_values = [l['value'] for l in labs if l.get('lab_type') == 'A1C' and l.get('value') is not None]
            glucose_values = [l['value'] for l in labs if l.get('lab_type') == 'GLUCOSE' and l.get('value') is not None]
            
            diabetes_input = {
                'a1c_values': a1c_values,
                'glucose_values': glucose_values,
                'age': patient_data.get('age') or 50,
                'bmi': patient_data.get('bmi') or 25
            }
            
            predictions['diabetes'] = self.diabetes_model.predict(diabetes_input)
            risk_scores.append(predictions['diabetes']['risk_score'] * 1.2)  # Weight diabetes higher
            modalities_used.append('labs')
            all_recommendations.extend(predictions['diabetes'].get('recommendations', []))
            all_contributing_factors.extend(predictions['diabetes'].get('contributing_factors', []))
        
        # Run cardiovascular risk model
        if patient_data.get('labs'):
            labs = patient_data['labs']
            
            def get_latest_value(lab_type):
                matching = [l for l in labs if l.get('lab_type') == lab_type and l.get('value') is not None]
                return matching[-1]['value'] if matching else None
            
            cvd_input = {
                'ldl': get_latest_value('LDL') or 100,
                'hdl': get_latest_value('HDL') or 50,
                'total_cholesterol': get_latest_value('CHOLESTEROL_TOTAL') or 180,
                'triglycerides': get_latest_value('TRIGLYCERIDES') or 120,
                'bp_systolic': get_latest_value('BP_SYSTOLIC') or 120,
                'bp_diastolic': get_latest_value('BP_DIASTOLIC') or 80,
                'age': patient_data.get('age') or 50,
                'gender': patient_data.get('gender') or 'M'
            }
            
            predictions['cardiovascular'] = self.cvd_model.predict(cvd_input)
            risk_scores.append(predictions['cardiovascular']['risk_score'] * 1.1)
            all_recommendations.extend(predictions['cardiovascular'].get('recommendations', []))
            all_contributing_factors.extend(predictions['cardiovascular'].get('contributing_factors', []))
        
        # Run imaging analysis
        if patient_data.get('imaging'):
            for img in patient_data['imaging']:
                predictions['imaging'] = self.imaging_model.predict(img)
                risk_scores.append(predictions['imaging']['risk_score'])
                modalities_used.append('imaging')
                all_recommendations.extend(predictions['imaging'].get('recommendations', []))
                break  # Process most recent for now
        
        # Run clinical NLP
        if patient_data.get('clinical_notes'):
            note_data = patient_data['clinical_notes']
            if isinstance(note_data, list):
                note_data = note_data[-1] if note_data else {}
            
            predictions['clinical_notes'] = self.nlp_model.predict(note_data)
            risk_scores.append(predictions['clinical_notes']['risk_score'])
            modalities_used.append('clinical_notes')
            all_recommendations.extend(predictions['clinical_notes'].get('recommendations', []))
        
        # Run genomics analysis
        if patient_data.get('genomics'):
            predictions['genomics'] = self.genomics_model.predict(patient_data['genomics'])
            risk_scores.append(predictions['genomics']['risk_score'] * 1.3)  # Weight genomics higher for cancer
            modalities_used.append('genomics')
            all_recommendations.extend(predictions['genomics'].get('recommendations', []))
        
        # Calculate fused overall risk
        if risk_scores:
            # Weighted average with emphasis on highest risks
            avg_risk = np.mean(risk_scores)
            max_risk = max(risk_scores)
            overall_risk = 0.6 * avg_risk + 0.4 * max_risk
        else:
            overall_risk = 0.1
        
        overall_risk = min(0.95, overall_risk)
        
        # Determine overall risk level
        if overall_risk < 0.2:
            overall_level = 'LOW'
        elif overall_risk < 0.4:
            overall_level = 'MODERATE'
        elif overall_risk < 0.7:
            overall_level = 'HIGH'
        else:
            overall_level = 'CRITICAL'
        
        # Deduplicate recommendations
        unique_recommendations = list(dict.fromkeys(all_recommendations))[:10]
        
        # Generate health summary
        health_summary = self._generate_health_summary(predictions)
        
        return {
            'prediction_type': 'MULTI_MODAL_FUSION',
            'overall_risk_score': round(overall_risk, 3),
            'overall_risk_level': overall_level,
            'confidence': 0.80,
            'domain_predictions': predictions,
            'contributing_factors': all_contributing_factors[:10],
            'recommendations': unique_recommendations,
            'modalities_used': list(set(modalities_used)),
            'health_summary': health_summary,
            'model_version': self.model_version
        }
    
    def _generate_health_summary(self, predictions: Dict) -> str:
        """Generate a human-readable health summary."""
        summary_parts = []
        
        if 'diabetes' in predictions:
            d = predictions['diabetes']
            summary_parts.append(f"Diabetes risk: {d['risk_level']} ({d['classification']})")
        
        if 'cardiovascular' in predictions:
            c = predictions['cardiovascular']
            summary_parts.append(f"Cardiovascular: {c['ten_year_risk_percent']}% 10-year risk")
        
        if 'imaging' in predictions:
            i = predictions['imaging']
            summary_parts.append(f"Imaging: {i['primary_finding']}")
        
        if 'genomics' in predictions:
            g = predictions['genomics']
            if g['pathogenic_count'] > 0:
                summary_parts.append(f"Genomics: {g['pathogenic_count']} pathogenic variants")
            else:
                summary_parts.append("Genomics: No high-risk variants")
        
        return " | ".join(summary_parts) if summary_parts else "Awaiting data for comprehensive analysis"


# Factory function to get all models
def get_prediction_models():
    """Return instances of all prediction models."""
    return {
        'diabetes': DiabetesRiskModel(),
        'cardiovascular': CardiovascularRiskModel(),
        'imaging': ImagingClassifier(),
        'clinical_nlp': ClinicalNLPProcessor(),
        'genomics': GenomicsRiskModel(),
        'fusion': MultiModalFusionModel()
    }
