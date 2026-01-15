import { Activity } from 'lucide-react'

function Header({ activeView, onViewChange }) {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">
              <Activity size={24} />
            </div>
            <div className="logo-text">
              <h1>Health Analytics</h1>
              <span className="tagline">AI-Powered Health Intelligence</span>
            </div>
          </div>

          <nav className="nav-links">
            <button
              onClick={() => onViewChange('dashboard')}
              className={`nav-link ${activeView === 'dashboard' ? 'active' : ''}`}
            >
              Dashboard
            </button>
            <button
              onClick={() => onViewChange('trends')}
              className={`nav-link ${activeView === 'trends' ? 'active' : ''}`}
            >
              Trends
            </button>
            <button
              onClick={() => onViewChange('reports')}
              className={`nav-link ${activeView === 'reports' ? 'active' : ''}`}
            >
              Reports
            </button>
          </nav>
        </div>
      </div>

      <style>{`
        .header {
          background: var(--bg-secondary);
          border-bottom: 1px solid var(--border-color);
          padding: var(--space-md) 0;
          position: sticky;
          top: 0;
          z-index: 100;
          backdrop-filter: blur(12px);
        }
        
        .header-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        
        .logo {
          display: flex;
          align-items: center;
          gap: var(--space-md);
        }
        
        .logo-icon {
          width: 44px;
          height: 44px;
          border-radius: var(--radius-lg);
          background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          box-shadow: var(--shadow-glow);
        }
        
        .logo-text h1 {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0;
          background: linear-gradient(135deg, var(--text-primary), var(--color-primary-light));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        
        .tagline {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        
        .nav-links {
          display: flex;
          gap: var(--space-lg);
        }
        
        .nav-link {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-secondary);
          padding: var(--space-sm) var(--space-md);
          border-radius: var(--radius-md);
          transition: all var(--transition-fast);
        }
        
        .nav-link:hover {
          color: var(--text-primary);
          background: var(--bg-tertiary);
        }
        
        .nav-link.active {
          color: var(--color-primary-light);
          background: rgba(8, 145, 178, 0.1);
        }
        
        @media (max-width: 640px) {
          .nav-links {
            display: none;
          }
        }
      `}</style>
    </header>
  )
}

export default Header
