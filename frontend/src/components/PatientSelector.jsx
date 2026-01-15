import { User, ChevronDown } from 'lucide-react'
import { useState } from 'react'

function PatientSelector({ patients, selectedPatient, onSelectPatient }) {
  const [isOpen, setIsOpen] = useState(false)

  const calculateAge = (dob) => {
    if (!dob) return null
    const birth = new Date(dob)
    const today = new Date()
    let age = today.getFullYear() - birth.getFullYear()
    const m = today.getMonth() - birth.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    return age
  }

  return (
    <div className="patient-selector">
      <button
        className="selector-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="patient-avatar">
          <User size={20} />
        </div>
        <div className="patient-info">
          <span className="patient-name">{selectedPatient?.name || 'Select Patient'}</span>
          {selectedPatient && (
            <span className="patient-meta">
              {selectedPatient.gender} • {calculateAge(selectedPatient.date_of_birth)} years
            </span>
          )}
        </div>
        <ChevronDown size={18} className={`chevron ${isOpen ? 'open' : ''}`} />
      </button>

      {isOpen && (
        <div className="dropdown-menu animate-scale-in">
          {patients.map(patient => (
            <button
              key={patient.id}
              className={`dropdown-item ${selectedPatient?.id === patient.id ? 'active' : ''}`}
              onClick={() => {
                onSelectPatient(patient)
                setIsOpen(false)
              }}
            >
              <div className="patient-avatar small">
                <User size={16} />
              </div>
              <div className="patient-info">
                <span className="patient-name">{patient.name}</span>
                <span className="patient-meta">
                  {patient.gender} • {calculateAge(patient.date_of_birth)} years • {patient.blood_type}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      <style>{`
        .patient-selector {
          position: relative;
        }
        
        .selector-button {
          display: flex;
          align-items: center;
          gap: var(--space-md);
          padding: var(--space-sm) var(--space-md);
          background: var(--bg-card);
          border: 1px solid var(--border-color);
          border-radius: var(--radius-lg);
          cursor: pointer;
          transition: all var(--transition-fast);
          min-width: 280px;
        }
        
        .selector-button:hover {
          border-color: var(--border-hover);
          background: var(--bg-glass);
        }
        
        .patient-avatar {
          width: 40px;
          height: 40px;
          border-radius: var(--radius-md);
          background: linear-gradient(135deg, var(--color-primary), var(--color-info));
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }
        
        .patient-avatar.small {
          width: 32px;
          height: 32px;
        }
        
        .patient-info {
          flex: 1;
          text-align: left;
        }
        
        .patient-name {
          display: block;
          font-weight: 600;
          color: var(--text-primary);
          font-size: 0.9rem;
        }
        
        .patient-meta {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        
        .chevron {
          color: var(--text-muted);
          transition: transform var(--transition-fast);
        }
        
        .chevron.open {
          transform: rotate(180deg);
        }
        
        .dropdown-menu {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          margin-top: var(--space-xs);
          background: var(--bg-secondary);
          border: 1px solid var(--border-color);
          border-radius: var(--radius-lg);
          padding: var(--space-xs);
          box-shadow: var(--shadow-lg);
          z-index: 50;
          max-height: 300px;
          overflow-y: auto;
        }
        
        .dropdown-item {
          display: flex;
          align-items: center;
          gap: var(--space-md);
          padding: var(--space-sm) var(--space-md);
          background: transparent;
          border: none;
          border-radius: var(--radius-md);
          cursor: pointer;
          width: 100%;
          transition: all var(--transition-fast);
        }
        
        .dropdown-item:hover {
          background: var(--bg-tertiary);
        }
        
        .dropdown-item.active {
          background: rgba(8, 145, 178, 0.15);
        }
        
        .dropdown-item.active .patient-avatar {
          background: var(--color-primary);
        }
      `}</style>
    </div>
  )
}

export default PatientSelector
