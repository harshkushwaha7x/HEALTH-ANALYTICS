"""
Health Analytics Flask Application
Main API server providing endpoints for patient management, file uploads,
predictions, and dashboard data.
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from models import db, Patient, LabResult, ImagingStudy, GenomicsData, ClinicalNote, Prediction
from parsers import parse_health_file, detect_file_type
from ml_models import get_prediction_models, MultiModalFusionModel
from data_generator import generate_complete_patient_dataset

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "health_analytics.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)

# Initialize database
db.init_app(app)

# Initialize ML models
models = get_prediction_models()
fusion_model = MultiModalFusionModel()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'csv', 'xlsx', 'xls', 'vcf', 'txt', 'jpg', 'jpeg', 'png', 'dcm'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============= Root Route =============

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API welcome message."""
    return jsonify({
        'name': 'Health Analytics API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'patients': '/api/patients',
            'dashboard': '/api/patients/<id>/dashboard',
            'predict': '/api/patients/<id>/predict',
            'upload': '/api/patients/<id>/upload'
        },
        'frontend': 'http://localhost:3000',
        'message': 'Welcome to Health Analytics API. Access the dashboard at http://localhost:3000'
    })


# ============= Health Check =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


# ============= Patient Endpoints =============

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients."""
    patients = Patient.query.all()
    return jsonify({
        'patients': [p.to_dict() for p in patients],
        'count': len(patients)
    })


@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient by ID."""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify(patient.to_dict())


@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Create a new patient."""
    data = request.json
    
    patient = Patient(
        name=data.get('name'),
        date_of_birth=datetime.fromisoformat(data.get('date_of_birth')),
        gender=data.get('gender'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        blood_type=data.get('blood_type'),
        emergency_contact=data.get('emergency_contact')
    )
    
    db.session.add(patient)
    db.session.commit()
    
    return jsonify(patient.to_dict()), 201


@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update a patient."""
    patient = Patient.query.get_or_404(patient_id)
    data = request.json
    
    if 'name' in data:
        patient.name = data['name']
    if 'email' in data:
        patient.email = data['email']
    if 'phone' in data:
        patient.phone = data['phone']
    if 'address' in data:
        patient.address = data['address']
    
    db.session.commit()
    return jsonify(patient.to_dict())


@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient and all associated data."""
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'})


# ============= File Upload =============

@app.route('/api/upload/<int:patient_id>', methods=['POST'])
def upload_file(patient_id):
    """Upload and process a health data file for a patient."""
    patient = Patient.query.get_or_404(patient_id)
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed: {ALLOWED_EXTENSIONS}'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f'{patient_id}_{timestamp}_{filename}'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    
    # Parse file
    try:
        parsed_data = parse_health_file(file_path, app.config['UPLOAD_FOLDER'])
        
        # Store extracted data
        records_created = {'labs': 0, 'genomics': 0, 'notes': 0, 'imaging': 0}
        
        # Store lab results
        for lab in parsed_data.get('lab_results', []):
            lab_result = LabResult(
                patient_id=patient_id,
                lab_type=lab['lab_type'],
                value=lab['value'],
                unit=lab.get('unit'),
                reference_low=lab.get('reference_low'),
                reference_high=lab.get('reference_high'),
                status=lab.get('status'),
                source_file=filename,
                recorded_at=datetime.fromisoformat(lab['recorded_at']) if lab.get('recorded_at') else datetime.utcnow()
            )
            db.session.add(lab_result)
            records_created['labs'] += 1
        
        # Store genomics data
        for variant in parsed_data.get('genomics_data', []):
            genomics = GenomicsData(
                patient_id=patient_id,
                gene=variant['gene'],
                variant=variant['variant'],
                chromosome=variant.get('chromosome'),
                position=variant.get('position'),
                reference_allele=variant.get('reference_allele'),
                alternate_allele=variant.get('alternate_allele'),
                classification=variant.get('classification'),
                pathogenicity_score=variant.get('pathogenicity_score'),
                associated_conditions=json.dumps(variant.get('associated_conditions', [])),
                source_file=filename
            )
            db.session.add(genomics)
            records_created['genomics'] += 1
        
        # Store clinical notes
        if parsed_data.get('clinical_notes'):
            note_data = parsed_data['clinical_notes']
            note = ClinicalNote(
                patient_id=patient_id,
                note_type='UPLOADED',
                content=parsed_data.get('raw_text', '')[:5000],
                extracted_entities=json.dumps(note_data.get('extracted_entities', {})),
                conditions=json.dumps(note_data.get('conditions', [])),
                medications=json.dumps(note_data.get('medications', [])),
                symptoms=json.dumps(note_data.get('symptoms', [])),
                sentiment_score=note_data.get('sentiment_score', 0),
                source_file=filename
            )
            db.session.add(note)
            records_created['notes'] += 1
        
        # Store imaging data
        if parsed_data.get('imaging_data'):
            img_data = parsed_data['imaging_data']
            imaging = ImagingStudy(
                patient_id=patient_id,
                modality=img_data['modality'],
                body_part=img_data['body_part'],
                file_path=file_path,
                thumbnail_path=img_data.get('thumbnail_path'),
                findings=json.dumps(img_data.get('findings', [])),
                abnormality_score=img_data.get('abnormality_score')
            )
            db.session.add(imaging)
            records_created['imaging'] += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'File processed successfully',
            'file_type': parsed_data['file_type'],
            'records_created': records_created,
            'errors': parsed_data.get('errors', [])
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= Lab Results =============

@app.route('/api/patients/<int:patient_id>/labs', methods=['GET'])
def get_patient_labs(patient_id):
    """Get all lab results for a patient."""
    Patient.query.get_or_404(patient_id)
    labs = LabResult.query.filter_by(patient_id=patient_id).order_by(LabResult.recorded_at.desc()).all()
    return jsonify({
        'labs': [l.to_dict() for l in labs],
        'count': len(labs)
    })


@app.route('/api/patients/<int:patient_id>/labs/trends', methods=['GET'])
def get_lab_trends(patient_id):
    """Get lab value trends for charting."""
    Patient.query.get_or_404(patient_id)
    
    # Get lab type from query param, default to all
    lab_type = request.args.get('type', None)
    
    query = LabResult.query.filter_by(patient_id=patient_id)
    if lab_type:
        query = query.filter_by(lab_type=lab_type)
    
    labs = query.order_by(LabResult.recorded_at.asc()).all()
    
    # Group by lab type
    trends = {}
    for lab in labs:
        if lab.lab_type not in trends:
            trends[lab.lab_type] = {
                'lab_type': lab.lab_type,
                'unit': lab.unit,
                'reference_low': lab.reference_low,
                'reference_high': lab.reference_high,
                'data': []
            }
        trends[lab.lab_type]['data'].append({
            'value': lab.value,
            'date': lab.recorded_at.isoformat() if lab.recorded_at else None,
            'status': lab.status
        })
    
    return jsonify({'trends': list(trends.values())})


# ============= Predictions =============

@app.route('/api/patients/<int:patient_id>/predict', methods=['POST'])
def run_predictions(patient_id):
    """Run ML predictions for a patient."""
    patient = Patient.query.get_or_404(patient_id)
    
    # Gather all patient data
    labs = LabResult.query.filter_by(patient_id=patient_id).order_by(LabResult.recorded_at.asc()).all()
    imaging = ImagingStudy.query.filter_by(patient_id=patient_id).order_by(ImagingStudy.study_date.desc()).all()
    genomics = GenomicsData.query.filter_by(patient_id=patient_id).all()
    notes = ClinicalNote.query.filter_by(patient_id=patient_id).order_by(ClinicalNote.note_date.desc()).all()
    
    # Prepare data for fusion model
    patient_data = {
        'labs': [l.to_dict() for l in labs],
        'imaging': [i.to_dict() for i in imaging],
        'genomics': [g.to_dict() for g in genomics],
        'clinical_notes': [n.to_dict() for n in notes],
        'age': calculate_age(patient.date_of_birth) if patient.date_of_birth else 50,
        'gender': patient.gender
    }
    
    # Run fusion model
    try:
        prediction_result = fusion_model.predict(patient_data)
        
        # Store predictions
        # Clear old predictions
        Prediction.query.filter_by(patient_id=patient_id).delete()
        
        # Store overall prediction
        overall_pred = Prediction(
            patient_id=patient_id,
            prediction_type='OVERALL_HEALTH',
            risk_score=prediction_result['overall_risk_score'],
            risk_level=prediction_result['overall_risk_level'],
            confidence=prediction_result['confidence'],
            explanation=json.dumps(prediction_result.get('contributing_factors', [])),
            contributing_factors=json.dumps(prediction_result.get('contributing_factors', [])),
            recommendations=json.dumps(prediction_result.get('recommendations', [])),
            modalities_used=json.dumps(prediction_result.get('modalities_used', [])),
            model_version=prediction_result.get('model_version', '1.0.0')
        )
        db.session.add(overall_pred)
        
        # Store domain-specific predictions
        for domain, domain_pred in prediction_result.get('domain_predictions', {}).items():
            pred = Prediction(
                patient_id=patient_id,
                prediction_type=domain_pred.get('prediction_type', domain.upper()),
                risk_score=domain_pred.get('risk_score', 0),
                risk_level=domain_pred.get('risk_level', 'LOW'),
                confidence=domain_pred.get('confidence', 0.5),
                explanation=json.dumps(domain_pred),
                contributing_factors=json.dumps(domain_pred.get('contributing_factors', [])),
                recommendations=json.dumps(domain_pred.get('recommendations', [])),
                modalities_used=json.dumps(domain_pred.get('modalities_used', [])),
                model_version=domain_pred.get('model_version', '1.0.0')
            )
            db.session.add(pred)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Predictions generated successfully',
            'result': prediction_result
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/patients/<int:patient_id>/predictions', methods=['GET'])
def get_predictions(patient_id):
    """Get all predictions for a patient."""
    Patient.query.get_or_404(patient_id)
    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(Prediction.created_at.desc()).all()
    return jsonify({
        'predictions': [p.to_dict() for p in predictions],
        'count': len(predictions)
    })


@app.route('/api/patients/<int:patient_id>/anomalies', methods=['GET'])
def detect_anomalies(patient_id):
    """Detect anomalies and analyze trends in patient lab values."""
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        # Get all labs for this patient
        labs = LabResult.query.filter_by(patient_id=patient_id).order_by(LabResult.recorded_at).all()
        
        if not labs:
            return jsonify({
                'anomalies': [],
                'trends': {},
                'alerts': [],
                'message': 'No lab data available for analysis'
            })
        
        # Convert to dict format for anomaly detector
        lab_data = [l.to_dict() for l in labs]
        patient_info = {'gender': patient.gender, 'age': calculate_age(patient.date_of_birth) if patient.date_of_birth else None}
        
        # Run anomaly detection
        anomaly_detector = models['anomaly_detector']
        result = anomaly_detector.detect_anomalies(lab_data, patient_info)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= Dashboard =============

@app.route('/api/patients/<int:patient_id>/dashboard', methods=['GET'])
def get_dashboard(patient_id):
    """Get complete dashboard data for a patient."""
    patient = Patient.query.get_or_404(patient_id)
    
    # Get all data
    labs = LabResult.query.filter_by(patient_id=patient_id).order_by(LabResult.recorded_at.desc()).all()
    imaging = ImagingStudy.query.filter_by(patient_id=patient_id).order_by(ImagingStudy.study_date.desc()).all()
    genomics = GenomicsData.query.filter_by(patient_id=patient_id).all()
    notes = ClinicalNote.query.filter_by(patient_id=patient_id).order_by(ClinicalNote.note_date.desc()).all()
    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(Prediction.created_at.desc()).all()
    
    # Get overall prediction
    overall_pred = next((p for p in predictions if p.prediction_type == 'OVERALL_HEALTH'), None)
    
    # Group labs by type for latest values
    latest_labs = {}
    for lab in labs:
        if lab.lab_type not in latest_labs:
            latest_labs[lab.lab_type] = lab.to_dict()
    
    # Build lab trends for charts
    lab_trends = {}
    for lab in sorted(labs, key=lambda x: x.recorded_at or datetime.min):
        if lab.lab_type not in lab_trends:
            lab_trends[lab.lab_type] = []
        lab_trends[lab.lab_type].append({
            'value': lab.value,
            'date': lab.recorded_at.isoformat() if lab.recorded_at else None
        })
    
    # Build dashboard response
    dashboard = {
        'patient': patient.to_dict(),
        'age': calculate_age(patient.date_of_birth) if patient.date_of_birth else None,
        'overall_risk': {
            'score': overall_pred.risk_score if overall_pred else 0.1,
            'level': overall_pred.risk_level if overall_pred else 'LOW',
            'confidence': overall_pred.confidence if overall_pred else 0.5
        },
        'latest_labs': latest_labs,
        'lab_trends': lab_trends,
        'imaging': [i.to_dict() for i in imaging[:5]],  # Last 5 studies
        'genomics': {
            'variants': [g.to_dict() for g in genomics],
            'high_risk_count': len([g for g in genomics if g.classification == 'PATHOGENIC'])
        },
        'clinical_notes': [n.to_dict() for n in notes[:3]],  # Latest 3 notes
        'predictions': [p.to_dict() for p in predictions],
        'recommendations': json.loads(overall_pred.recommendations) if overall_pred and overall_pred.recommendations else [],
        'last_updated': datetime.utcnow().isoformat()
    }
    
    return jsonify(dashboard)


# ============= Data Initialization =============

@app.route('/api/init-sample-data', methods=['POST'])
def init_sample_data():
    """Initialize database with sample data."""
    try:
        # Generate synthetic data
        dataset = generate_complete_patient_dataset(num_patients=5, seed=42)
        
        # Clear existing data
        Prediction.query.delete()
        ClinicalNote.query.delete()
        GenomicsData.query.delete()
        ImagingStudy.query.delete()
        LabResult.query.delete()
        Patient.query.delete()
        
        # Insert patients
        for p_data in dataset['patients']:
            patient = Patient(
                name=p_data['name'],
                date_of_birth=datetime.fromisoformat(p_data['date_of_birth']),
                gender=p_data['gender'],
                email=p_data['email'],
                phone=p_data['phone'],
                address=p_data['address'],
                blood_type=p_data['blood_type'],
                emergency_contact=p_data['emergency_contact']
            )
            db.session.add(patient)
        
        db.session.flush()  # Get patient IDs
        
        # Insert lab results
        for lab in dataset['lab_results']:
            lab_result = LabResult(
                patient_id=lab['patient_id'],
                lab_type=lab['lab_type'],
                value=lab['value'],
                unit=lab['unit'],
                reference_low=lab['reference_low'],
                reference_high=lab['reference_high'],
                status=lab['status'],
                recorded_at=datetime.fromisoformat(lab['recorded_at'])
            )
            db.session.add(lab_result)
        
        # Insert genomics
        for variant in dataset['genomics_data']:
            genomics = GenomicsData(
                patient_id=variant['patient_id'],
                gene=variant['gene'],
                variant=variant['variant'],
                chromosome=variant['chromosome'],
                position=variant['position'],
                classification=variant['classification'],
                pathogenicity_score=variant['pathogenicity_score'],
                associated_conditions=json.dumps(variant['associated_conditions'])
            )
            db.session.add(genomics)
        
        # Insert clinical notes
        for note in dataset['clinical_notes']:
            clinical_note = ClinicalNote(
                patient_id=note['patient_id'],
                note_type=note['note_type'],
                content=note['content'],
                conditions=json.dumps(note['conditions']),
                medications=json.dumps(note['medications']),
                symptoms=json.dumps(note['symptoms']),
                note_date=datetime.fromisoformat(note['note_date'])
            )
            db.session.add(clinical_note)
        
        # Insert imaging
        for img in dataset['imaging_studies']:
            imaging = ImagingStudy(
                patient_id=img['patient_id'],
                modality=img['modality'],
                body_part=img['body_part'],
                findings=json.dumps([img['findings']]),
                abnormality_score=img['abnormality_score'],
                study_date=datetime.fromisoformat(img['study_date'])
            )
            db.session.add(imaging)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Sample data initialized successfully',
            'patients': len(dataset['patients']),
            'lab_results': len(dataset['lab_results']),
            'genomics': len(dataset['genomics_data']),
            'notes': len(dataset['clinical_notes']),
            'imaging': len(dataset['imaging_studies'])
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= Utilities =============

def calculate_age(birth_date):
    """Calculate age from birth date."""
    if not birth_date:
        return None
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


# ============= Export & Share Endpoints =============

@app.route('/api/patients/<int:patient_id>/export', methods=['GET'])
def export_patient_report(patient_id):
    """Export patient health report in various formats."""
    patient = Patient.query.get_or_404(patient_id)
    format_type = request.args.get('format', 'json').lower()
    
    # Gather all patient data
    labs = LabResult.query.filter_by(patient_id=patient_id).order_by(LabResult.recorded_at.desc()).all()
    imaging = ImagingStudy.query.filter_by(patient_id=patient_id).all()
    genomics = GenomicsData.query.filter_by(patient_id=patient_id).all()
    notes = ClinicalNote.query.filter_by(patient_id=patient_id).all()
    predictions = Prediction.query.filter_by(patient_id=patient_id).all()
    
    # Get overall prediction
    overall_pred = next((p for p in predictions if p.prediction_type == 'OVERALL_HEALTH'), None)
    
    # Build report data
    report_data = {
        'report_type': 'Health Analytics Export',
        'generated_at': datetime.utcnow().isoformat(),
        'patient': {
            'name': patient.name,
            'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            'gender': patient.gender,
            'blood_type': patient.blood_type,
            'age': calculate_age(patient.date_of_birth)
        },
        'overall_risk': {
            'score': round(overall_pred.risk_score * 100, 1) if overall_pred else 0,
            'level': overall_pred.risk_level if overall_pred else 'LOW',
            'confidence': round(overall_pred.confidence * 100, 1) if overall_pred else 50
        },
        'lab_results': [
            {
                'test': lab.lab_type,
                'value': lab.value,
                'unit': lab.unit,
                'reference_range': f"{lab.reference_low} - {lab.reference_high}" if lab.reference_low else None,
                'status': lab.status,
                'date': lab.recorded_at.isoformat() if lab.recorded_at else None
            } for lab in labs[:20]  # Latest 20
        ],
        'predictions': [
            {
                'type': pred.prediction_type,
                'risk_score': round(pred.risk_score * 100, 1),
                'risk_level': pred.risk_level
            } for pred in predictions
        ],
        'imaging_studies': [
            {
                'modality': img.modality,
                'body_part': img.body_part,
                'date': img.study_date.isoformat() if img.study_date else None
            } for img in imaging
        ],
        'genomics_summary': {
            'total_variants': len(genomics),
            'pathogenic_count': len([g for g in genomics if g.classification == 'PATHOGENIC'])
        },
        'disclaimer': 'This report is for informational purposes only and should not be considered medical advice. Please consult with a healthcare professional for proper medical guidance.'
    }
    
    if format_type == 'json':
        return jsonify(report_data)
    
    elif format_type == 'csv':
        # Return lab results as CSV
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Test', 'Value', 'Unit', 'Reference Range', 'Status', 'Date'])
        
        for lab in report_data['lab_results']:
            writer.writerow([
                lab['test'],
                lab['value'],
                lab['unit'],
                lab['reference_range'],
                lab['status'],
                lab['date']
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=health_report_{patient_id}.csv'}
        )
    
    elif format_type == 'text':
        # Return formatted text report
        text_report = f"""
================================================================================
                        HEALTH ANALYTICS REPORT
================================================================================

PATIENT INFORMATION
-------------------
Name: {report_data['patient']['name']}
Date of Birth: {report_data['patient']['date_of_birth']}
Gender: {report_data['patient']['gender']}
Blood Type: {report_data['patient']['blood_type']}
Age: {report_data['patient']['age']} years
Generated: {report_data['generated_at']}

OVERALL HEALTH RISK
-------------------
Risk Score: {report_data['overall_risk']['score']}%
Risk Level: {report_data['overall_risk']['level']}
Confidence: {report_data['overall_risk']['confidence']}%

LABORATORY RESULTS
------------------
"""
        for lab in report_data['lab_results'][:10]:
            text_report += f"  {lab['test']}: {lab['value']} {lab['unit'] or ''} ({lab['status']})\n"
        
        text_report += f"""
AI PREDICTIONS
--------------
"""
        for pred in report_data['predictions']:
            text_report += f"  {pred['type']}: {pred['risk_score']}% ({pred['risk_level']})\n"
        
        text_report += f"""
GENOMICS SUMMARY
----------------
Total Variants Analyzed: {report_data['genomics_summary']['total_variants']}
Pathogenic Variants: {report_data['genomics_summary']['pathogenic_count']}

DISCLAIMER
----------
{report_data['disclaimer']}

================================================================================
"""
        from flask import Response
        return Response(
            text_report,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment;filename=health_report_{patient_id}.txt'}
        )
    
    else:
        return jsonify({'error': f'Unsupported format: {format_type}. Use json, csv, or text.'}), 400


@app.route('/api/patients/<int:patient_id>/share', methods=['POST'])
def share_patient_report(patient_id):
    """Share patient report via email or generate shareable link."""
    patient = Patient.query.get_or_404(patient_id)
    data = request.json or {}
    
    share_method = data.get('method', 'link')  # 'email' or 'link'
    recipient_email = data.get('email')
    
    if share_method == 'email':
        if not recipient_email:
            return jsonify({'error': 'Email address is required'}), 400
        
        # Get SMTP configuration from environment
        smtp_host = os.environ.get('SMTP_HOST', '')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER', '')
        smtp_pass = os.environ.get('SMTP_PASS', '')
        sender_email = os.environ.get('SMTP_FROM', smtp_user)
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            # No SMTP configured - provide instructions
            return jsonify({
                'success': False,
                'simulated': True,
                'message': 'Email not configured. Set SMTP environment variables.',
                'instructions': {
                    'step1': 'Set SMTP_HOST (e.g., smtp.gmail.com)',
                    'step2': 'Set SMTP_PORT (e.g., 587)',
                    'step3': 'Set SMTP_USER (your email)',
                    'step4': 'Set SMTP_PASS (your app password - NOT regular password)',
                    'step5': 'Set SMTP_FROM (optional, sender email)',
                    'gmail_note': 'For Gmail: Enable 2FA, then create App Password at https://myaccount.google.com/apppasswords'
                }
            }), 200
        
        # Build report content
        predictions = Prediction.query.filter_by(patient_id=patient_id).all()
        overall_pred = next((p for p in predictions if p.prediction_type == 'OVERALL_HEALTH'), None)
        
        email_body = f"""
Health Analytics Report - {patient.name}
========================================

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Patient Information:
- Name: {patient.name}
- Date of Birth: {patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else 'N/A'}
- Gender: {patient.gender or 'N/A'}
- Blood Type: {patient.blood_type or 'N/A'}

Overall Health Risk:
- Risk Score: {overall_pred.risk_score * 100:.1f}% if overall_pred else 'Not calculated'
- Risk Level: {overall_pred.risk_level if overall_pred else 'Unknown'}

This report was automatically generated by Health Analytics.
Please consult with a healthcare professional for medical advice.

---
View full details at: {request.host_url}
"""
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f'Health Analytics Report - {patient.name}'
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            return jsonify({
                'success': True,
                'message': f'Report sent to {recipient_email}',
                'simulated': False
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': f'Failed to send email: {str(e)}',
                'troubleshooting': {
                    'gmail': 'Use App Password (not regular password). Enable at https://myaccount.google.com/apppasswords',
                    'outlook': 'May need to enable "Less secure apps" or use App Password',
                    'other': 'Check SMTP settings and credentials'
                }
            }), 500
    
    elif share_method == 'link':
        # Generate a unique shareable link
        import hashlib
        import time
        
        # Create a token based on patient ID and timestamp
        token_data = f"{patient_id}:{int(time.time())}:{patient.name}"
        share_token = hashlib.sha256(token_data.encode()).hexdigest()[:16]
        
        # In production, store this token in database with expiry
        share_url = f"/shared/report/{share_token}"
        
        return jsonify({
            'success': True,
            'share_url': share_url,
            'token': share_token,
            'expires_in': '24 hours',
            'note': 'Full share link implementation requires token storage and validation'
        })
    
    else:
        return jsonify({'error': f'Unsupported share method: {share_method}. Use email or link.'}), 400


@app.route('/api/patients/<int:patient_id>/export/pdf', methods=['GET'])
def export_patient_pdf(patient_id):
    """Export patient report as PDF (requires reportlab or weasyprint)."""
    # Check if PDF libraries are available
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        import io
        
        patient = Patient.query.get_or_404(patient_id)
        predictions = Prediction.query.filter_by(patient_id=patient_id).all()
        overall_pred = next((p for p in predictions if p.prediction_type == 'OVERALL_HEALTH'), None)
        
        # Create PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "Health Analytics Report")
        
        # Patient info
        p.setFont("Helvetica", 12)
        y = height - 100
        p.drawString(50, y, f"Patient: {patient.name}")
        y -= 20
        p.drawString(50, y, f"Date of Birth: {patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else 'N/A'}")
        y -= 20
        p.drawString(50, y, f"Gender: {patient.gender or 'N/A'}")
        y -= 20
        p.drawString(50, y, f"Blood Type: {patient.blood_type or 'N/A'}")
        
        # Risk score
        y -= 40
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Overall Health Risk")
        y -= 25
        p.setFont("Helvetica", 12)
        if overall_pred:
            p.drawString(50, y, f"Risk Score: {overall_pred.risk_score * 100:.1f}%")
            y -= 20
            p.drawString(50, y, f"Risk Level: {overall_pred.risk_level}")
        else:
            p.drawString(50, y, "No predictions available. Run AI Analysis first.")
        
        # Disclaimer
        y -= 60
        p.setFont("Helvetica-Oblique", 9)
        p.drawString(50, y, "Disclaimer: This report is for informational purposes only.")
        y -= 15
        p.drawString(50, y, "Please consult with a healthcare professional for medical advice.")
        
        # Generated date
        y -= 30
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        
        from flask import Response
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment;filename=health_report_{patient_id}.pdf'}
        )
        
    except ImportError:
        return jsonify({
            'error': 'PDF generation requires reportlab library',
            'install': 'pip install reportlab',
            'alternative': 'Use /api/patients/<id>/export?format=text for text export'
        }), 501


# ============= Static Files (for production) =============

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve static files from frontend build."""
    static_folder = os.path.join(BASE_DIR, '..', 'frontend', 'dist')
    if path and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')


# ============= Main =============

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created.")
    
    print("Starting Health Analytics API Server...")
    print("API available at http://localhost:5000/api")
    app.run(debug=True, host='0.0.0.0', port=5000)
