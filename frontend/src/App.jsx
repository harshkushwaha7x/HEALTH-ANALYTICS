import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import PatientSelector from './components/PatientSelector'
import FileUpload from './components/FileUpload'
import Header from './components/Header'
import TrendsView from './components/TrendsView'
import ReportsView from './components/ReportsView'

const API_BASE = '/api'

function App() {
    const [patients, setPatients] = useState([])
    const [selectedPatient, setSelectedPatient] = useState(null)
    const [dashboardData, setDashboardData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [showUpload, setShowUpload] = useState(false)
    const [activeView, setActiveView] = useState('dashboard')

    // Fetch patients on mount
    useEffect(() => {
        fetchPatients()
    }, [])

    // Fetch dashboard when patient changes
    useEffect(() => {
        if (selectedPatient) {
            fetchDashboard(selectedPatient.id)
        }
    }, [selectedPatient])

    const fetchPatients = async () => {
        try {
            const res = await fetch(`${API_BASE}/patients`)
            const data = await res.json()
            setPatients(data.patients || [])

            // Select first patient by default
            if (data.patients && data.patients.length > 0) {
                setSelectedPatient(data.patients[0])
            }
            setLoading(false)
        } catch (err) {
            setError('Failed to fetch patients. Make sure the backend is running.')
            setLoading(false)
        }
    }

    const fetchDashboard = async (patientId) => {
        try {
            setLoading(true)
            const res = await fetch(`${API_BASE}/patients/${patientId}/dashboard`)
            const data = await res.json()
            setDashboardData(data)
            setLoading(false)
        } catch (err) {
            setError('Failed to fetch dashboard data')
            setLoading(false)
        }
    }

    const handleInitSampleData = async () => {
        try {
            setLoading(true)
            setError(null)
            const res = await fetch(`${API_BASE}/init-sample-data`, { method: 'POST' })
            const data = await res.json()

            if (data.error) {
                setError(data.error)
            } else {
                await fetchPatients()
            }
            setLoading(false)
        } catch (err) {
            setError('Failed to initialize sample data')
            setLoading(false)
        }
    }

    const handleRunPredictions = async () => {
        if (!selectedPatient) return

        try {
            setLoading(true)
            const res = await fetch(`${API_BASE}/patients/${selectedPatient.id}/predict`, {
                method: 'POST'
            })
            const data = await res.json()

            if (data.error) {
                setError(data.error)
            } else {
                await fetchDashboard(selectedPatient.id)
            }
            setLoading(false)
        } catch (err) {
            setError('Failed to run predictions')
            setLoading(false)
        }
    }

    const handleUploadComplete = () => {
        setShowUpload(false)
        if (selectedPatient) {
            fetchDashboard(selectedPatient.id)
        }
    }

    const handleViewChange = (view) => {
        setActiveView(view)
    }

    // Render the active view
    const renderView = () => {
        switch (activeView) {
            case 'trends':
                return <TrendsView dashboardData={dashboardData} />
            case 'reports':
                return <ReportsView dashboardData={dashboardData} />
            default:
                return <Dashboard data={dashboardData} loading={loading} />
        }
    }

    // No patients - show init screen
    if (!loading && patients.length === 0) {
        return (
            <div className="app">
                <Header activeView={activeView} onViewChange={handleViewChange} />
                <main className="container" style={{ paddingTop: '2rem' }}>
                    <div className="card" style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
                        <div className="empty-state">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                                <path d="M2 17l10 5 10-5" />
                                <path d="M2 12l10 5 10-5" />
                            </svg>
                            <h2>Welcome to Health Analytics</h2>
                            <p className="mt-md text-secondary">
                                No patient data found. Initialize the system with sample data to get started.
                            </p>
                            <button
                                className="btn btn-primary mt-lg"
                                onClick={handleInitSampleData}
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className="spinner"></span>
                                        Initializing...
                                    </>
                                ) : (
                                    'Initialize Sample Data'
                                )}
                            </button>
                            {error && (
                                <p className="mt-md text-danger text-sm">{error}</p>
                            )}
                        </div>
                    </div>
                </main>
            </div>
        )
    }

    return (
        <div className="app">
            <Header activeView={activeView} onViewChange={handleViewChange} />

            <main className="container" style={{ paddingTop: '1rem', paddingBottom: '2rem' }}>
                {/* Patient Selector */}
                <div className="flex items-center justify-between mb-lg">
                    <PatientSelector
                        patients={patients}
                        selectedPatient={selectedPatient}
                        onSelectPatient={setSelectedPatient}
                    />

                    <div className="flex gap-sm">
                        <button
                            className="btn btn-secondary"
                            onClick={() => setShowUpload(true)}
                        >
                            Upload Data
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={handleRunPredictions}
                            disabled={loading || !selectedPatient}
                        >
                            {loading ? 'Analyzing...' : 'Run AI Analysis'}
                        </button>
                    </div>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="card mb-lg" style={{ borderColor: 'var(--color-danger)' }}>
                        <p className="text-danger">{error}</p>
                        <button
                            className="btn btn-secondary mt-sm"
                            onClick={() => setError(null)}
                        >
                            Dismiss
                        </button>
                    </div>
                )}

                {/* Loading State */}
                {loading && !dashboardData && (
                    <div className="flex justify-center items-center" style={{ minHeight: '400px' }}>
                        <div className="spinner" style={{ width: '48px', height: '48px' }}></div>
                    </div>
                )}

                {/* Render Active View */}
                {dashboardData && renderView()}
            </main>

            {/* Upload Modal */}
            {showUpload && selectedPatient && (
                <FileUpload
                    patientId={selectedPatient.id}
                    patientName={selectedPatient.name}
                    onClose={() => setShowUpload(false)}
                    onUploadComplete={handleUploadComplete}
                />
            )}
        </div>
    )
}

export default App

