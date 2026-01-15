import { Dna, AlertTriangle, Shield, ChevronRight } from 'lucide-react'

function GenomicsPanel({ genomics }) {
    if (!genomics || !genomics.variants || genomics.variants.length === 0) {
        return (
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">
                        <Dna size={18} />
                        Genomics Data
                    </h3>
                </div>
                <div className="empty-state">
                    <p className="text-muted text-sm">No genomic data available</p>
                </div>
            </div>
        )
    }

    const { variants, high_risk_count } = genomics

    const getClassificationBadge = (classification) => {
        switch (classification?.toUpperCase()) {
            case 'PATHOGENIC':
                return <span className="classification-badge pathogenic">Pathogenic</span>
            case 'LIKELY_PATHOGENIC':
                return <span className="classification-badge likely-pathogenic">Likely Pathogenic</span>
            case 'VUS':
                return <span className="classification-badge vus">VUS</span>
            case 'BENIGN':
                return <span className="classification-badge benign">Benign</span>
            default:
                return <span className="classification-badge unknown">Unknown</span>
        }
    }

    // Sort variants by pathogenicity
    const sortedVariants = [...variants].sort((a, b) => {
        const order = { 'PATHOGENIC': 0, 'LIKELY_PATHOGENIC': 1, 'VUS': 2, 'BENIGN': 3 }
        return (order[a.classification] || 4) - (order[b.classification] || 4)
    })

    return (
        <div className="genomics-panel card">
            <div className="card-header">
                <h3 className="card-title">
                    <Dna size={18} />
                    Genomics Data
                </h3>
                {high_risk_count > 0 && (
                    <span className="risk-count">
                        <AlertTriangle size={14} />
                        {high_risk_count} High Risk
                    </span>
                )}
            </div>

            <div className="genomics-summary">
                <div className="summary-stat">
                    <span className="stat-value">{variants.length}</span>
                    <span className="stat-label">Total Variants</span>
                </div>
                <div className="summary-stat">
                    <span className="stat-value text-danger">{high_risk_count}</span>
                    <span className="stat-label">Pathogenic</span>
                </div>
                <div className="summary-stat">
                    <span className="stat-value text-warning">
                        {variants.filter(v => v.classification === 'VUS').length}
                    </span>
                    <span className="stat-label">VUS</span>
                </div>
            </div>

            <div className="variants-list">
                {sortedVariants.slice(0, 5).map((variant, idx) => (
                    <div key={idx} className="variant-item">
                        <div className="variant-header">
                            <span className="gene-name">{variant.gene}</span>
                            {getClassificationBadge(variant.classification)}
                        </div>

                        <div className="variant-details">
                            <span className="variant-id">{variant.variant}</span>
                            {variant.pathogenicity_score && (
                                <span className="pathogenicity-score">
                                    Score: {(variant.pathogenicity_score * 100).toFixed(0)}%
                                </span>
                            )}
                        </div>

                        {variant.associated_conditions && variant.associated_conditions.length > 0 && (
                            <div className="associated-conditions">
                                {variant.associated_conditions.slice(0, 2).map((condition, cidx) => (
                                    <span key={cidx} className="condition-tag">
                                        <ChevronRight size={10} />
                                        {condition}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                ))}

                {variants.length > 5 && (
                    <p className="more-variants text-muted text-xs">
                        +{variants.length - 5} more variants
                    </p>
                )}
            </div>

            <style>{`
        .genomics-panel {
          max-height: 350px;
          overflow-y: auto;
        }
        
        .risk-count {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          font-size: 0.75rem;
          color: var(--color-danger-light);
          background: var(--color-danger-bg);
          padding: 2px 8px;
          border-radius: var(--radius-full);
        }
        
        .genomics-summary {
          display: flex;
          gap: var(--space-lg);
          padding: var(--space-md);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
          margin-bottom: var(--space-md);
        }
        
        .summary-stat {
          flex: 1;
          text-align: center;
        }
        
        .stat-value {
          display: block;
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        
        .stat-label {
          font-size: 0.65rem;
          color: var(--text-muted);
          text-transform: uppercase;
        }
        
        .variants-list {
          display: flex;
          flex-direction: column;
          gap: var(--space-sm);
        }
        
        .variant-item {
          padding: var(--space-sm);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
          border-left: 3px solid var(--border-color);
        }
        
        .variant-item:has(.pathogenic) {
          border-left-color: var(--color-danger);
        }
        
        .variant-item:has(.likely-pathogenic) {
          border-left-color: var(--color-warning);
        }
        
        .variant-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-xs);
        }
        
        .gene-name {
          font-weight: 600;
          font-size: 0.9rem;
          color: var(--text-primary);
        }
        
        .classification-badge {
          font-size: 0.65rem;
          font-weight: 600;
          padding: 2px 6px;
          border-radius: var(--radius-sm);
        }
        
        .classification-badge.pathogenic {
          background: var(--color-danger-bg);
          color: var(--color-danger-light);
        }
        
        .classification-badge.likely-pathogenic {
          background: var(--color-warning-bg);
          color: var(--color-warning-light);
        }
        
        .classification-badge.vus {
          background: var(--color-info-bg);
          color: var(--color-info-light);
        }
        
        .classification-badge.benign {
          background: var(--color-success-bg);
          color: var(--color-success-light);
        }
        
        .variant-details {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-bottom: var(--space-xs);
        }
        
        .variant-id {
          font-family: monospace;
        }
        
        .associated-conditions {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-xs);
        }
        
        .condition-tag {
          display: flex;
          align-items: center;
          gap: 2px;
          font-size: 0.65rem;
          color: var(--text-secondary);
          background: var(--bg-secondary);
          padding: 2px 6px;
          border-radius: var(--radius-sm);
        }
        
        .more-variants {
          text-align: center;
          padding: var(--space-sm);
        }
      `}</style>
        </div>
    )
}

export default GenomicsPanel
