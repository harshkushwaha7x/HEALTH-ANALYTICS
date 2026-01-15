import {
    Activity, Heart, Droplets, TrendingUp, TrendingDown,
    AlertTriangle, Shield, Brain, Dna, FileText,
    Calendar, Clock, ChevronRight, Info
} from 'lucide-react'
import LabsPanel from './LabsPanel'
import TrendChart from './TrendChart'
import PredictionsPanel from './PredictionsPanel'
import GenomicsPanel from './GenomicsPanel'
import NotesPanel from './NotesPanel'
import ImagingPanel from './ImagingPanel'

function Dashboard({ data, loading }) {
    if (!data) return null

    const {
        patient,
        age,
        overall_risk,
        latest_labs,
        lab_trends,
        imaging,
        genomics,
        clinical_notes,
        predictions,
        recommendations
    } = data

    // Get risk level color
    const getRiskColor = (level) => {
        switch (level?.toUpperCase()) {
            case 'LOW': return 'var(--color-success)'
            case 'MODERATE': return 'var(--color-warning)'
            case 'HIGH': return 'var(--color-danger)'
            case 'CRITICAL': return 'var(--color-danger)'
            default: return 'var(--text-muted)'
        }
    }

    const getRiskBgColor = (level) => {
        switch (level?.toUpperCase()) {
            case 'LOW': return 'var(--color-success-bg)'
            case 'MODERATE': return 'var(--color-warning-bg)'
            case 'HIGH': return 'var(--color-danger-bg)'
            case 'CRITICAL': return 'rgba(239, 68, 68, 0.2)'
            default: return 'var(--bg-tertiary)'
        }
    }

    // Calculate risk percentage for display
    const riskPercent = Math.round((overall_risk?.score || 0) * 100)

    return (
        <div className="dashboard animate-fade-in">
            {/* Patient Header with Overall Risk */}
            <section className="patient-header">
                <div className="patient-overview">
                    <div className="patient-details">
                        <h2>{patient?.name}</h2>
                        <div className="patient-meta-row">
                            <span><Calendar size={14} /> {patient?.date_of_birth} ({age} years)</span>
                            <span>•</span>
                            <span>{patient?.gender}</span>
                            <span>•</span>
                            <span>Blood Type: {patient?.blood_type || 'Unknown'}</span>
                        </div>
                    </div>

                    <div className="overall-risk-card" style={{
                        background: getRiskBgColor(overall_risk?.level),
                        borderColor: getRiskColor(overall_risk?.level)
                    }}>
                        <div className="risk-score-ring">
                            <svg viewBox="0 0 36 36" className="risk-circle">
                                <path
                                    className="ring-bg"
                                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                    fill="none"
                                    stroke="rgba(255,255,255,0.1)"
                                    strokeWidth="3"
                                />
                                <path
                                    className="ring-fill"
                                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                    fill="none"
                                    stroke={getRiskColor(overall_risk?.level)}
                                    strokeWidth="3"
                                    strokeDasharray={`${riskPercent}, 100`}
                                    strokeLinecap="round"
                                />
                            </svg>
                            <span className="risk-value">{riskPercent}%</span>
                        </div>
                        <div className="risk-info">
                            <span className="risk-label">Overall Health Risk</span>
                            <span className="risk-level" style={{ color: getRiskColor(overall_risk?.level) }}>
                                {overall_risk?.level || 'Unknown'}
                            </span>
                            <span className="risk-confidence">
                                Confidence: {Math.round((overall_risk?.confidence || 0) * 100)}%
                            </span>
                        </div>
                    </div>
                </div>
            </section>

            {/* Key Vitals Summary */}
            <section className="vitals-summary">
                <div className="grid grid-4">
                    <VitalCard
                        icon={<Droplets />}
                        label="A1C"
                        value={latest_labs?.A1C?.value}
                        unit="%"
                        status={latest_labs?.A1C?.status}
                        reference="Normal: < 5.7%"
                    />
                    <VitalCard
                        icon={<Heart />}
                        label="Blood Pressure"
                        value={`${latest_labs?.BP_SYSTOLIC?.value || '--'}/${latest_labs?.BP_DIASTOLIC?.value || '--'}`}
                        unit="mmHg"
                        status={latest_labs?.BP_SYSTOLIC?.status}
                        reference="Normal: < 120/80"
                    />
                    <VitalCard
                        icon={<Activity />}
                        label="LDL Cholesterol"
                        value={latest_labs?.LDL?.value}
                        unit="mg/dL"
                        status={latest_labs?.LDL?.status}
                        reference="Optimal: < 100"
                    />
                    <VitalCard
                        icon={<Shield />}
                        label="HDL Cholesterol"
                        value={latest_labs?.HDL?.value}
                        unit="mg/dL"
                        status={latest_labs?.HDL?.status === 'LOW' ? 'HIGH' : 'NORMAL'}
                        reference="Optimal: > 60"
                    />
                </div>
            </section>

            {/* Charts Row */}
            <section className="charts-section">
                <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                    {lab_trends?.A1C && lab_trends.A1C.length > 1 && (
                        <TrendChart
                            title="A1C Trend"
                            data={lab_trends.A1C}
                            unit="%"
                            thresholds={{ warning: 5.7, danger: 6.5 }}
                            color="var(--color-primary)"
                        />
                    )}
                    {(lab_trends?.BP_SYSTOLIC || lab_trends?.LDL) && (
                        <TrendChart
                            title="Cardiovascular Indicators"
                            data={lab_trends.BP_SYSTOLIC || lab_trends.LDL || []}
                            unit={lab_trends.BP_SYSTOLIC ? 'mmHg' : 'mg/dL'}
                            thresholds={{ warning: lab_trends.BP_SYSTOLIC ? 120 : 100, danger: lab_trends.BP_SYSTOLIC ? 140 : 160 }}
                            color="var(--color-danger)"
                        />
                    )}
                </div>
            </section>

            {/* Detailed Panels */}
            <section className="panels-section">
                <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                    {/* Labs Panel */}
                    <LabsPanel labs={latest_labs} trends={lab_trends} />

                    {/* Predictions Panel */}
                    <PredictionsPanel predictions={predictions} />
                </div>
            </section>

            {/* Secondary Panels */}
            <section className="panels-section">
                <div className="grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
                    {/* Genomics Panel */}
                    <GenomicsPanel genomics={genomics} />

                    {/* Imaging Panel */}
                    <ImagingPanel imaging={imaging} />

                    {/* Clinical Notes Panel */}
                    <NotesPanel notes={clinical_notes} />
                </div>
            </section>

            {/* Recommendations */}
            {recommendations && recommendations.length > 0 && (
                <section className="recommendations-section">
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">
                                <Info size={18} />
                                AI Recommendations
                            </h3>
                        </div>
                        <div className="recommendations-list">
                            {recommendations.map((rec, idx) => (
                                <div key={idx} className="recommendation-item">
                                    <ChevronRight size={16} className="text-success" />
                                    <span>{rec}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            )}

            <style>{`
        .dashboard {
          display: flex;
          flex-direction: column;
          gap: var(--space-lg);
        }
        
        .patient-header {
          margin-bottom: var(--space-md);
        }
        
        .patient-overview {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: var(--space-xl);
        }
        
        .patient-details h2 {
          font-size: 1.75rem;
          margin-bottom: var(--space-sm);
        }
        
        .patient-meta-row {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          color: var(--text-secondary);
          font-size: 0.875rem;
        }
        
        .patient-meta-row svg {
          color: var(--text-muted);
        }
        
        .overall-risk-card {
          display: flex;
          align-items: center;
          gap: var(--space-lg);
          padding: var(--space-lg);
          border-radius: var(--radius-xl);
          border: 1px solid;
          min-width: 280px;
        }
        
        .risk-score-ring {
          position: relative;
          width: 80px;
          height: 80px;
        }
        
        .risk-circle {
          width: 100%;
          height: 100%;
          transform: rotate(-90deg);
        }
        
        .ring-fill {
          transition: stroke-dasharray 0.5s ease;
        }
        
        .risk-value {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        
        .risk-info {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        
        .risk-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .risk-level {
          font-size: 1.25rem;
          font-weight: 700;
          text-transform: uppercase;
        }
        
        .risk-confidence {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        
        .vitals-summary {
          margin-bottom: var(--space-md);
        }
        
        .charts-section,
        .panels-section {
          margin-bottom: var(--space-md);
        }
        
        .recommendations-list {
          display: flex;
          flex-direction: column;
          gap: var(--space-sm);
        }
        
        .recommendation-item {
          display: flex;
          align-items: flex-start;
          gap: var(--space-sm);
          padding: var(--space-sm) 0;
          color: var(--text-secondary);
          font-size: 0.9rem;
        }
        
        .recommendation-item svg {
          flex-shrink: 0;
          margin-top: 2px;
        }
        
        @media (max-width: 1200px) {
          .panels-section .grid {
            grid-template-columns: 1fr 1fr !important;
          }
        }
        
        @media (max-width: 768px) {
          .patient-overview {
            flex-direction: column;
          }
          
          .overall-risk-card {
            width: 100%;
          }
          
          .charts-section .grid,
          .panels-section .grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
        </div>
    )
}

// Vital Card Component
function VitalCard({ icon, label, value, unit, status, reference }) {
    const getStatusColor = (status) => {
        switch (status?.toUpperCase()) {
            case 'NORMAL': return 'var(--color-success)'
            case 'HIGH': return 'var(--color-danger)'
            case 'LOW': return 'var(--color-info)'
            default: return 'var(--text-muted)'
        }
    }

    return (
        <div className="vital-card card">
            <div className="vital-header">
                <div className="vital-icon" style={{ color: getStatusColor(status) }}>
                    {icon}
                </div>
                <span className={`status-badge ${status?.toLowerCase() || 'unknown'}`}>
                    {status || 'N/A'}
                </span>
            </div>
            <div className="vital-body">
                <span className="vital-value">
                    {value ?? '--'} <span className="vital-unit">{unit}</span>
                </span>
                <span className="vital-label">{label}</span>
            </div>
            <div className="vital-footer">
                <span className="vital-reference">{reference}</span>
            </div>

            <style>{`
        .vital-card {
          padding: var(--space-md);
        }
        
        .vital-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-md);
        }
        
        .vital-icon {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-md);
          background: var(--bg-tertiary);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .vital-body {
          margin-bottom: var(--space-sm);
        }
        
        .vital-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--text-primary);
          display: block;
        }
        
        .vital-unit {
          font-size: 0.875rem;
          font-weight: 400;
          color: var(--text-muted);
        }
        
        .vital-label {
          font-size: 0.8rem;
          color: var(--text-secondary);
        }
        
        .vital-footer {
          padding-top: var(--space-sm);
          border-top: 1px solid var(--border-color);
        }
        
        .vital-reference {
          font-size: 0.7rem;
          color: var(--text-muted);
        }
      `}</style>
        </div>
    )
}

export default Dashboard
