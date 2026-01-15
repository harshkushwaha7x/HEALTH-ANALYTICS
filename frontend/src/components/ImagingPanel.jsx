import { Image, AlertCircle, CheckCircle, Calendar } from 'lucide-react'

function ImagingPanel({ imaging }) {
    if (!imaging || imaging.length === 0) {
        return (
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">
                        <Image size={18} />
                        Imaging Studies
                    </h3>
                </div>
                <div className="empty-state">
                    <p className="text-muted text-sm">No imaging studies available</p>
                </div>
            </div>
        )
    }

    const getModalityIcon = (modality) => {
        switch (modality?.toUpperCase()) {
            case 'XRAY': return '🩻'
            case 'CT': return '🔬'
            case 'MRI': return '🧲'
            default: return '📷'
        }
    }

    const getSeverityClass = (score) => {
        if (score < 0.3) return 'normal'
        if (score < 0.6) return 'moderate'
        return 'high'
    }

    const formatDate = (dateStr) => {
        if (!dateStr) return 'Unknown date'
        const date = new Date(dateStr)
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        })
    }

    return (
        <div className="imaging-panel card">
            <div className="card-header">
                <h3 className="card-title">
                    <Image size={18} />
                    Imaging Studies
                </h3>
                <span className="text-muted text-xs">
                    {imaging.length} studies
                </span>
            </div>

            <div className="imaging-list">
                {imaging.map((study, idx) => (
                    <div key={idx} className="imaging-item">
                        <div className="imaging-icon">
                            {getModalityIcon(study.modality)}
                        </div>

                        <div className="imaging-info">
                            <div className="imaging-header">
                                <span className="modality-name">
                                    {study.modality} - {study.body_part}
                                </span>
                                <span className={`abnormality-indicator ${getSeverityClass(study.abnormality_score)}`}>
                                    {study.abnormality_score < 0.3 ? (
                                        <><CheckCircle size={12} /> Normal</>
                                    ) : (
                                        <><AlertCircle size={12} /> Review Needed</>
                                    )}
                                </span>
                            </div>

                            <div className="imaging-date">
                                <Calendar size={12} />
                                {formatDate(study.study_date)}
                            </div>

                            {study.findings && (
                                <div className="imaging-findings">
                                    {Array.isArray(study.findings)
                                        ? study.findings.slice(0, 2).join(', ')
                                        : study.findings
                                    }
                                </div>
                            )}

                            <div className="abnormality-bar">
                                <div
                                    className={`abnormality-fill ${getSeverityClass(study.abnormality_score)}`}
                                    style={{ width: `${(study.abnormality_score || 0) * 100}%` }}
                                />
                                <span className="abnormality-score">
                                    {Math.round((study.abnormality_score || 0) * 100)}% abnormality
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <style>{`
        .imaging-panel {
          max-height: 350px;
          overflow-y: auto;
        }
        
        .imaging-list {
          display: flex;
          flex-direction: column;
          gap: var(--space-md);
        }
        
        .imaging-item {
          display: flex;
          gap: var(--space-md);
          padding: var(--space-md);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
        }
        
        .imaging-icon {
          font-size: 2rem;
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
        }
        
        .imaging-info {
          flex: 1;
        }
        
        .imaging-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-xs);
        }
        
        .modality-name {
          font-weight: 600;
          font-size: 0.9rem;
          color: var(--text-primary);
        }
        
        .abnormality-indicator {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          font-size: 0.7rem;
          font-weight: 500;
          padding: 2px 6px;
          border-radius: var(--radius-sm);
        }
        
        .abnormality-indicator.normal {
          background: var(--color-success-bg);
          color: var(--color-success-light);
        }
        
        .abnormality-indicator.moderate {
          background: var(--color-warning-bg);
          color: var(--color-warning-light);
        }
        
        .abnormality-indicator.high {
          background: var(--color-danger-bg);
          color: var(--color-danger-light);
        }
        
        .imaging-date {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-bottom: var(--space-xs);
        }
        
        .imaging-findings {
          font-size: 0.8rem;
          color: var(--text-secondary);
          margin-bottom: var(--space-sm);
          line-height: 1.4;
        }
        
        .abnormality-bar {
          position: relative;
          height: 4px;
          background: var(--bg-secondary);
          border-radius: var(--radius-full);
          overflow: hidden;
        }
        
        .abnormality-fill {
          height: 100%;
          border-radius: var(--radius-full);
          transition: width 0.3s ease;
        }
        
        .abnormality-fill.normal { background: var(--color-success); }
        .abnormality-fill.moderate { background: var(--color-warning); }
        .abnormality-fill.high { background: var(--color-danger); }
        
        .abnormality-score {
          position: absolute;
          right: 0;
          top: 8px;
          font-size: 0.65rem;
          color: var(--text-muted);
        }
      `}</style>
        </div>
    )
}

export default ImagingPanel
