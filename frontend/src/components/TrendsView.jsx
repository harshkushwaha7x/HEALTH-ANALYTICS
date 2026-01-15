import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react'
import TrendChart from './TrendChart'

function TrendsView({ dashboardData }) {
    const [selectedMetric, setSelectedMetric] = useState('A1C')

    if (!dashboardData) {
        return (
            <div className="trends-view empty">
                <p>Select a patient to view trends</p>
            </div>
        )
    }

    const { lab_trends, patient } = dashboardData
    const availableMetrics = Object.keys(lab_trends || {})

    // Get trend data for the selected metric
    const trendData = lab_trends?.[selectedMetric] || []

    // Calculate statistics
    const calculateStats = (data) => {
        if (!data || data.length === 0) return { avg: 0, min: 0, max: 0, change: 0 }
        const values = data.map(d => d.value).filter(v => v != null)
        if (values.length === 0) return { avg: 0, min: 0, max: 0, change: 0 }

        const avg = values.reduce((a, b) => a + b, 0) / values.length
        const min = Math.min(...values)
        const max = Math.max(...values)
        const change = values.length >= 2 ? ((values[values.length - 1] - values[0]) / values[0] * 100) : 0

        return { avg: avg.toFixed(1), min: min.toFixed(1), max: max.toFixed(1), change: change.toFixed(1) }
    }

    const stats = calculateStats(trendData)

    return (
        <div className="trends-view">
            <div className="trends-header">
                <h2>Health Trends for {patient?.name}</h2>
                <p className="subtitle">Analyze historical data and patterns over time</p>
            </div>

            <div className="metric-selector">
                <h3>Select Metric</h3>
                <div className="metric-buttons">
                    {availableMetrics.map(metric => (
                        <button
                            key={metric}
                            className={`metric-btn ${selectedMetric === metric ? 'active' : ''}`}
                            onClick={() => setSelectedMetric(metric)}
                        >
                            {metric.replace(/_/g, ' ')}
                        </button>
                    ))}
                </div>
            </div>

            <div className="trend-stats">
                <div className="stat-card">
                    <span className="stat-label">Average</span>
                    <span className="stat-value">{stats.avg}</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">Minimum</span>
                    <span className="stat-value">{stats.min}</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">Maximum</span>
                    <span className="stat-value">{stats.max}</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">Change</span>
                    <span className={`stat-value ${parseFloat(stats.change) > 0 ? 'text-red' : parseFloat(stats.change) < 0 ? 'text-green' : ''}`}>
                        {parseFloat(stats.change) > 0 ? '+' : ''}{stats.change}%
                    </span>
                </div>
            </div>

            <div className="trend-chart-container">
                <h3>{selectedMetric.replace(/_/g, ' ')} Over Time</h3>
                {trendData && trendData.length > 0 ? (
                    <TrendChart
                        data={trendData}
                        label={selectedMetric}
                        color="var(--color-primary)"
                        height={300}
                    />
                ) : (
                    <div className="no-data">
                        <p>No data available for {selectedMetric}</p>
                    </div>
                )}
            </div>

            <div className="all-trends">
                <h3>All Metrics Overview</h3>
                <div className="trends-grid">
                    {availableMetrics.slice(0, 6).map(metric => {
                        const data = lab_trends?.[metric] || []
                        const metricStats = calculateStats(data)
                        const isIncreasing = parseFloat(metricStats.change) > 5
                        const isDecreasing = parseFloat(metricStats.change) < -5

                        return (
                            <div key={metric} className="mini-trend-card" onClick={() => setSelectedMetric(metric)}>
                                <div className="mini-header">
                                    <span className="mini-label">{metric.replace(/_/g, ' ')}</span>
                                    {isIncreasing && <TrendingUp size={16} className="text-red" />}
                                    {isDecreasing && <TrendingDown size={16} className="text-green" />}
                                    {!isIncreasing && !isDecreasing && <Minus size={16} className="text-muted" />}
                                </div>
                                <div className="mini-value">
                                    {data.length > 0 ? data[data.length - 1]?.value?.toFixed(1) || 'N/A' : 'N/A'}
                                </div>
                                <div className="mini-chart">
                                    <TrendChart data={data} height={40} minimal={true} />
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>

            <style>{`
                .trends-view {
                    padding: var(--space-xl);
                }
                
                .trends-view.empty {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 400px;
                    color: var(--text-muted);
                }
                
                .trends-header {
                    margin-bottom: var(--space-xl);
                }
                
                .trends-header h2 {
                    font-size: 1.5rem;
                    margin-bottom: var(--space-xs);
                }
                
                .subtitle {
                    color: var(--text-muted);
                }
                
                .metric-selector {
                    margin-bottom: var(--space-xl);
                }
                
                .metric-selector h3 {
                    font-size: 0.875rem;
                    color: var(--text-secondary);
                    margin-bottom: var(--space-md);
                }
                
                .metric-buttons {
                    display: flex;
                    flex-wrap: wrap;
                    gap: var(--space-sm);
                }
                
                .metric-btn {
                    padding: var(--space-sm) var(--space-md);
                    border-radius: var(--radius-md);
                    background: var(--bg-tertiary);
                    border: 1px solid var(--border-color);
                    color: var(--text-secondary);
                    cursor: pointer;
                    transition: all var(--transition-fast);
                }
                
                .metric-btn:hover {
                    background: var(--bg-hover);
                    color: var(--text-primary);
                }
                
                .metric-btn.active {
                    background: var(--color-primary);
                    color: white;
                    border-color: var(--color-primary);
                }
                
                .trend-stats {
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: var(--space-md);
                    margin-bottom: var(--space-xl);
                }
                
                .stat-card {
                    background: var(--bg-card);
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    text-align: center;
                }
                
                .stat-label {
                    display: block;
                    font-size: 0.75rem;
                    color: var(--text-muted);
                    margin-bottom: var(--space-xs);
                }
                
                .stat-value {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--text-primary);
                }
                
                .text-red { color: var(--color-error); }
                .text-green { color: var(--color-success); }
                .text-muted { color: var(--text-muted); }
                
                .trend-chart-container {
                    background: var(--bg-card);
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    margin-bottom: var(--space-xl);
                }
                
                .trend-chart-container h3 {
                    margin-bottom: var(--space-md);
                }
                
                .no-data {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 200px;
                    color: var(--text-muted);
                }
                
                .all-trends h3 {
                    margin-bottom: var(--space-md);
                }
                
                .trends-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: var(--space-md);
                }
                
                .mini-trend-card {
                    background: var(--bg-card);
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-lg);
                    padding: var(--space-md);
                    cursor: pointer;
                    transition: all var(--transition-fast);
                }
                
                .mini-trend-card:hover {
                    border-color: var(--color-primary);
                    transform: translateY(-2px);
                }
                
                .mini-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--space-xs);
                }
                
                .mini-label {
                    font-size: 0.75rem;
                    color: var(--text-secondary);
                    text-transform: uppercase;
                }
                
                .mini-value {
                    font-size: 1.25rem;
                    font-weight: 700;
                    margin-bottom: var(--space-sm);
                }
                
                @media (max-width: 768px) {
                    .trend-stats {
                        grid-template-columns: repeat(2, 1fr);
                    }
                    .trends-grid {
                        grid-template-columns: repeat(2, 1fr);
                    }
                }
            `}</style>
        </div>
    )
}

export default TrendsView
