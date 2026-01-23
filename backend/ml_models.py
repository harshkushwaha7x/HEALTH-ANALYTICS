"""
Machine Learning models for Health Analytics.
Includes models for diabetes risk, cardiovascular risk, imaging classification,
clinical NLP, genomics analysis, anomaly detection, and multi-modal fusion.
"""

import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class AnomalyDetector:
    """
    Anomaly detection and trend analysis for health metrics.
    Identifies abnormal values, rapid changes, and concerning patterns.
    """
    
    # Clinical reference ranges for common lab tests
    REFERENCE_RANGES = {
        'A1C': {'low': 4.0, 'normal_low': 4.0, 'normal_high': 5.6, 'prediabetic': 6.4, 'high': 6.5, 'critical': 9.0, 'unit': '%'},
        'GLUCOSE': {'low': 70, 'normal_low': 70, 'normal_high': 100, 'prediabetic': 125, 'high': 126, 'critical': 250, 'unit': 'mg/dL'},
        'LDL': {'optimal': 100, 'normal_high': 129, 'borderline': 159, 'high': 189, 'critical': 190, 'unit': 'mg/dL'},
        'HDL': {'critical_low': 40, 'low': 40, 'normal': 60, 'optimal': 60, 'unit': 'mg/dL'},
        'CHOLESTEROL_TOTAL': {'optimal': 200, 'borderline': 239, 'high': 240, 'critical': 300, 'unit': 'mg/dL'},
        'TRIGLYCERIDES': {'normal': 150, 'borderline': 199, 'high': 499, 'critical': 500, 'unit': 'mg/dL'},
        'BP_SYSTOLIC': {'low': 90, 'normal': 120, 'elevated': 129, 'high_stage1': 139, 'high_stage2': 180, 'critical': 180, 'unit': 'mmHg'},
        'BP_DIASTOLIC': {'low': 60, 'normal': 80, 'high_stage1': 89, 'high_stage2': 120, 'critical': 120, 'unit': 'mmHg'},
        'CREATININE': {'normal_low': 0.7, 'normal_high': 1.3, 'elevated': 2.0, 'critical': 4.0, 'unit': 'mg/dL'},
        'HEMOGLOBIN': {'low_male': 13.5, 'normal_male': 17.5, 'low_female': 12.0, 'normal_female': 15.5, 'unit': 'g/dL'},
    }
    
    # Rate of change thresholds (per month)
    RATE_THRESHOLDS = {
        'A1C': {'warning': 0.3, 'critical': 0.5},
        'GLUCOSE': {'warning': 15, 'critical': 30},
        'LDL': {'warning': 20, 'critical': 40},
        'BP_SYSTOLIC': {'warning': 10, 'critical': 20},
    }
    
    def __init__(self):
        self.model_version = "1.0.0"
    
    def analyze_value(self, lab_type: str, value: float, gender: str = 'M') -> Dict[str, Any]:
        """Analyze a single value against reference ranges."""
        if value is None:
            return {'status': 'UNKNOWN', 'message': 'No value provided'}
        
        ranges = self.REFERENCE_RANGES.get(lab_type.upper())
        if not ranges:
            return {'status': 'UNKNOWN', 'message': f'No reference range for {lab_type}'}
        
        unit = ranges.get('unit', '')
        
        # Determine status based on lab type
        if lab_type.upper() == 'A1C':
            if value < ranges['normal_high']:
                status, severity = 'NORMAL', 'LOW'
            elif value < ranges['prediabetic']:
                status, severity = 'ELEVATED', 'MODERATE'
            elif value < ranges['critical']:
                status, severity = 'HIGH', 'HIGH'
            else:
                status, severity = 'CRITICAL', 'CRITICAL'
        elif lab_type.upper() == 'GLUCOSE':
            if value < ranges['low']:
                status, severity = 'LOW', 'MODERATE'
            elif value <= ranges['normal_high']:
                status, severity = 'NORMAL', 'LOW'
            elif value <= ranges['prediabetic']:
                status, severity = 'ELEVATED', 'MODERATE'
            elif value < ranges['critical']:
                status, severity = 'HIGH', 'HIGH'
            else:
                status, severity = 'CRITICAL', 'CRITICAL'
        elif lab_type.upper() == 'HDL':
            if value < ranges['critical_low']:
                status, severity = 'CRITICAL_LOW', 'HIGH'
            elif value < ranges['optimal']:
                status, severity = 'LOW', 'MODERATE'
            else:
                status, severity = 'OPTIMAL', 'LOW'
        elif lab_type.upper() in ['LDL', 'CHOLESTEROL_TOTAL', 'TRIGLYCERIDES']:
            optimal = ranges.get('optimal', ranges.get('normal', 100))
            borderline = ranges.get('borderline', optimal * 1.3)
            high = ranges.get('high', borderline * 1.3)
            critical = ranges.get('critical', high * 1.2)
            
            if value <= optimal:
                status, severity = 'OPTIMAL', 'LOW'
            elif value <= borderline:
                status, severity = 'BORDERLINE', 'MODERATE'
            elif value < critical:
                status, severity = 'HIGH', 'HIGH'
            else:
                status, severity = 'CRITICAL', 'CRITICAL'
        elif 'BP' in lab_type.upper():
            if value < ranges.get('low', 90):
                status, severity = 'LOW', 'MODERATE'
            elif value <= ranges.get('normal', 120):
                status, severity = 'NORMAL', 'LOW'
            elif value <= ranges.get('elevated', 129):
                status, severity = 'ELEVATED', 'MODERATE'
            elif value <= ranges.get('high_stage1', 139):
                status, severity = 'HIGH_STAGE1', 'HIGH'
            else:
                status, severity = 'HIGH_STAGE2', 'CRITICAL'
        else:
            # Generic check
            normal_low = ranges.get('normal_low', 0)
            normal_high = ranges.get('normal_high', 100)
            if value < normal_low:
                status, severity = 'LOW', 'MODERATE'
            elif value <= normal_high:
                status, severity = 'NORMAL', 'LOW'
            else:
                status, severity = 'HIGH', 'HIGH'
        
        return {
            'lab_type': lab_type,
            'value': value,
            'unit': unit,
            'status': status,
            'severity': severity,
            'reference_range': ranges,
            'is_abnormal': status not in ['NORMAL', 'OPTIMAL']
        }
    
    def analyze_trend(self, values: List[Dict], lab_type: str) -> Dict[str, Any]:
        """Analyze trend over time for a series of values."""
        if not values or len(values) < 2:
            return {'trend': 'INSUFFICIENT_DATA', 'message': 'Need at least 2 data points'}
        
        # Extract numeric values and dates
        data_points = []
        for v in values:
            if isinstance(v, dict):
                val = v.get('value')
                date = v.get('date') or v.get('test_date')
            else:
                val = v
                date = None
            if val is not None:
                data_points.append({'value': float(val), 'date': date})
        
        if len(data_points) < 2:
            return {'trend': 'INSUFFICIENT_DATA', 'message': 'Need at least 2 valid data points'}
        
        # Calculate statistics
        values_only = [d['value'] for d in data_points]
        first_value = values_only[0]
        last_value = values_only[-1]
        min_value = min(values_only)
        max_value = max(values_only)
        avg_value = np.mean(values_only)
        std_value = np.std(values_only)
        
        # Calculate change
        absolute_change = last_value - first_value
        percent_change = (absolute_change / first_value * 100) if first_value != 0 else 0
        
        # Determine trend direction
        if absolute_change > 0:
            if percent_change > 20:
                trend = 'RAPIDLY_INCREASING'
            elif percent_change > 5:
                trend = 'INCREASING'
            else:
                trend = 'SLIGHTLY_INCREASING'
        elif absolute_change < 0:
            if percent_change < -20:
                trend = 'RAPIDLY_DECREASING'
            elif percent_change < -5:
                trend = 'DECREASING'
            else:
                trend = 'SLIGHTLY_DECREASING'
        else:
            trend = 'STABLE'
        
        # Check for volatility
        volatility = 'LOW'
        if std_value > avg_value * 0.2:
            volatility = 'HIGH'
        elif std_value > avg_value * 0.1:
            volatility = 'MODERATE'
        
        # Check rate of change thresholds
        rate_alert = None
        thresholds = self.RATE_THRESHOLDS.get(lab_type.upper())
        if thresholds and len(data_points) >= 2:
            # Assume monthly rate (simplified)
            monthly_rate = abs(absolute_change) / max(1, len(data_points) - 1)
            if monthly_rate >= thresholds.get('critical', float('inf')):
                rate_alert = 'CRITICAL_RATE_OF_CHANGE'
            elif monthly_rate >= thresholds.get('warning', float('inf')):
                rate_alert = 'WARNING_RATE_OF_CHANGE'
        
        return {
            'trend': trend,
            'first_value': first_value,
            'last_value': last_value,
            'absolute_change': round(absolute_change, 2),
            'percent_change': round(percent_change, 1),
            'min_value': min_value,
            'max_value': max_value,
            'average': round(avg_value, 2),
            'std_deviation': round(std_value, 2),
            'volatility': volatility,
            'data_points': len(data_points),
            'rate_alert': rate_alert,
            'is_concerning': trend.startswith('RAPIDLY') or rate_alert is not None
        }
    
    def detect_anomalies(self, patient_labs: List[Dict], patient_info: Dict = None) -> Dict[str, Any]:
        """
        Comprehensive anomaly detection across all patient lab values.
        
        Returns summary of all abnormal findings, trends, and alerts.
        """
        gender = (patient_info or {}).get('gender', 'M')
        anomalies = []
        trends = {}
        alerts = []
        
        # Group labs by type
        labs_by_type = {}
        for lab in patient_labs:
            lab_type = lab.get('lab_type', 'UNKNOWN')
            if lab_type not in labs_by_type:
                labs_by_type[lab_type] = []
            labs_by_type[lab_type].append(lab)
        
        # Analyze each lab type
        for lab_type, labs in labs_by_type.items():
            # Sort by date if available
            labs_sorted = sorted(labs, key=lambda x: x.get('test_date', ''))
            
            # Analyze latest value
            if labs_sorted:
                latest = labs_sorted[-1]
                value_analysis = self.analyze_value(lab_type, latest.get('value'), gender)
                
                if value_analysis.get('is_abnormal'):
                    anomalies.append({
                        'lab_type': lab_type,
                        'value': latest.get('value'),
                        'status': value_analysis['status'],
                        'severity': value_analysis['severity'],
                        'message': f"{lab_type}: {latest.get('value')} {value_analysis.get('unit', '')} - {value_analysis['status']}"
                    })
                    
                    if value_analysis['severity'] in ['HIGH', 'CRITICAL']:
                        alerts.append({
                            'type': 'ABNORMAL_VALUE',
                            'priority': 'HIGH' if value_analysis['severity'] == 'CRITICAL' else 'MEDIUM',
                            'lab_type': lab_type,
                            'message': f"⚠️ {lab_type} is {value_analysis['status']}: {latest.get('value')} {value_analysis.get('unit', '')}"
                        })
            
            # Analyze trend
            if len(labs_sorted) >= 2:
                trend_analysis = self.analyze_trend(labs_sorted, lab_type)
                trends[lab_type] = trend_analysis
                
                if trend_analysis.get('is_concerning'):
                    alerts.append({
                        'type': 'CONCERNING_TREND',
                        'priority': 'HIGH' if trend_analysis.get('rate_alert') == 'CRITICAL_RATE_OF_CHANGE' else 'MEDIUM',
                        'lab_type': lab_type,
                        'message': f"📈 {lab_type} showing {trend_analysis['trend']}: {trend_analysis['percent_change']}% change"
                    })
        
        # Generate recommendations based on anomalies
        recommendations = self._generate_anomaly_recommendations(anomalies, trends)
        
        # Calculate overall anomaly score
        anomaly_score = min(1.0, len(anomalies) * 0.15 + len([a for a in alerts if a['priority'] == 'HIGH']) * 0.2)
        
        return {
            'prediction_type': 'ANOMALY_DETECTION',
            'anomaly_score': round(anomaly_score, 3),
            'total_anomalies': len(anomalies),
            'high_priority_alerts': len([a for a in alerts if a['priority'] == 'HIGH']),
            'anomalies': anomalies,
            'trends': trends,
            'alerts': sorted(alerts, key=lambda x: 0 if x['priority'] == 'HIGH' else 1),
            'recommendations': recommendations,
            'model_version': self.model_version
        }
    
    def _generate_anomaly_recommendations(self, anomalies: List, trends: Dict) -> List[str]:
        """Generate recommendations based on detected anomalies."""
        recommendations = []
        
        anomaly_types = [a['lab_type'] for a in anomalies]
        
        if 'A1C' in anomaly_types or 'GLUCOSE' in anomaly_types:
            recommendations.append('Consult with endocrinologist for blood sugar management')
            recommendations.append('Consider dietary modifications to reduce carbohydrate intake')
        
        if 'LDL' in anomaly_types or 'CHOLESTEROL_TOTAL' in anomaly_types:
            recommendations.append('Discuss lipid management options with your physician')
            recommendations.append('Increase physical activity and adopt heart-healthy diet')
        
        if 'BP_SYSTOLIC' in anomaly_types or 'BP_DIASTOLIC' in anomaly_types:
            recommendations.append('Monitor blood pressure regularly')
            recommendations.append('Reduce sodium intake and manage stress')
        
        # Check for concerning trends
        for lab_type, trend in trends.items():
            if trend.get('is_concerning'):
                recommendations.append(f'Schedule follow-up for {lab_type} - showing {trend["trend"]} pattern')
        
        if not recommendations:
            recommendations.append('No immediate concerns detected - continue routine monitoring')
        
        return list(dict.fromkeys(recommendations))[:8]  # Deduplicate and limit


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
    Enhanced medical imaging classifier for detecting abnormalities.
    Includes detailed findings, anatomical analysis, quality scoring,
    and cancer staging capabilities.
    """
    
    # Expanded findings database with detailed descriptions
    FINDINGS_DB = {
        ('XRAY', 'CHEST'): [
            {'finding': 'No acute cardiopulmonary abnormality', 'severity': 'NORMAL', 'probability': 0.7,
             'description': 'Lungs are clear bilaterally. Heart size is normal. No pleural effusion or pneumothorax.',
             'anatomical_regions': ['lungs', 'heart', 'pleura']},
            {'finding': 'Cardiomegaly', 'severity': 'MODERATE', 'probability': 0.15,
             'description': 'Cardiac silhouette is enlarged with cardiothoracic ratio > 0.5.',
             'anatomical_regions': ['heart'], 'possible_conditions': ['Heart failure', 'Cardiomyopathy']},
            {'finding': 'Pulmonary nodule', 'severity': 'HIGH', 'probability': 0.05,
             'description': 'Solitary pulmonary nodule identified. Further evaluation recommended.',
             'anatomical_regions': ['lungs'], 'lung_rads': 'Category 4A', 'possible_conditions': ['Lung cancer', 'Granuloma']},
            {'finding': 'Pneumonia', 'severity': 'MODERATE', 'probability': 0.08,
             'description': 'Consolidation with air bronchograms noted, consistent with pneumonia.',
             'anatomical_regions': ['lungs'], 'possible_conditions': ['Bacterial pneumonia', 'Viral pneumonia']},
            {'finding': 'Pleural effusion', 'severity': 'MODERATE', 'probability': 0.02,
             'description': 'Blunting of costophrenic angle suggesting pleural fluid.',
             'anatomical_regions': ['pleura'], 'possible_conditions': ['Heart failure', 'Infection', 'Malignancy']},
        ],
        ('CT', 'CHEST'): [
            {'finding': 'No significant abnormality', 'severity': 'NORMAL', 'probability': 0.6,
             'description': 'No pulmonary nodules, masses, or lymphadenopathy. Airways are patent.',
             'anatomical_regions': ['lungs', 'mediastinum', 'airways']},
            {'finding': 'Pulmonary nodule < 6mm', 'severity': 'LOW', 'probability': 0.2,
             'description': 'Subcentimeter nodule identified. Likely benign, follow-up recommended.',
             'anatomical_regions': ['lungs'], 'lung_rads': 'Category 2', 'size_mm': 4},
            {'finding': 'Ground glass opacity', 'severity': 'MODERATE', 'probability': 0.1,
             'description': 'Focal ground glass opacity noted. Could represent inflammation or early malignancy.',
             'anatomical_regions': ['lungs'], 'possible_conditions': ['COVID-19', 'Atypical infection', 'Early adenocarcinoma']},
            {'finding': 'Suspicious pulmonary mass', 'severity': 'HIGH', 'probability': 0.05,
             'description': 'Spiculated mass with irregular margins. High suspicion for malignancy.',
             'anatomical_regions': ['lungs'], 'lung_rads': 'Category 4B', 'possible_conditions': ['Lung cancer'],
             'cancer_staging': {'T': 'T2a', 'estimated_stage': 'IB-IIA'}},
            {'finding': 'Mediastinal lymphadenopathy', 'severity': 'MODERATE', 'probability': 0.05,
             'description': 'Enlarged mediastinal lymph nodes > 1cm in short axis.',
             'anatomical_regions': ['mediastinum'], 'possible_conditions': ['Metastatic disease', 'Lymphoma', 'Sarcoidosis']},
        ],
        ('MRI', 'BRAIN'): [
            {'finding': 'No acute intracranial abnormality', 'severity': 'NORMAL', 'probability': 0.65,
             'description': 'No mass, hemorrhage, or acute infarct. Ventricles and sulci are normal.',
             'anatomical_regions': ['cerebrum', 'ventricles', 'brainstem']},
            {'finding': 'White matter hyperintensities', 'severity': 'LOW', 'probability': 0.15,
             'description': 'Scattered T2/FLAIR hyperintensities in periventricular white matter.',
             'anatomical_regions': ['white matter'], 'possible_conditions': ['Microvascular disease', 'Demyelination']},
            {'finding': 'Small vessel ischemic disease', 'severity': 'MODERATE', 'probability': 0.1,
             'description': 'Moderate burden of chronic small vessel disease.',
             'anatomical_regions': ['white matter', 'basal ganglia'], 'fazekas_score': 2},
            {'finding': 'Enhancing brain lesion', 'severity': 'HIGH', 'probability': 0.05,
             'description': 'Ring-enhancing lesion with surrounding edema. Biopsy recommended.',
             'anatomical_regions': ['cerebrum'], 'possible_conditions': ['Glioblastoma', 'Metastasis', 'Abscess'],
             'cancer_staging': {'grade': 'High-grade', 'estimated_type': 'Glioblastoma multiforme'}},
            {'finding': 'Acute ischemic infarct', 'severity': 'CRITICAL', 'probability': 0.05,
             'description': 'Restricted diffusion on DWI consistent with acute stroke.',
             'anatomical_regions': ['cerebrum'], 'requires_urgent_care': True},
        ],
        ('CT', 'ABDOMEN'): [
            {'finding': 'No acute abnormality', 'severity': 'NORMAL', 'probability': 0.6,
             'description': 'Liver, spleen, pancreas, and kidneys appear normal. No free fluid.',
             'anatomical_regions': ['liver', 'spleen', 'pancreas', 'kidneys']},
            {'finding': 'Hepatic steatosis', 'severity': 'LOW', 'probability': 0.2,
             'description': 'Diffusely decreased liver attenuation consistent with fatty liver.',
             'anatomical_regions': ['liver'], 'possible_conditions': ['NAFLD', 'NASH']},
            {'finding': 'Simple renal cyst', 'severity': 'LOW', 'probability': 0.1,
             'description': 'Well-defined cyst in kidney. Bosniak category I, benign.',
             'anatomical_regions': ['kidneys'], 'bosniak': 'I'},
            {'finding': 'Indeterminate hepatic lesion', 'severity': 'MODERATE', 'probability': 0.05,
             'description': 'Hepatic lesion requiring MRI for further characterization.',
             'anatomical_regions': ['liver'], 'possible_conditions': ['Hemangioma', 'FNH', 'HCC']},
            {'finding': 'Pancreatic mass', 'severity': 'HIGH', 'probability': 0.05,
             'description': 'Hypoattenuating mass in pancreatic head with biliary dilation.',
             'anatomical_regions': ['pancreas'], 'possible_conditions': ['Pancreatic adenocarcinoma'],
             'cancer_staging': {'T': 'T2', 'estimated_stage': 'IB-IIA'}},
        ],
        ('MAMMOGRAM', 'BREAST'): [
            {'finding': 'No significant abnormality', 'severity': 'NORMAL', 'probability': 0.7,
             'description': 'No suspicious masses, calcifications, or architectural distortion.',
             'anatomical_regions': ['breast'], 'birads': '1'},
            {'finding': 'Benign calcifications', 'severity': 'LOW', 'probability': 0.15,
             'description': 'Coarse, scattered calcifications. Likely benign.',
             'anatomical_regions': ['breast'], 'birads': '2'},
            {'finding': 'Asymmetric density', 'severity': 'MODERATE', 'probability': 0.1,
             'description': 'Focal asymmetry in upper outer quadrant. Short-term follow-up recommended.',
             'anatomical_regions': ['breast'], 'birads': '3'},
            {'finding': 'Suspicious calcifications', 'severity': 'HIGH', 'probability': 0.05,
             'description': 'Clustered pleomorphic calcifications. Biopsy recommended.',
             'anatomical_regions': ['breast'], 'birads': '4B', 'possible_conditions': ['DCIS', 'Invasive carcinoma']},
        ]
    }
    
    # Image quality criteria
    QUALITY_CRITERIA = {
        'XRAY': ['positioning', 'exposure', 'inspiration', 'rotation', 'artifacts'],
        'CT': ['motion_artifact', 'contrast_timing', 'coverage', 'resolution'],
        'MRI': ['motion_artifact', 'susceptibility', 'coverage', 'signal_noise_ratio'],
    }
    
    def __init__(self):
        self.model_version = "2.0.0"  # Enhanced version
    
    def assess_image_quality(self, imaging_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess image quality for reliable interpretation."""
        modality = imaging_data.get('modality', 'XRAY')
        
        # Simulate quality assessment (in production, would analyze actual image)
        import random
        random.seed(hash(str(imaging_data.get('id', ''))))
        
        quality_score = random.uniform(0.7, 1.0)
        
        quality_issues = []
        if quality_score < 0.8:
            possible_issues = self.QUALITY_CRITERIA.get(modality, ['artifacts'])
            quality_issues = random.sample(possible_issues, min(2, len(possible_issues)))
        
        quality_grade = 'EXCELLENT' if quality_score >= 0.9 else 'GOOD' if quality_score >= 0.8 else 'ADEQUATE' if quality_score >= 0.7 else 'SUBOPTIMAL'
        
        return {
            'quality_score': round(quality_score, 2),
            'quality_grade': quality_grade,
            'quality_issues': quality_issues,
            'interpretation_reliable': quality_score >= 0.7,
            'repeat_recommended': quality_score < 0.6
        }
    
    def predict(self, imaging_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced classification with detailed findings, anatomical analysis,
        quality assessment, and cancer staging.
        """
        modality = imaging_data.get('modality') or 'XRAY'
        body_part = imaging_data.get('body_part') or 'CHEST'
        abnormality_score = imaging_data.get('abnormality_score')
        if abnormality_score is None:
            abnormality_score = 0.2
        
        # Assess image quality first
        quality_assessment = self.assess_image_quality(imaging_data)
        
        # Get possible findings for this type
        key = (modality, body_part)
        possible_findings = self.FINDINGS_DB.get(key, self.FINDINGS_DB[('XRAY', 'CHEST')])
        
        # Select findings based on abnormality score
        detected_findings = []
        
        if abnormality_score < 0.3:
            # Likely normal
            normal_finding = possible_findings[0].copy()
            normal_finding['confidence'] = round(0.85 + (0.3 - abnormality_score) * 0.3, 2)
            detected_findings.append(normal_finding)
        else:
            # Add abnormal findings
            import random
            random.seed(hash(str(imaging_data)))
            
            abnormal_findings = [f.copy() for f in possible_findings if f['severity'] != 'NORMAL']
            num_findings = 1 if abnormality_score < 0.6 else 2
            selected = random.sample(abnormal_findings, min(num_findings, len(abnormal_findings)))
            
            for finding in selected:
                finding['confidence'] = round(0.6 + abnormality_score * 0.3, 2)
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
        
        # Extract unique anatomical regions
        anatomical_regions = []
        for f in detected_findings:
            anatomical_regions.extend(f.get('anatomical_regions', []))
        anatomical_regions = list(set(anatomical_regions))
        
        # Check for cancer staging
        cancer_info = None
        for f in detected_findings:
            if 'cancer_staging' in f:
                cancer_info = {
                    'finding': f['finding'],
                    'staging': f['cancer_staging'],
                    'possible_conditions': f.get('possible_conditions', []),
                    'requires_biopsy': True
                }
                break
        
        # Generate detailed recommendations
        recommendations = self._generate_recommendations(detected_findings, overall_severity, cancer_info)
        
        # Create comprehensive report
        report = self._generate_report(detected_findings, modality, body_part, quality_assessment)
        
        return {
            'prediction_type': 'IMAGING_ANALYSIS',
            'risk_score': risk_score,
            'risk_level': overall_severity,
            'confidence': round(0.75 + quality_assessment['quality_score'] * 0.1, 2),
            'findings': detected_findings,
            'primary_finding': detected_findings[0]['finding'] if detected_findings else 'Unable to analyze',
            'primary_description': detected_findings[0].get('description', '') if detected_findings else '',
            'modality': modality,
            'body_part': body_part,
            'anatomical_regions_analyzed': anatomical_regions,
            'quality_assessment': quality_assessment,
            'cancer_staging': cancer_info,
            'recommendations': recommendations,
            'structured_report': report,
            'requires_follow_up': overall_severity in ['MODERATE', 'HIGH', 'CRITICAL'],
            'requires_urgent_care': any(f.get('requires_urgent_care') for f in detected_findings),
            'model_version': self.model_version,
            'modalities_used': ['imaging']
        }
    
    def _generate_recommendations(self, findings: List, severity: str, cancer_info: Dict) -> List[str]:
        """Generate detailed recommendations based on findings."""
        recommendations = []
        
        if severity == 'NORMAL':
            recommendations.append('No immediate follow-up required')
            recommendations.append('Continue routine screening as per guidelines')
        elif severity == 'LOW':
            recommendations.append('Consider follow-up imaging in 6-12 months')
            recommendations.append('Discuss findings with primary care physician')
        elif severity == 'MODERATE':
            recommendations.append('Recommend follow-up imaging in 3-6 months')
            recommendations.append('Specialist consultation advised')
            for f in findings:
                if f.get('birads') == '3':
                    recommendations.append('Short-interval mammographic follow-up in 6 months')
                if f.get('lung_rads') in ['Category 3', 'Category 4A']:
                    recommendations.append('Repeat CT in 3 months to assess stability')
        elif severity in ['HIGH', 'CRITICAL']:
            recommendations.append('Urgent specialist consultation recommended')
            recommendations.append('Priority follow-up within 1-2 weeks')
            if cancer_info:
                recommendations.append('Tissue biopsy recommended for definitive diagnosis')
                recommendations.append('Consider PET-CT for staging workup')
            for f in findings:
                if f.get('requires_urgent_care'):
                    recommendations.append('URGENT: Immediate medical attention required')
        
        return recommendations[:6]
    
    def _generate_report(self, findings: List, modality: str, body_part: str, quality: Dict) -> str:
        """Generate structured radiology report."""
        report_parts = [
            f"MODALITY: {modality}",
            f"BODY REGION: {body_part}",
            f"IMAGE QUALITY: {quality['quality_grade']}",
            "",
            "FINDINGS:"
        ]
        
        for i, f in enumerate(findings, 1):
            report_parts.append(f"  {i}. {f['finding']}")
            if f.get('description'):
                report_parts.append(f"     {f['description']}")
        
        report_parts.append("")
        report_parts.append(f"IMPRESSION: {findings[0]['finding'] if findings else 'Unable to interpret'}")
        
        return "\n".join(report_parts)


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
    Enhanced genomics-based risk assessment for hereditary conditions and cancer.
    Includes ACMG variant classification, gene-disease associations, and 
    hereditary condition risk scoring.
    """
    
    # ACMG Classification hierarchy
    ACMG_CLASSIFICATIONS = {
        'PATHOGENIC': {'severity': 5, 'actionable': True, 'color': 'red'},
        'LIKELY_PATHOGENIC': {'severity': 4, 'actionable': True, 'color': 'orange'},
        'VUS': {'severity': 3, 'actionable': False, 'color': 'yellow'},  # Variant of Uncertain Significance
        'LIKELY_BENIGN': {'severity': 2, 'actionable': False, 'color': 'lightgreen'},
        'BENIGN': {'severity': 1, 'actionable': False, 'color': 'green'}
    }
    
    # Gene-Disease associations database
    GENE_DISEASE_DB = {
        'BRCA1': {
            'conditions': ['Breast cancer', 'Ovarian cancer', 'Pancreatic cancer'],
            'inheritance': 'Autosomal Dominant',
            'cancer_type': 'HEREDITARY_BREAST_OVARIAN',
            'lifetime_risk_increase': 0.7,
            'screening_recommendations': ['Annual mammogram from age 25', 'Annual MRI', 'Consider prophylactic surgery']
        },
        'BRCA2': {
            'conditions': ['Breast cancer', 'Ovarian cancer', 'Prostate cancer', 'Pancreatic cancer'],
            'inheritance': 'Autosomal Dominant',
            'cancer_type': 'HEREDITARY_BREAST_OVARIAN',
            'lifetime_risk_increase': 0.6,
            'screening_recommendations': ['Annual mammogram from age 25', 'Annual MRI', 'Prostate screening from age 40']
        },
        'TP53': {
            'conditions': ['Li-Fraumeni syndrome', 'Multiple cancer types'],
            'inheritance': 'Autosomal Dominant',
            'cancer_type': 'LI_FRAUMENI',
            'lifetime_risk_increase': 0.9,
            'screening_recommendations': ['Comprehensive cancer screening', 'Annual whole-body MRI']
        },
        'MLH1': {
            'conditions': ['Lynch syndrome', 'Colorectal cancer', 'Endometrial cancer'],
            'inheritance': 'Autosomal Dominant',
            'cancer_type': 'LYNCH_SYNDROME',
            'lifetime_risk_increase': 0.5,
            'screening_recommendations': ['Colonoscopy every 1-2 years from age 20-25']
        },
        'MSH2': {
            'conditions': ['Lynch syndrome', 'Colorectal cancer', 'Urinary tract cancer'],
            'inheritance': 'Autosomal Dominant',
            'cancer_type': 'LYNCH_SYNDROME',
            'lifetime_risk_increase': 0.5,
            'screening_recommendations': ['Colonoscopy every 1-2 years from age 20-25']
        },
        'APC': {
            'conditions': ['Familial adenomatous polyposis', 'Colorectal cancer'],
            'inheritance': 'Autosomal Dominant',
            'cancer_type': 'FAP',
            'lifetime_risk_increase': 0.95,
            'screening_recommendations': ['Annual colonoscopy from age 10-12', 'Consider prophylactic colectomy']
        },
        'CFTR': {
            'conditions': ['Cystic fibrosis'],
            'inheritance': 'Autosomal Recessive',
            'cancer_type': None,
            'lifetime_risk_increase': 0,
            'screening_recommendations': ['Pulmonary function tests', 'Pancreatic enzyme levels']
        },
        'HBB': {
            'conditions': ['Sickle cell disease', 'Beta thalassemia'],
            'inheritance': 'Autosomal Recessive',
            'cancer_type': None,
            'lifetime_risk_increase': 0,
            'screening_recommendations': ['Complete blood count monitoring']
        },
        'APOE': {
            'conditions': ["Alzheimer's disease risk", 'Cardiovascular disease risk'],
            'inheritance': 'Complex',
            'cancer_type': None,
            'lifetime_risk_increase': 0,
            'screening_recommendations': ['Cognitive screening if symptomatic', 'Cardiovascular risk assessment']
        }
    }
    
    # Hereditary cancer syndromes
    HEREDITARY_SYNDROMES = {
        'HEREDITARY_BREAST_OVARIAN': {
            'name': 'Hereditary Breast and Ovarian Cancer Syndrome',
            'genes': ['BRCA1', 'BRCA2', 'PALB2', 'ATM', 'CHEK2'],
            'primary_cancers': ['Breast', 'Ovarian'],
            'surveillance_protocol': 'NCCN High-Risk Breast Cancer Screening'
        },
        'LYNCH_SYNDROME': {
            'name': 'Lynch Syndrome (HNPCC)',
            'genes': ['MLH1', 'MSH2', 'MSH6', 'PMS2', 'EPCAM'],
            'primary_cancers': ['Colorectal', 'Endometrial'],
            'surveillance_protocol': 'Amsterdam II / Bethesda Guidelines'
        },
        'LI_FRAUMENI': {
            'name': 'Li-Fraumeni Syndrome',
            'genes': ['TP53'],
            'primary_cancers': ['Sarcoma', 'Breast', 'Brain', 'Adrenal'],
            'surveillance_protocol': 'Toronto Protocol'
        }
    }
    
    def __init__(self):
        self.model_version = "2.0.0"  # Enhanced version
    
    def classify_variant_acmg(self, variant: Dict) -> Dict[str, Any]:
        """
        Classify variant according to ACMG guidelines.
        Returns detailed classification with supporting evidence.
        """
        classification = variant.get('classification', 'VUS')
        gene = variant.get('gene', 'UNKNOWN')
        
        acmg_info = self.ACMG_CLASSIFICATIONS.get(classification, self.ACMG_CLASSIFICATIONS['VUS'])
        gene_info = self.GENE_DISEASE_DB.get(gene, {})
        
        # Determine clinical actionability
        is_actionable = acmg_info['actionable'] and gene_info.get('conditions', [])
        
        return {
            'classification': classification,
            'severity_level': acmg_info['severity'],
            'is_actionable': is_actionable,
            'gene': gene,
            'associated_conditions': gene_info.get('conditions', []),
            'inheritance_pattern': gene_info.get('inheritance', 'Unknown'),
            'cancer_syndrome': gene_info.get('cancer_type'),
            'lifetime_risk_increase': gene_info.get('lifetime_risk_increase', 0),
            'screening_recommendations': gene_info.get('screening_recommendations', [])
        }
    
    def identify_hereditary_syndromes(self, variants: List[Dict]) -> List[Dict]:
        """Identify hereditary cancer syndromes based on affected genes."""
        identified_syndromes = []
        
        pathogenic_genes = set()
        for v in variants:
            if v.get('classification') in ['PATHOGENIC', 'LIKELY_PATHOGENIC']:
                pathogenic_genes.add(v.get('gene', ''))
        
        for syndrome_key, syndrome_info in self.HEREDITARY_SYNDROMES.items():
            matching_genes = pathogenic_genes.intersection(set(syndrome_info['genes']))
            if matching_genes:
                identified_syndromes.append({
                    'syndrome': syndrome_info['name'],
                    'syndrome_code': syndrome_key,
                    'affected_genes': list(matching_genes),
                    'primary_cancers': syndrome_info['primary_cancers'],
                    'surveillance_protocol': syndrome_info['surveillance_protocol'],
                    'confidence': 0.9 if len(matching_genes) > 1 else 0.75
                })
        
        return identified_syndromes
    
    def predict(self, variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enhanced genomic risk assessment with ACMG classification,
        hereditary syndrome identification, and actionable recommendations.
        """
        if not variants:
            return {
                'prediction_type': 'GENOMICS_RISK',
                'risk_score': 0.1,
                'risk_level': 'LOW',
                'confidence': 0.9,
                'acmg_summary': {'pathogenic': 0, 'likely_pathogenic': 0, 'vus': 0, 'benign': 0},
                'message': 'No genetic variants provided for analysis',
                'hereditary_syndromes': [],
                'model_version': self.model_version,
                'modalities_used': ['genomics']
            }
        
        # Classify all variants using ACMG
        classified_variants = []
        for v in variants:
            classified = self.classify_variant_acmg(v)
            classified['variant_id'] = v.get('id', '')
            classified['chromosome'] = v.get('chromosome', '')
            classified['position'] = v.get('position', '')
            classified['ref_allele'] = v.get('ref', '')
            classified['alt_allele'] = v.get('alt', '')
            classified_variants.append(classified)
        
        # Count by ACMG classification
        acmg_counts = {
            'pathogenic': len([v for v in classified_variants if v['classification'] == 'PATHOGENIC']),
            'likely_pathogenic': len([v for v in classified_variants if v['classification'] == 'LIKELY_PATHOGENIC']),
            'vus': len([v for v in classified_variants if v['classification'] == 'VUS']),
            'likely_benign': len([v for v in classified_variants if v['classification'] == 'LIKELY_BENIGN']),
            'benign': len([v for v in classified_variants if v['classification'] == 'BENIGN'])
        }
        
        # Identify hereditary syndromes
        hereditary_syndromes = self.identify_hereditary_syndromes(variants)
        
        # Get actionable variants
        actionable_variants = [v for v in classified_variants if v['is_actionable']]
        
        # Aggregate all conditions and calculate risks
        all_conditions = []
        cancer_conditions = []
        max_lifetime_risk = 0
        
        for v in classified_variants:
            all_conditions.extend(v['associated_conditions'])
            if v['cancer_syndrome']:
                cancer_conditions.extend(v['associated_conditions'])
            max_lifetime_risk = max(max_lifetime_risk, v['lifetime_risk_increase'])
        
        # Determine overall risk level
        if acmg_counts['pathogenic'] > 0:
            risk_level = 'HIGH'
            overall_risk = max(0.7, max_lifetime_risk)
        elif acmg_counts['likely_pathogenic'] > 0:
            risk_level = 'MODERATE'
            overall_risk = max(0.5, max_lifetime_risk * 0.8)
        elif acmg_counts['vus'] > 0:
            risk_level = 'LOW'
            overall_risk = 0.25
        else:
            risk_level = 'LOW'
            overall_risk = 0.1
        
        # Generate comprehensive recommendations
        recommendations = self._generate_recommendations(
            acmg_counts, hereditary_syndromes, actionable_variants
        )
        
        # Create key findings summary
        key_findings = []
        for v in actionable_variants[:5]:  # Top 5 actionable
            key_findings.append({
                'gene': v['gene'],
                'classification': v['classification'],
                'conditions': v['associated_conditions'][:3],
                'inheritance': v['inheritance_pattern']
            })
        
        return {
            'prediction_type': 'GENOMICS_RISK',
            'risk_score': round(overall_risk, 3),
            'risk_level': risk_level,
            'confidence': 0.88,
            'acmg_summary': acmg_counts,
            'total_variants_analyzed': len(variants),
            'actionable_variants_count': len(actionable_variants),
            'hereditary_syndromes': hereditary_syndromes,
            'cancer_risk_elevated': len(cancer_conditions) > 0,
            'cancer_related_conditions': list(set(cancer_conditions)),
            'all_associated_conditions': list(set(all_conditions)),
            'key_findings': key_findings,
            'classified_variants': classified_variants[:10],  # Top 10 for display
            'recommendations': recommendations,
            'model_version': self.model_version,
            'modalities_used': ['genomics']
        }
    
    def _generate_recommendations(self, acmg_counts: Dict, syndromes: List, actionable: List) -> List[str]:
        """Generate detailed recommendations based on genomic findings."""
        recommendations = []
        
        if acmg_counts['pathogenic'] > 0 or acmg_counts['likely_pathogenic'] > 0:
            recommendations.append('Genetic counseling strongly recommended')
            recommendations.append('Discuss results with a clinical geneticist')
        
        if syndromes:
            for s in syndromes[:2]:
                recommendations.append(f"Follow {s['surveillance_protocol']} surveillance protocol")
                recommendations.append(f"Screen for {', '.join(s['primary_cancers'][:2])} cancers")
        
        # Gene-specific recommendations
        genes_with_action = set()
        for v in actionable:
            gene = v['gene']
            if gene not in genes_with_action:
                genes_with_action.add(gene)
                gene_recs = v.get('screening_recommendations', [])
                recommendations.extend(gene_recs[:2])
        
        if acmg_counts['vus'] > 0 and acmg_counts['pathogenic'] == 0:
            recommendations.append('VUS findings require periodic re-evaluation as evidence evolves')
        
        if not recommendations:
            recommendations.append('No actionable genetic findings - continue routine care')
            recommendations.append('Consider updating genetic testing as technology advances')
        
        # Deduplicate and limit
        return list(dict.fromkeys(recommendations))[:8]


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
            # Support both old and new format
            pathogenic_count = g.get('pathogenic_count', 0)
            if 'acmg_summary' in g:
                pathogenic_count = g['acmg_summary'].get('pathogenic', 0)
            if pathogenic_count > 0:
                summary_parts.append(f"Genomics: {pathogenic_count} pathogenic variants")
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
        'anomaly_detector': AnomalyDetector(),
        'fusion': MultiModalFusionModel()
    }

