import { Beaker, TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react'

function LabsPanel({ labs, trends }) {
    if (!labs || Object.keys(labs).length === 0) {
        return (
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">
                        <Beaker size={18} />
                        Laboratory Results
                    </h3>
                </div>
                <div className="empty-state">
                    <p className="text-muted">No lab results available</p>
                </div>
            </div>
        )
    }

    const labCategories = {
        'Diabetes Markers': ['A1C', 'GLUCOSE'],
        'Cardiovascular': ['LDL', 'HDL', 'CHOLESTEROL_TOTAL', 'TRIGLYCERIDES', 'BP_SYSTOLIC', 'BP_DIASTOLIC'],
        'Other': ['HEMOGLOBIN', 'WBC', 'PLATELETS', 'CREATININE', 'HEART_RATE']
    }

    const getStatusClass = (status) => {
        switch (status?.toUpperCase()) {
            case 'NORMAL': return 'normal'
            case 'HIGH': return 'high'
            case 'LOW': return 'low'
            default: return ''
        }
    }

    const getTrendIcon = (labType) => {
        const trendData = trends?.[labType]
        if (!trendData || trendData.length < 2) return null

        const first = trendData[0].value
        const last = trendData[trendData.length - 1].value
        const change = ((last - first) / first) * 100

        if (Math.abs(change) < 3) return <Minus size={14} className="text-muted" />
        if (change > 0) return <TrendingUp size={14} className="text-danger" />
        return <TrendingDown size={14} className="text-success" />
    }

    const formatLabName = (name) => {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const isInRange = (lab) => {
        if (!lab.reference_low && !lab.reference_high) return true
        if (lab.reference_low && lab.value < lab.reference_low) return false
        if (lab.reference_high && lab.value > lab.reference_high) return false
        return true
    }

    return (
        <div className="labs-panel card">
            <div className="card-header">
                <h3 className="card-title">
                    <Beaker size={18} />
                    Laboratory Results
                </h3>
                <span className="text-muted text-xs">
                    {Object.keys(labs).length} tests
                </span>
            </div>

            <div className="labs-content">
                {Object.entries(labCategories).map(([category, labTypes]) => {
                    const categoryLabs = labTypes.filter(type => labs[type])
                    if (categoryLabs.length === 0) return null

                    return (
                        <div key={category} className="lab-category">
                            <h4 className="category-title">{category}</h4>
                            <div className="lab-items">
                                {categoryLabs.map(labType => {
                                    const lab = labs[labType]
                                    if (!lab) return null

                                    return (
                                        <div key={labType} className="lab-item">
                                            <div className="lab-info">
                                                <span className="lab-name">{formatLabName(labType)}</span>
                                                {!isInRange(lab) && (
                                                    <AlertCircle size={12} className="text-warning" />
                                                )}
                                            </div>
                                            <div className="lab-value-row">
                                                <span className={`lab-value ${getStatusClass(lab.status)}`}>
                                                    {lab.value?.toFixed(1)}
                                                </span>
                                                <span className="lab-unit">{lab.unit}</span>
                                                {getTrendIcon(labType)}
                                            </div>
                                            <div className="lab-reference">
                                                {lab.reference_low && lab.reference_high && (
                                                    <span>Ref: {lab.reference_low} - {lab.reference_high}</span>
                                                )}
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    )
                })}
            </div>

            <style>{`
        .labs-panel {
          max-height: 400px;
          overflow-y: auto;
        }
        
        .labs-content {
          display: flex;
          flex-direction: column;
          gap: var(--space-lg);
        }
        
        .lab-category {
          border-bottom: 1px solid var(--border-color);
          padding-bottom: var(--space-md);
        }
        
        .lab-category:last-child {
          border-bottom: none;
        }
        
        .category-title {
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--text-muted);
          margin-bottom: var(--space-sm);
        }
        
        .lab-items {
          display: grid;
          gap: var(--space-sm);
        }
        
        .lab-item {
          display: grid;
          grid-template-columns: 1fr auto auto;
          align-items: center;
          gap: var(--space-sm);
          padding: var(--space-sm);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
        }
        
        .lab-info {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
        }
        
        .lab-name {
          font-size: 0.8rem;
          color: var(--text-secondary);
        }
        
        .lab-value-row {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
        }
        
        .lab-value {
          font-size: 0.9rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .lab-value.normal {
          color: var(--color-success-light);
        }
        
        .lab-value.high {
          color: var(--color-danger-light);
        }
        
        .lab-value.low {
          color: var(--color-info-light);
        }
        
        .lab-unit {
          font-size: 0.7rem;
          color: var(--text-muted);
        }
        
        .lab-reference {
          text-align: right;
        }
        
        .lab-reference span {
          font-size: 0.65rem;
          color: var(--text-muted);
        }
      `}</style>
        </div>
    )
}

export default LabsPanel
