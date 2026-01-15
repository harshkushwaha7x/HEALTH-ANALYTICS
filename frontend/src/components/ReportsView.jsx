import { useState } from 'react'
import { FileText, Download, AlertTriangle, CheckCircle, Clock } from 'lucide-react'

function ReportsView({ dashboardData }) {
    const [generatingReport, setGeneratingReport] = useState(false)

    if (!dashboardData) {
        return (
            <div className="reports-view empty">
                <p>Select a patient to generate reports</p>
            </div>
        )
    }

    const { patient, predictions, latest_labs, genomics, imaging, clinical_notes, overall_risk } = dashboardData

    const exportReport = async () => {
        setGeneratingReport(true)
        try {
            const response = await fetch(`http://localhost:5000/api/patients/${patient.id}/export?format=text`)
            const blob = await response.blob()
            downloadBlob(blob, `health_report_${patient.id}.txt`)
        } catch (error) {
            console.error('Export failed:', error)
            generateLocalReport()
        }
        setGeneratingReport(false)
    }

    const downloadBlob = (blob, filename) => {
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        a.click()
        URL.revokeObjectURL(url)
    }

    const generateLocalReport = () => {
        const reportContent = `
            HEALTH ANALYTICS REPORT
            ========================
            
            Patient: ${patient?.name || 'Unknown'}
            Date of Birth: ${patient?.date_of_birth || 'Unknown'}
            Blood Type: ${patient?.blood_type || 'Unknown'}
            Generated: ${new Date().toLocaleString()}
            
            OVERALL HEALTH RISK
            -------------------
            Risk Score: ${(overall_risk?.score * 100).toFixed(0)}%
            Risk Level: ${overall_risk?.level || 'Unknown'}
            Confidence: ${(overall_risk?.confidence * 100).toFixed(0)}%
            
            LABORATORY RESULTS
            ------------------
            ${Object.entries(latest_labs || {}).map(([key, lab]) =>
            `${key}: ${lab.value} ${lab.unit} (${lab.status})`
        ).join('\n            ')}
            
            AI PREDICTIONS
            --------------
            ${(predictions || []).map(p =>
            `${p.prediction_type}: ${p.risk_level} (${(p.risk_score * 100).toFixed(0)}% risk)`
        ).join('\n            ')}
            
            DISCLAIMER
            ----------
            This report is for informational purposes only and should not be 
            considered medical advice. Please consult with a healthcare professional
            for proper medical guidance.
        `

        const blob = new Blob([reportContent], { type: 'text/plain' })
        downloadBlob(blob, `health_report_${patient?.name?.replace(/\s/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`)
    }

    const getRiskColor = (level) => {
        switch (level?.toUpperCase()) {
            case 'LOW': return 'var(--color-success)'
            case 'MODERATE': return 'var(--color-warning)'
            case 'HIGH': return 'var(--color-error)'
            case 'CRITICAL': return 'var(--color-error)'
            default: return 'var(--text-muted)'
        }
    }

    return (
        <div className="reports-view">
            <div className="reports-header">
                <div>
                    <h2>Reports & Summary</h2>
                    <p className="subtitle">Generate comprehensive health reports</p>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={exportReport}
                    disabled={generatingReport}
                >
                    {generatingReport ? (
                        <>
                            <Clock size={18} className="spin" />
                            Exporting...
                        </>
                    ) : (
                        <>
                            <Download size={18} />
                            Export Report
                        </>
                    )}
                </button>
            </div>

            <div className="report-summary">
                <div className="summary-card main">
                    <div className="summary-header">
                        <FileText size={24} />
                        <h3>Patient Summary</h3>
                    </div>
                    <div className="summary-content">
                        <div className="patient-info">
                            <div className="info-row">
                                <span className="label">Name:</span>
                                <span className="value">{patient?.name}</span>
                            </div>
                            <div className="info-row">
                                <span className="label">Date of Birth:</span>
                                <span className="value">{patient?.date_of_birth?.split('T')[0]}</span>
                            </div>
                            <div className="info-row">
                                <span className="label">Gender:</span>
                                <span className="value">{patient?.gender}</span>
                            </div>
                            <div className="info-row">
                                <span className="label">Blood Type:</span>
                                <span className="value">{patient?.blood_type}</span>
                            </div>
                        </div>
                        <div className="risk-summary">
                            <div className="risk-circle" style={{ borderColor: getRiskColor(overall_risk?.level) }}>
                                <span className="risk-score">{((overall_risk?.score || 0) * 100).toFixed(0)}%</span>
                                <span className="risk-label">Risk</span>
                            </div>
                            <span className="risk-level" style={{ color: getRiskColor(overall_risk?.level) }}>
                                {overall_risk?.level || 'Unknown'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="report-sections">
                <div className="report-section">
                    <h3>
                        <CheckCircle size={18} />
                        Latest Lab Results
                    </h3>
                    <table className="report-table">
                        <thead>
                            <tr>
                                <th>Test</th>
                                <th>Value</th>
                                <th>Reference</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(latest_labs || {}).map(([key, lab]) => (
                                <tr key={key}>
                                    <td>{key.replace(/_/g, ' ')}</td>
                                    <td>{lab.value} {lab.unit}</td>
                                    <td>{lab.reference_low} - {lab.reference_high}</td>
                                    <td>
                                        <span className={`status-badge ${lab.status?.toLowerCase()}`}>
                                            {lab.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="report-section">
                    <h3>
                        <AlertTriangle size={18} />
                        AI Risk Predictions
                    </h3>
                    <div className="predictions-list">
                        {(predictions || []).filter(p => p.prediction_type !== 'OVERALL_HEALTH').map((pred, idx) => (
                            <div key={idx} className="prediction-row">
                                <span className="pred-type">{pred.prediction_type?.replace(/_/g, ' ')}</span>
                                <div className="pred-bar">
                                    <div
                                        className="pred-fill"
                                        style={{
                                            width: `${(pred.risk_score || 0) * 100}%`,
                                            background: getRiskColor(pred.risk_level)
                                        }}
                                    />
                                </div>
                                <span className="pred-score">{((pred.risk_score || 0) * 100).toFixed(0)}%</span>
                                <span className="pred-level" style={{ color: getRiskColor(pred.risk_level) }}>
                                    {pred.risk_level}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {genomics?.variants?.length > 0 && (
                    <div className="report-section">
                        <h3>Genomics Summary</h3>
                        <p>{genomics.variants.length} variants analyzed, {genomics.high_risk_count} pathogenic</p>
                    </div>
                )}

                {imaging?.length > 0 && (
                    <div className="report-section">
                        <h3>Imaging Studies</h3>
                        <p>{imaging.length} studies on record</p>
                    </div>
                )}
            </div>

            <div className="disclaimer">
                <AlertTriangle size={18} />
                <p>
                    <strong>Disclaimer:</strong> This report is generated by an AI-powered system for informational
                    purposes only. It is not intended as medical advice and should not be used for diagnosing or
                    treating health conditions. Always consult with qualified healthcare professionals.
                </p>
            </div>

            <style>{`
                .reports-view {
                    padding: var(--space-xl);
                }
                
                .reports-view.empty {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 400px;
                    color: var(--text-muted);
                }
                
                .reports-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--space-xl);
                }
                
                .reports-header h2 {
                    font-size: 1.5rem;
                    margin-bottom: var(--space-xs);
                }
                
                .subtitle {
                    color: var(--text-muted);
                }
                
                .summary-card {
                    background: var(--bg-card);
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-lg);
                    padding: var(--space-xl);
                    margin-bottom: var(--space-xl);
                }
                
                .summary-header {
                    display: flex;
                    align-items: center;
                    gap: var(--space-md);
                    margin-bottom: var(--space-lg);
                    color: var(--color-primary);
                }
                
                .summary-header h3 {
                    margin: 0;
                }
                
                .summary-content {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .info-row {
                    display: flex;
                    gap: var(--space-md);
                    margin-bottom: var(--space-sm);
                }
                
                .info-row .label {
                    color: var(--text-muted);
                    min-width: 120px;
                }
                
                .info-row .value {
                    font-weight: 500;
                }
                
                .risk-summary {
                    text-align: center;
                }
                
                .risk-circle {
                    width: 100px;
                    height: 100px;
                    border-radius: 50%;
                    border: 4px solid;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: var(--space-sm);
                }
                
                .risk-score {
                    font-size: 1.5rem;
                    font-weight: 700;
                }
                
                .risk-label {
                    font-size: 0.75rem;
                    color: var(--text-muted);
                }
                
                .risk-level {
                    font-weight: 700;
                    font-size: 1rem;
                }
                
                .report-sections {
                    display: grid;
                    gap: var(--space-lg);
                    margin-bottom: var(--space-xl);
                }
                
                .report-section {
                    background: var(--bg-card);
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                }
                
                .report-section h3 {
                    display: flex;
                    align-items: center;
                    gap: var(--space-sm);
                    margin-bottom: var(--space-md);
                    color: var(--color-primary);
                }
                
                .report-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                
                .report-table th,
                .report-table td {
                    padding: var(--space-sm) var(--space-md);
                    text-align: left;
                    border-bottom: 1px solid var(--border-color);
                }
                
                .report-table th {
                    color: var(--text-muted);
                    font-weight: 500;
                    font-size: 0.75rem;
                    text-transform: uppercase;
                }
                
                .status-badge {
                    padding: 2px 8px;
                    border-radius: var(--radius-sm);
                    font-size: 0.75rem;
                    font-weight: 500;
                }
                
                .status-badge.normal {
                    background: rgba(16, 185, 129, 0.2);
                    color: var(--color-success);
                }
                
                .status-badge.high {
                    background: rgba(239, 68, 68, 0.2);
                    color: var(--color-error);
                }
                
                .status-badge.low {
                    background: rgba(245, 158, 11, 0.2);
                    color: var(--color-warning);
                }
                
                .predictions-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--space-md);
                }
                
                .prediction-row {
                    display: grid;
                    grid-template-columns: 150px 1fr 60px 80px;
                    align-items: center;
                    gap: var(--space-md);
                }
                
                .pred-type {
                    font-size: 0.875rem;
                    font-weight: 500;
                }
                
                .pred-bar {
                    height: 8px;
                    background: var(--bg-tertiary);
                    border-radius: var(--radius-full);
                    overflow: hidden;
                }
                
                .pred-fill {
                    height: 100%;
                    border-radius: var(--radius-full);
                    transition: width 0.5s ease;
                }
                
                .pred-score {
                    font-weight: 600;
                    text-align: right;
                }
                
                .pred-level {
                    font-weight: 600;
                    font-size: 0.75rem;
                }
                
                .disclaimer {
                    display: flex;
                    gap: var(--space-md);
                    padding: var(--space-lg);
                    background: rgba(245, 158, 11, 0.1);
                    border: 1px solid rgba(245, 158, 11, 0.3);
                    border-radius: var(--radius-lg);
                    color: var(--color-warning);
                }
                
                .disclaimer p {
                    font-size: 0.875rem;
                    margin: 0;
                }
                
                .spin {
                    animation: spin 1s linear infinite;
                }
                
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }

                .header-actions {
                    display: flex;
                    gap: var(--space-md);
                }

                .export-dropdown {
                    position: relative;
                }

                .export-dropdown:hover .dropdown-menu {
                    display: flex;
                }

                .dropdown-menu {
                    display: none;
                    position: absolute;
                    top: 100%;
                    right: 0;
                    margin-top: 4px;
                    background: var(--bg-card);
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-md);
                    padding: var(--space-xs);
                    flex-direction: column;
                    min-width: 120px;
                    z-index: 100;
                }

                .dropdown-menu button {
                    display: flex;
                    align-items: center;
                    gap: var(--space-sm);
                    padding: var(--space-sm) var(--space-md);
                    background: transparent;
                    border: none;
                    color: var(--text-primary);
                    cursor: pointer;
                    border-radius: var(--radius-sm);
                    transition: background 0.2s;
                }

                .dropdown-menu button:hover {
                    background: var(--bg-tertiary);
                }

                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                }

                .share-modal {
                    background: var(--bg-card);
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-lg);
                    padding: var(--space-xl);
                    min-width: 400px;
                    position: relative;
                }

                .share-modal h3 {
                    margin: 0 0 var(--space-lg);
                }

                .share-option {
                    margin-bottom: var(--space-md);
                }

                .share-option label {
                    display: block;
                    margin-bottom: var(--space-sm);
                    color: var(--text-muted);
                    font-size: 0.875rem;
                }

                .share-input {
                    display: flex;
                    gap: var(--space-sm);
                }

                .share-input input {
                    flex: 1;
                    padding: var(--space-sm) var(--space-md);
                    background: var(--bg-tertiary);
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-md);
                    color: var(--text-primary);
                }

                .share-divider {
                    text-align: center;
                    color: var(--text-muted);
                    margin: var(--space-md) 0;
                }

                .full-width {
                    width: 100%;
                    justify-content: center;
                }

                .share-status {
                    margin-top: var(--space-md);
                    padding: var(--space-sm) var(--space-md);
                    border-radius: var(--radius-md);
                    font-size: 0.875rem;
                }

                .share-status.success {
                    background: rgba(16, 185, 129, 0.2);
                    color: var(--color-success);
                }

                .share-status.error {
                    background: rgba(239, 68, 68, 0.2);
                    color: var(--color-error);
                }

                .modal-close {
                    position: absolute;
                    top: var(--space-md);
                    right: var(--space-md);
                    background: transparent;
                    border: none;
                    color: var(--text-muted);
                    cursor: pointer;
                    font-size: 1.25rem;
                }
            `}</style>
        </div>
    )
}

export default ReportsView
