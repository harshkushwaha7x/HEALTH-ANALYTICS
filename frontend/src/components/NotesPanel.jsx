import { FileText, Calendar, Pill, Thermometer, Stethoscope } from 'lucide-react'

function NotesPanel({ notes }) {
    if (!notes || notes.length === 0) {
        return (
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">
                        <FileText size={18} />
                        Clinical Notes
                    </h3>
                </div>
                <div className="empty-state">
                    <p className="text-muted text-sm">No clinical notes available</p>
                </div>
            </div>
        )
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

    const getSentimentIndicator = (score) => {
        if (score > 0.3) return { text: 'Positive', class: 'positive' }
        if (score < -0.3) return { text: 'Concerning', class: 'concerning' }
        return { text: 'Neutral', class: 'neutral' }
    }

    return (
        <div className="notes-panel card">
            <div className="card-header">
                <h3 className="card-title">
                    <FileText size={18} />
                    Clinical Notes
                </h3>
                <span className="text-muted text-xs">
                    {notes.length} notes
                </span>
            </div>

            <div className="notes-list">
                {notes.map((note, idx) => {
                    const sentiment = getSentimentIndicator(note.sentiment_score || 0)
                    const conditions = note.conditions || []
                    const medications = note.medications || []
                    const symptoms = note.symptoms || []

                    return (
                        <div key={idx} className="note-item">
                            <div className="note-header">
                                <div className="note-type">
                                    <span className="type-badge">{note.note_type || 'Note'}</span>
                                    <span className={`sentiment-badge ${sentiment.class}`}>
                                        {sentiment.text}
                                    </span>
                                </div>
                                <span className="note-date">
                                    <Calendar size={12} />
                                    {formatDate(note.note_date)}
                                </span>
                            </div>

                            {/* Extracted Entities */}
                            <div className="extracted-entities">
                                {conditions.length > 0 && (
                                    <div className="entity-group">
                                        <span className="entity-label">
                                            <Stethoscope size={12} />
                                            Conditions
                                        </span>
                                        <div className="entity-tags">
                                            {conditions.slice(0, 3).map((c, cidx) => (
                                                <span key={cidx} className="entity-tag condition">{c}</span>
                                            ))}
                                            {conditions.length > 3 && (
                                                <span className="entity-tag more">+{conditions.length - 3}</span>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {medications.length > 0 && (
                                    <div className="entity-group">
                                        <span className="entity-label">
                                            <Pill size={12} />
                                            Medications
                                        </span>
                                        <div className="entity-tags">
                                            {medications.slice(0, 3).map((m, midx) => (
                                                <span key={midx} className="entity-tag medication">{m}</span>
                                            ))}
                                            {medications.length > 3 && (
                                                <span className="entity-tag more">+{medications.length - 3}</span>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {symptoms.length > 0 && (
                                    <div className="entity-group">
                                        <span className="entity-label">
                                            <Thermometer size={12} />
                                            Symptoms
                                        </span>
                                        <div className="entity-tags">
                                            {symptoms.slice(0, 3).map((s, sidx) => (
                                                <span key={sidx} className="entity-tag symptom">{s}</span>
                                            ))}
                                            {symptoms.length > 3 && (
                                                <span className="entity-tag more">+{symptoms.length - 3}</span>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Note Preview */}
                            {note.content && (
                                <div className="note-preview">
                                    {note.content.substring(0, 150)}
                                    {note.content.length > 150 && '...'}
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>

            <style>{`
        .notes-panel {
          max-height: 350px;
          overflow-y: auto;
        }
        
        .notes-list {
          display: flex;
          flex-direction: column;
          gap: var(--space-md);
        }
        
        .note-item {
          padding: var(--space-md);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
        }
        
        .note-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: var(--space-sm);
        }
        
        .note-type {
          display: flex;
          gap: var(--space-xs);
        }
        
        .type-badge {
          font-size: 0.65rem;
          font-weight: 600;
          padding: 2px 6px;
          border-radius: var(--radius-sm);
          background: var(--color-primary-light);
          color: white;
          text-transform: uppercase;
        }
        
        .sentiment-badge {
          font-size: 0.6rem;
          font-weight: 500;
          padding: 2px 6px;
          border-radius: var(--radius-sm);
        }
        
        .sentiment-badge.positive {
          background: var(--color-success-bg);
          color: var(--color-success-light);
        }
        
        .sentiment-badge.neutral {
          background: var(--bg-secondary);
          color: var(--text-muted);
        }
        
        .sentiment-badge.concerning {
          background: var(--color-warning-bg);
          color: var(--color-warning-light);
        }
        
        .note-date {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          font-size: 0.7rem;
          color: var(--text-muted);
        }
        
        .extracted-entities {
          display: flex;
          flex-direction: column;
          gap: var(--space-sm);
          margin-bottom: var(--space-sm);
        }
        
        .entity-group {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        
        .entity-label {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          font-size: 0.65rem;
          color: var(--text-muted);
          text-transform: uppercase;
        }
        
        .entity-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 2px;
        }
        
        .entity-tag {
          font-size: 0.65rem;
          padding: 2px 6px;
          border-radius: var(--radius-sm);
          background: var(--bg-secondary);
          color: var(--text-secondary);
        }
        
        .entity-tag.condition {
          background: rgba(239, 68, 68, 0.1);
          color: var(--color-danger-light);
        }
        
        .entity-tag.medication {
          background: rgba(59, 130, 246, 0.1);
          color: var(--color-info-light);
        }
        
        .entity-tag.symptom {
          background: rgba(245, 158, 11, 0.1);
          color: var(--color-warning-light);
        }
        
        .entity-tag.more {
          background: var(--bg-secondary);
          color: var(--text-muted);
        }
        
        .note-preview {
          font-size: 0.75rem;
          color: var(--text-muted);
          line-height: 1.5;
          padding-top: var(--space-sm);
          border-top: 1px solid var(--border-color);
        }
      `}</style>
        </div>
    )
}

export default NotesPanel
