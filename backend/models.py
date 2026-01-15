"""
Database models for Health Analytics application.
Defines SQLAlchemy models for patients, labs, imaging, genomics, notes, and predictions.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Patient(db.Model):
    """Patient demographic and contact information."""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    blood_type = db.Column(db.String(5))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lab_results = db.relationship('LabResult', backref='patient', lazy=True, cascade='all, delete-orphan')
    imaging_studies = db.relationship('ImagingStudy', backref='patient', lazy=True, cascade='all, delete-orphan')
    genomics_data = db.relationship('GenomicsData', backref='patient', lazy=True, cascade='all, delete-orphan')
    clinical_notes = db.relationship('ClinicalNote', backref='patient', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'blood_type': self.blood_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LabResult(db.Model):
    """Laboratory test results - A1C, cholesterol, blood pressure, etc."""
    __tablename__ = 'lab_results'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    lab_type = db.Column(db.String(50), nullable=False)  # A1C, LDL, HDL, GLUCOSE, BP_SYSTOLIC, BP_DIASTOLIC, etc.
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    reference_low = db.Column(db.Float)
    reference_high = db.Column(db.Float)
    status = db.Column(db.String(20))  # NORMAL, HIGH, LOW, CRITICAL
    source_file = db.Column(db.String(255))  # Original file name
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'lab_type': self.lab_type,
            'value': self.value,
            'unit': self.unit,
            'reference_low': self.reference_low,
            'reference_high': self.reference_high,
            'status': self.status,
            'source_file': self.source_file,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }


class ImagingStudy(db.Model):
    """Medical imaging studies - X-rays, CT scans, MRIs."""
    __tablename__ = 'imaging_studies'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    modality = db.Column(db.String(20), nullable=False)  # XRAY, CT, MRI
    body_part = db.Column(db.String(50))  # CHEST, BRAIN, ABDOMEN, etc.
    file_path = db.Column(db.String(255))
    thumbnail_path = db.Column(db.String(255))
    findings = db.Column(db.Text)  # JSON string of detected findings
    abnormality_score = db.Column(db.Float)  # 0-1 probability of abnormality
    heatmap_path = db.Column(db.String(255))  # Grad-CAM visualization
    study_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        findings_parsed = None
        if self.findings:
            try:
                findings_parsed = json.loads(self.findings)
            except:
                findings_parsed = self.findings
        
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'modality': self.modality,
            'body_part': self.body_part,
            'file_path': self.file_path,
            'thumbnail_path': self.thumbnail_path,
            'findings': findings_parsed,
            'abnormality_score': self.abnormality_score,
            'heatmap_path': self.heatmap_path,
            'study_date': self.study_date.isoformat() if self.study_date else None
        }


class GenomicsData(db.Model):
    """Genomics variant data for cancer and disease risk analysis."""
    __tablename__ = 'genomics_data'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    gene = db.Column(db.String(50), nullable=False)  # BRCA1, BRCA2, TP53, etc.
    variant = db.Column(db.String(100))  # HGVS notation
    chromosome = db.Column(db.String(10))
    position = db.Column(db.Integer)
    reference_allele = db.Column(db.String(50))
    alternate_allele = db.Column(db.String(50))
    classification = db.Column(db.String(30))  # PATHOGENIC, LIKELY_PATHOGENIC, VUS, BENIGN
    pathogenicity_score = db.Column(db.Float)  # 0-1 score
    associated_conditions = db.Column(db.Text)  # JSON array of conditions
    source_file = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        conditions = None
        if self.associated_conditions:
            try:
                conditions = json.loads(self.associated_conditions)
            except:
                conditions = self.associated_conditions
        
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'gene': self.gene,
            'variant': self.variant,
            'chromosome': self.chromosome,
            'position': self.position,
            'classification': self.classification,
            'pathogenicity_score': self.pathogenicity_score,
            'associated_conditions': conditions
        }


class ClinicalNote(db.Model):
    """Doctor's notes and clinical observations."""
    __tablename__ = 'clinical_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    note_type = db.Column(db.String(50))  # PROGRESS, DISCHARGE, CONSULTATION, etc.
    content = db.Column(db.Text, nullable=False)
    extracted_entities = db.Column(db.Text)  # JSON of NLP-extracted entities
    conditions = db.Column(db.Text)  # JSON array of detected conditions
    medications = db.Column(db.Text)  # JSON array of medications
    symptoms = db.Column(db.Text)  # JSON array of symptoms
    sentiment_score = db.Column(db.Float)  # Overall health sentiment
    source_file = db.Column(db.String(255))
    note_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        def parse_json(field):
            if field:
                try:
                    return json.loads(field)
                except:
                    return field
            return None
        
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'note_type': self.note_type,
            'content': self.content,
            'extracted_entities': parse_json(self.extracted_entities),
            'conditions': parse_json(self.conditions),
            'medications': parse_json(self.medications),
            'symptoms': parse_json(self.symptoms),
            'sentiment_score': self.sentiment_score,
            'note_date': self.note_date.isoformat() if self.note_date else None
        }


class Prediction(db.Model):
    """ML model predictions and risk assessments."""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    prediction_type = db.Column(db.String(50), nullable=False)  # DIABETES_RISK, CVD_RISK, CANCER_RISK, etc.
    risk_score = db.Column(db.Float, nullable=False)  # 0-1 probability
    risk_level = db.Column(db.String(20))  # LOW, MODERATE, HIGH, CRITICAL
    confidence = db.Column(db.Float)  # Model confidence 0-1
    explanation = db.Column(db.Text)  # JSON of SHAP values and feature importances
    contributing_factors = db.Column(db.Text)  # JSON of top contributing factors
    recommendations = db.Column(db.Text)  # JSON array of recommendations
    modalities_used = db.Column(db.Text)  # JSON array of data sources used
    model_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        def parse_json(field):
            if field:
                try:
                    return json.loads(field)
                except:
                    return field
            return None
        
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'prediction_type': self.prediction_type,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'confidence': self.confidence,
            'explanation': parse_json(self.explanation),
            'contributing_factors': parse_json(self.contributing_factors),
            'recommendations': parse_json(self.recommendations),
            'modalities_used': parse_json(self.modalities_used),
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
