import { useEffect, useRef, useMemo } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

function TrendChart({ title, data, unit, thresholds, color = '#0891b2', height = 150, minimal = false }) {
    const canvasRef = useRef(null)

    // Process data for chart
    const chartData = useMemo(() => {
        if (!data || data.length === 0) return null

        // Handle both array of objects and array of values
        const values = data.map(d => typeof d === 'object' ? d.value : d)
        const dates = data.map(d => typeof d === 'object' && d.date ? new Date(d.date) : null)

        const min = Math.min(...values)
        const max = Math.max(...values)
        const range = max - min || 1

        // Calculate trend
        const firstHalf = values.slice(0, Math.floor(values.length / 2))
        const secondHalf = values.slice(Math.floor(values.length / 2))
        const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length
        const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length

        let trend = 'stable'
        if (secondAvg > firstAvg * 1.05) trend = 'increasing'
        else if (secondAvg < firstAvg * 0.95) trend = 'decreasing'

        return {
            values,
            dates,
            min,
            max,
            range,
            latest: values[values.length - 1],
            trend,
            change: values.length > 1 ? values[values.length - 1] - values[0] : 0
        }
    }, [data])

    // Draw chart
    useEffect(() => {
        if (!canvasRef.current || !chartData) return

        const canvas = canvasRef.current
        const ctx = canvas.getContext('2d')
        const dpr = window.devicePixelRatio || 1

        // Set canvas size
        const rect = canvas.getBoundingClientRect()
        canvas.width = rect.width * dpr
        canvas.height = rect.height * dpr
        ctx.scale(dpr, dpr)

        const width = rect.width
        const height = rect.height
        const padding = { top: 20, right: 10, bottom: 20, left: 10 }
        const chartWidth = width - padding.left - padding.right
        const chartHeight = height - padding.top - padding.bottom

        // Clear canvas
        ctx.clearRect(0, 0, width, height)

        // Extend range for thresholds
        let yMin = chartData.min
        let yMax = chartData.max
        if (thresholds) {
            if (thresholds.warning) yMin = Math.min(yMin, thresholds.warning * 0.9)
            if (thresholds.danger) yMax = Math.max(yMax, thresholds.danger * 1.1)
        }
        const yRange = yMax - yMin || 1

        // Draw threshold lines
        if (thresholds) {
            if (thresholds.warning) {
                const y = padding.top + chartHeight - ((thresholds.warning - yMin) / yRange) * chartHeight
                ctx.strokeStyle = 'rgba(245, 158, 11, 0.3)'
                ctx.lineWidth = 1
                ctx.setLineDash([5, 5])
                ctx.beginPath()
                ctx.moveTo(padding.left, y)
                ctx.lineTo(width - padding.right, y)
                ctx.stroke()
            }

            if (thresholds.danger) {
                const y = padding.top + chartHeight - ((thresholds.danger - yMin) / yRange) * chartHeight
                ctx.strokeStyle = 'rgba(239, 68, 68, 0.3)'
                ctx.lineWidth = 1
                ctx.setLineDash([5, 5])
                ctx.beginPath()
                ctx.moveTo(padding.left, y)
                ctx.lineTo(width - padding.right, y)
                ctx.stroke()
            }
        }

        // Reset line dash
        ctx.setLineDash([])

        // Draw gradient fill
        const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom)
        gradient.addColorStop(0, 'rgba(8, 145, 178, 0.3)')
        gradient.addColorStop(1, 'rgba(8, 145, 178, 0)')

        ctx.beginPath()
        ctx.moveTo(padding.left, height - padding.bottom)

        chartData.values.forEach((value, i) => {
            const x = padding.left + (i / (chartData.values.length - 1)) * chartWidth
            const y = padding.top + chartHeight - ((value - yMin) / yRange) * chartHeight

            if (i === 0) {
                ctx.lineTo(x, y)
            } else {
                ctx.lineTo(x, y)
            }
        })

        ctx.lineTo(width - padding.right, height - padding.bottom)
        ctx.closePath()
        ctx.fillStyle = gradient
        ctx.fill()

        // Draw line
        ctx.beginPath()
        chartData.values.forEach((value, i) => {
            const x = padding.left + (i / (chartData.values.length - 1)) * chartWidth
            const y = padding.top + chartHeight - ((value - yMin) / yRange) * chartHeight

            if (i === 0) {
                ctx.moveTo(x, y)
            } else {
                ctx.lineTo(x, y)
            }
        })

        ctx.strokeStyle = (color && color.includes('var(')) ? '#0891b2' : (color || '#0891b2')
        ctx.lineWidth = 2
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'
        ctx.stroke()

        // Draw points
        chartData.values.forEach((value, i) => {
            const x = padding.left + (i / (chartData.values.length - 1)) * chartWidth
            const y = padding.top + chartHeight - ((value - yMin) / yRange) * chartHeight

            ctx.beginPath()
            ctx.arc(x, y, 4, 0, Math.PI * 2)
            ctx.fillStyle = '#1e293b'
            ctx.fill()
            ctx.strokeStyle = (color && color.includes('var(')) ? '#0891b2' : (color || '#0891b2')
            ctx.lineWidth = 2
            ctx.stroke()
        })

    }, [chartData, thresholds, color, height, minimal])

    if (!chartData) {
        if (minimal) {
            return <div style={{ height: height, background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)' }} />
        }
        return (
            <div className="trend-chart card">
                <h4 className="chart-title">{title}</h4>
                <div className="empty-chart">
                    <p className="text-muted text-sm">Not enough data to display trend</p>
                </div>
            </div>
        )
    }

    const getTrendIcon = () => {
        switch (chartData.trend) {
            case 'increasing': return <TrendingUp size={16} />
            case 'decreasing': return <TrendingDown size={16} />
            default: return <Minus size={16} />
        }
    }

    const getTrendColor = () => {
        // For metrics where lower is better (like A1C, LDL)
        if (chartData.trend === 'increasing') return 'var(--color-danger-light)'
        if (chartData.trend === 'decreasing') return 'var(--color-success-light)'
        return 'var(--text-muted)'
    }

    // Minimal mode - just return the canvas
    if (minimal) {
        return (
            <div style={{ height: height }}>
                <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
            </div>
        )
    }

    return (
        <div className="trend-chart card">
            <div className="chart-header">
                <h4 className="chart-title">{title}</h4>
                <div className="chart-meta">
                    <span className="current-value">
                        {chartData.latest?.toFixed(1)} {unit}
                    </span>
                    <span className="trend-indicator" style={{ color: getTrendColor() }}>
                        {getTrendIcon()}
                        <span>{chartData.change > 0 ? '+' : ''}{chartData.change.toFixed(1)}</span>
                    </span>
                </div>
            </div>

            <div className="chart-container" style={{ height: height }}>
                <canvas ref={canvasRef} className="chart-canvas" />
            </div>

            <div className="chart-footer">
                <span className="chart-range">
                    Range: {chartData.min.toFixed(1)} - {chartData.max.toFixed(1)} {unit}
                </span>
                <span className="chart-count">{chartData.values.length} readings</span>
            </div>

            <style>{`
        .trend-chart {
          padding: var(--space-md);
        }
        
        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: var(--space-md);
        }
        
        .chart-title {
          font-size: 0.9rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }
        
        .chart-meta {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 2px;
        }
        
        .current-value {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        
        .trend-indicator {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .chart-container {
          height: 150px;
          margin-bottom: var(--space-sm);
        }
        
        .chart-canvas {
          width: 100%;
          height: 100%;
        }
        
        .chart-footer {
          display: flex;
          justify-content: space-between;
          padding-top: var(--space-sm);
          border-top: 1px solid var(--border-color);
        }
        
        .chart-range,
        .chart-count {
          font-size: 0.7rem;
          color: var(--text-muted);
        }
        
        .empty-chart {
          height: 150px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      `}</style>
        </div>
    )
}

export default TrendChart
