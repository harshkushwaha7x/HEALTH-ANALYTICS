import { Brain, AlertTriangle, ChevronRight, Info } from 'lucide-react'

function PredictionsPanel({ predictions }) {
    if (!predictions || predictions.length === 0) {
        return (
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">
                        <Brain size={18} />
                        AI Predictions
                    </h3>
                </div>
                <div className="empty-state">
                    <p className="text-muted">No predictions available</p>
                    <p className="text-xs text-muted mt-sm">Run AI Analysis to generate predictions</p>
                </div>
            </div>
        )
    }

    const getRiskBadgeClass = (level) => {
        switch (level?.toUpperCase()) {
            case 'LOW': return 'low'
            case 'MODERATE': return 'moderate'
            case 'HIGH': return 'high'
            case 'CRITICAL': return 'critical'
            default: return ''
        }
    }

    const formatPredictionType = (type) => {
        return type
            .replace(/_/g, ' ')
            .replace(/RISK/gi, 'Risk')
            .replace(/\b\w/g, l => l.toUpperCase())
    }

    // Filter out overall health as it's shown in header
    const domainPredictions = predictions.filter(p => p.prediction_type !== 'OVERALL_HEALTH')

    return (
        <div className="predictions-panel card">
            <div className="card-header">
                <h3 className="card-title">
                    <Brain size={18} />
                    AI Predictions
                </h3>
                <span className="text-muted text-xs">
                    {domainPredictions.length} analyses
                </span>
            </div>

            <div className="predictions-list">
                {domainPredictions.map((prediction, idx) => (
                    <div key={idx} className="prediction-item">
                        <div className="prediction-header">
                            <span className="prediction-type">
                                {formatPredictionType(prediction.prediction_type)}
                            </span>
                            <span className={`risk-badge ${getRiskBadgeClass(prediction.risk_level)}`}>
                                {prediction.risk_level}
                            </span>
                        </div>

                        <div className="prediction-score">
                            <div className="score-bar">
                                <div
                                    className={`score-fill ${getRiskBadgeClass(prediction.risk_level)}`}
                                    style={{ width: `${Math.round(prediction.risk_score * 100)}%` }}
                                />
                            </div>
                            <span className="score-value">
                                {Math.round(prediction.risk_score * 100)}% Risk
                            </span>
                        </div>

                        {/* Contributing Factors */}
                        {prediction.contributing_factors && prediction.contributing_factors.length > 0 && (
                            <div className="contributing-factors">
                                <span className="factors-label">Key Factors:</span>
                                <div className="factors-list">
                                    {prediction.contributing_factors.slice(0, 3).map((factor, fidx) => (
                                        <div key={fidx} className="factor-item">
                                            <ChevronRight size={12} />
                                            <span className="factor-name">{factor.factor}</span>
                                            <span className={`factor-impact ${factor.impact?.toLowerCase()}`}>
                                                {factor.impact}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Confidence */}
                        <div className="prediction-footer">
                            <span className="confidence">
                                <Info size={12} />
                                Confidence: {Math.round((prediction.confidence || 0) * 100)}%
                            </span>
                            <span className="modalities">
                                Sources: {prediction.modalities_used?.join(', ') || 'N/A'}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            <style>{`
        .predictions-panel {
          max-height: 400px;
          overflow-y: auto;
        }
        
        .predictions-list {
          display: flex;
          flex-direction: column;
          gap: var(--space-md);
        }
        
        .prediction-item {
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
          padding: var(--space-md);
        }
        
        .prediction-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-sm);
        }
        
        .prediction-type {
          font-size: 0.9rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .prediction-score {
          display: flex;
          align-items: center;
          gap: var(--space-md);
          margin-bottom: var(--space-md);
        }
        
        .score-bar {
          flex: 1;
          height: 6px;
          background: var(--bg-secondary);
          border-radius: var(--radius-full);
          overflow: hidden;
        }
        
        .score-fill {
          height: 100%;
          border-radius: var(--radius-full);
          transition: width 0.5s ease;
        }
        
        .score-fill.low { background: var(--color-success); }
        .score-fill.moderate { background: var(--color-warning); }
        .score-fill.high { background: var(--color-danger); }
        .score-fill.critical { background: var(--color-danger); }
        
        .score-value {
          font-size: 0.8rem;
          font-weight: 600;
          color: var(--text-secondary);
          white-space: nowrap;
        }
        
        .contributing-factors {
          margin-bottom: var(--space-sm);
        }
        
        .factors-label {
          font-size: 0.7rem;
          color: var(--text-muted);
          text-transform: uppercase;
          display: block;
          margin-bottom: var(--space-xs);
        }
        
        .factors-list {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        
        .factor-item {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
        
        .factor-item svg {
          color: var(--text-muted);
        }
        
        .factor-name {
          flex: 1;
        }
        
        .factor-impact {
          font-size: 0.65rem;
          font-weight: 600;
          padding: 1px 4px;
          border-radius: var(--radius-sm);
        }
        
        .factor-impact.high {
          background: var(--color-danger-bg);
          color: var(--color-danger-light);
        }
        
        .factor-impact.moderate {
          background: var(--color-warning-bg);
          color: var(--color-warning-light);
        }
        
        .factor-impact.low {
          background: var(--color-success-bg);
          color: var(--color-success-light);
        }
        
        .prediction-footer {
          display: flex;
          justify-content: space-between;
          padding-top: var(--space-sm);
          border-top: 1px solid var(--border-color);
        }
        
        .confidence,
        .modalities {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          font-size: 0.65rem;
          color: var(--text-muted);
        }
      `}</style>
        </div>
    )
}

export default PredictionsPanel
