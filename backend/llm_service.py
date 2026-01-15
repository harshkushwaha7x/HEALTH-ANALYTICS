"""
LLM Integration Module for Health Analytics.
Uses Gemini for text analysis and Groq for image analysis.
"""

import os
import json
import base64
import requests
from typing import Dict, List, Any, Optional

# API Keys - set these as environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

# API Endpoints
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GeminiLabExtractor:
    """Use Gemini to extract lab values from unstructured medical text."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEMINI_API_KEY
        
    def extract_lab_values(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract lab values from medical report text using Gemini.
        
        Args:
            text: Raw text from a medical report
            
        Returns:
            List of extracted lab values with type, value, unit, status
        """
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not set, using fallback extraction")
            return []
        
        prompt = f"""Analyze this medical lab report and extract all lab values.
Return ONLY valid JSON array with this exact format:
[
    {{"lab_type": "GLUCOSE", "value": 83, "unit": "mg/dL", "status": "NORMAL"}},
    {{"lab_type": "CHOLESTEROL_TOTAL", "value": 221, "unit": "mg/dL", "status": "HIGH"}}
]

Lab types must be one of: A1C, GLUCOSE, CHOLESTEROL_TOTAL, LDL, HDL, TRIGLYCERIDES, 
BP_SYSTOLIC, BP_DIASTOLIC, CREATININE, HEMOGLOBIN, WBC, PLATELETS, HEART_RATE

Status must be: NORMAL, HIGH, or LOW (based on medical reference ranges)

Reference ranges:
- A1C: Normal < 5.6%, Pre-diabetic 5.7-6.4%, Diabetic > 6.4%
- Glucose: Normal 70-100 mg/dL
- Total Cholesterol: Normal < 200 mg/dL
- LDL: Optimal < 100 mg/dL
- HDL: Normal > 40 mg/dL (higher is better)
- Triglycerides: Normal < 150 mg/dL
- Blood Pressure: Normal 120/80 mmHg

Medical Report Text:
{text[:4000]}

Return ONLY the JSON array, no other text."""

        try:
            response = requests.post(
                f"{GEMINI_API_URL}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 2048
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                
                # Clean up the response
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                # Parse JSON
                labs = json.loads(content)
                
                # Add reference ranges
                ref_ranges = {
                    'A1C': (4.0, 5.6, '%'),
                    'GLUCOSE': (70, 100, 'mg/dL'),
                    'CHOLESTEROL_TOTAL': (0, 200, 'mg/dL'),
                    'LDL': (0, 100, 'mg/dL'),
                    'HDL': (40, 999, 'mg/dL'),
                    'TRIGLYCERIDES': (0, 150, 'mg/dL'),
                    'BP_SYSTOLIC': (90, 120, 'mmHg'),
                    'BP_DIASTOLIC': (60, 80, 'mmHg'),
                    'CREATININE': (0.7, 1.3, 'mg/dL'),
                    'HEMOGLOBIN': (12.0, 17.5, 'g/dL'),
                }
                
                for lab in labs:
                    lab_type = lab.get('lab_type', '').upper()
                    if lab_type in ref_ranges:
                        ref = ref_ranges[lab_type]
                        lab['reference_low'] = ref[0]
                        lab['reference_high'] = ref[1]
                        lab['unit'] = lab.get('unit') or ref[2]
                
                return labs
            else:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error extracting labs with Gemini: {e}")
            return []
    
    def generate_health_recommendations(self, patient_data: Dict) -> List[str]:
        """
        Generate personalized health recommendations using Gemini.
        
        Args:
            patient_data: Dict containing lab values, conditions, etc.
            
        Returns:
            List of personalized recommendations
        """
        if not self.api_key:
            return ["Unable to generate recommendations - API key not configured"]
        
        prompt = f"""Based on this patient's health data, provide 5 specific, actionable health recommendations.

Patient Data:
- Age: {patient_data.get('age', 'Unknown')}
- Gender: {patient_data.get('gender', 'Unknown')}
- Lab Values: {json.dumps(patient_data.get('labs', []))}
- Conditions: {patient_data.get('conditions', [])}
- Risk Score: {patient_data.get('risk_score', 'Unknown')}

Provide recommendations as a JSON array of strings, like:
["Recommendation 1", "Recommendation 2", ...]

Be specific and actionable. Include dietary, exercise, and lifestyle recommendations.
Return ONLY the JSON array."""

        try:
            response = requests.post(
                f"{GEMINI_API_URL}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1024
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                
                # Clean and parse
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                    
                return json.loads(content.strip())
            else:
                return ["Unable to generate recommendations at this time"]
                
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations at this time"]


class GroqImageAnalyzer:
    """Use Groq with LLaVA/Vision models for medical image analysis."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_xray(self, image_path: str, body_part: str = "chest") -> Dict[str, Any]:
        """
        Analyze an X-ray image using Groq's vision model.
        
        Args:
            image_path: Path to the X-ray image
            body_part: Body part (chest, spine, etc.)
            
        Returns:
            Analysis results with findings and risk score
        """
        if not self.api_key:
            print("Warning: GROQ_API_KEY not set, using simulated analysis")
            return self._simulated_analysis(body_part)
        
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return self._simulated_analysis(body_part)
        
        try:
            # Encode the image
            base64_image = self.encode_image(image_path)
            
            # Determine image type
            ext = os.path.splitext(image_path)[1].lower()
            media_type = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/png"
            
            prompt = f"""You are a radiologist AI assistant. Analyze this {body_part} X-ray image.

Provide your analysis in the following JSON format:
{{
    "primary_finding": "Main observation in 1 sentence",
    "findings": ["Finding 1", "Finding 2", "Finding 3"],
    "abnormality_score": 0.0-1.0 (0=completely normal, 1=severe abnormality),
    "quality": "GOOD/FAIR/POOR",
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "urgent": true/false
}}

Be thorough but concise. If the image appears normal, indicate that clearly.
Return ONLY valid JSON."""

            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llava-v1.5-7b-4096-preview",  # Groq's vision model
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{media_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1024
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Clean and parse JSON
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                
                analysis = json.loads(content.strip())
                analysis['model_used'] = 'groq-llava'
                analysis['body_part'] = body_part
                return analysis
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return self._simulated_analysis(body_part)
                
        except Exception as e:
            print(f"Error analyzing image with Groq: {e}")
            return self._simulated_analysis(body_part)
    
    def _simulated_analysis(self, body_part: str) -> Dict[str, Any]:
        """Fallback simulated analysis when API is unavailable."""
        import hashlib
        
        findings_db = {
            'chest': [
                "No acute cardiopulmonary abnormality",
                "Clear lung fields bilaterally",
                "Normal cardiac silhouette",
                "No pleural effusion detected",
                "No visible masses or nodules"
            ],
            'spine': [
                "Normal spinal alignment",
                "No compression fractures",
                "Disc spaces appear preserved",
                "No significant degenerative changes"
            ],
            'brain': [
                "No acute intracranial abnormality",
                "Normal ventricular size",
                "No mass effect observed"
            ]
        }
        
        findings = findings_db.get(body_part.lower(), findings_db['chest'])
        
        # Deterministic score based on body part hash (same body part = same score)
        hash_value = int(hashlib.md5(body_part.encode()).hexdigest()[:8], 16)
        abnormality_score = round(0.1 + (hash_value % 250) / 1000.0, 3)
        
        # Deterministic finding selection based on hash
        findings_count = min(3, len(findings))
        selected_findings = findings[:findings_count]
        
        return {
            "primary_finding": findings[0],
            "findings": selected_findings,
            "abnormality_score": abnormality_score,
            "quality": "GOOD",
            "recommendations": ["No immediate follow-up required"],
            "urgent": False,
            "model_used": "simulated",
            "body_part": body_part,
            "note": "Simulated analysis - set GROQ_API_KEY for real AI analysis"
        }


# Convenience functions
def extract_labs_with_llm(text: str) -> List[Dict[str, Any]]:
    """Extract lab values using Gemini LLM."""
    extractor = GeminiLabExtractor()
    return extractor.extract_lab_values(text)


def analyze_xray_with_llm(image_path: str, body_part: str = "chest") -> Dict[str, Any]:
    """Analyze X-ray using Groq vision model."""
    analyzer = GroqImageAnalyzer()
    return analyzer.analyze_xray(image_path, body_part)


def generate_recommendations_with_llm(patient_data: Dict) -> List[str]:
    """Generate health recommendations using Gemini."""
    extractor = GeminiLabExtractor()
    return extractor.generate_health_recommendations(patient_data)


# Test functions
if __name__ == "__main__":
    # Test Gemini extraction
    sample_text = """
    Glucose fasting (PHO) 83 mg/dl (70-99 Normal)
    Cholesterol, total (PHO) 221 high mg/dl (100-200 Normal)
    Triglycerides (PHO) 1315 high mg/dl (<150 Normal)
    HDL Cholesterol, direct 22.5 low mg/dl (>50 Normal)
    LDL Cholesterol, direct 36 mg/dl (<100 Optimal)
    """
    
    print("Testing Gemini Lab Extraction...")
    labs = extract_labs_with_llm(sample_text)
    print(json.dumps(labs, indent=2))
    
    print("\nTesting Groq X-Ray Analysis (simulated)...")
    analysis = analyze_xray_with_llm("test.jpg", "chest")
    print(json.dumps(analysis, indent=2))
