import { useState, useCallback } from 'react'
import { Upload, X, FileText, Image, Database, CheckCircle, AlertCircle } from 'lucide-react'

const API_BASE = '/api'

function FileUpload({ patientId, patientName, onClose, onUploadComplete }) {
  const [isDragging, setIsDragging] = useState(false)
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadResults, setUploadResults] = useState([])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFiles = Array.from(e.dataTransfer.files)
    setFiles(prev => [...prev, ...droppedFiles])
  }, [])

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files)
    setFiles(prev => [...prev, ...selectedFiles])
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase()
    if (['pdf', 'doc', 'docx', 'txt'].includes(ext)) return <FileText size={20} />
    if (['jpg', 'jpeg', 'png', 'dcm'].includes(ext)) return <Image size={20} />
    if (['csv', 'xlsx', 'xls', 'vcf'].includes(ext)) return <Database size={20} />
    return <FileText size={20} />
  }

  const uploadFiles = async () => {
    setUploading(true)
    setUploadResults([])

    const results = []

    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)

      try {
        const res = await fetch(`${API_BASE}/upload/${patientId}`, {
          method: 'POST',
          body: formData
        })
        const data = await res.json()

        results.push({
          filename: file.name,
          success: !data.error,
          message: data.error || 'Uploaded successfully',
          records: data.records_created
        })
      } catch (err) {
        results.push({
          filename: file.name,
          success: false,
          message: 'Upload failed'
        })
      }
    }

    setUploadResults(results)
    setUploading(false)

    // If all successful, notify parent
    if (results.every(r => r.success)) {
      setTimeout(() => {
        onUploadComplete()
      }, 1500)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Upload Health Data</h2>
          <span className="text-secondary text-sm">Patient: {patientName}</span>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* Drop Zone */}
          <div
            className={`drop-zone ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload size={48} className="drop-icon" />
            <p className="drop-text">Drag & drop files here</p>
            <p className="text-muted text-sm">or</p>
            <label className="btn btn-primary mt-sm">
              Browse Files
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                accept=".pdf,.csv,.xlsx,.xls,.vcf,.txt,.jpg,.jpeg,.png,.dcm"
                style={{ display: 'none' }}
              />
            </label>
            <p className="supported-formats">
              Supported: PDF, CSV, Excel, VCF, Images, DICOM
            </p>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="file-list">
              <h4>Selected Files ({files.length})</h4>
              {files.map((file, index) => (
                <div key={index} className="file-item">
                  <div className="file-icon">{getFileIcon(file.name)}</div>
                  <div className="file-info">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                  </div>
                  <button
                    className="remove-btn"
                    onClick={() => removeFile(index)}
                  >
                    <X size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Upload Results */}
          {uploadResults.length > 0 && (
            <div className="upload-results">
              <h4>Upload Results</h4>
              {uploadResults.map((result, index) => (
                <div key={index} className={`result-item ${result.success ? 'success' : 'error'}`}>
                  {result.success ? (
                    <CheckCircle size={18} className="text-success" />
                  ) : (
                    <AlertCircle size={18} className="text-danger" />
                  )}
                  <div className="result-info">
                    <span className="result-filename">{result.filename}</span>
                    <span className="result-message">{result.message}</span>
                    {result.records && (
                      <span className="result-records">
                        Labs: {result.records.labs} | Genomics: {result.records.genomics} |
                        Notes: {result.records.notes} | Imaging: {result.records.imaging}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={uploadFiles}
            disabled={files.length === 0 || uploading}
          >
            {uploading ? (
              <>
                <span className="spinner"></span>
                Uploading...
              </>
            ) : (
              `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`
            )}
          </button>
        </div>
      </div>

      <style>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: var(--space-lg);
        }
        
        .modal {
          background: var(--bg-secondary);
          border: 1px solid var(--border-color);
          border-radius: var(--radius-xl);
          width: 100%;
          max-width: 550px;
          max-height: 90vh;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          animation: scaleIn 0.2s ease;
        }
        
        .modal-header {
          padding: var(--space-lg);
          border-bottom: 1px solid var(--border-color);
          position: relative;
        }
        
        .modal-header h2 {
          margin: 0;
          font-size: 1.25rem;
        }
        
        .close-btn {
          position: absolute;
          top: var(--space-md);
          right: var(--space-md);
          background: transparent;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          padding: var(--space-xs);
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
        }
        
        .close-btn:hover {
          color: var(--text-primary);
          background: var(--bg-tertiary);
        }
        
        .modal-body {
          padding: var(--space-lg);
          overflow-y: auto;
          flex: 1;
        }
        
        .modal-footer {
          padding: var(--space-lg);
          border-top: 1px solid var(--border-color);
          display: flex;
          justify-content: flex-end;
          gap: var(--space-md);
        }
        
        .drop-zone {
          border: 2px dashed var(--border-color);
          border-radius: var(--radius-lg);
          padding: var(--space-2xl);
          text-align: center;
          transition: all var(--transition-fast);
        }
        
        .drop-zone.dragging {
          border-color: var(--color-primary);
          background: rgba(8, 145, 178, 0.1);
        }
        
        .drop-icon {
          color: var(--text-muted);
          margin-bottom: var(--space-md);
        }
        
        .drop-text {
          font-size: 1rem;
          font-weight: 500;
          color: var(--text-secondary);
          margin-bottom: var(--space-sm);
        }
        
        .supported-formats {
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-top: var(--space-md);
        }
        
        .file-list {
          margin-top: var(--space-lg);
        }
        
        .file-list h4 {
          font-size: 0.875rem;
          margin-bottom: var(--space-md);
          color: var(--text-secondary);
        }
        
        .file-item {
          display: flex;
          align-items: center;
          gap: var(--space-md);
          padding: var(--space-sm) var(--space-md);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
          margin-bottom: var(--space-sm);
        }
        
        .file-icon {
          color: var(--color-primary-light);
        }
        
        .file-info {
          flex: 1;
        }
        
        .file-name {
          display: block;
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-primary);
        }
        
        .file-size {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        
        .remove-btn {
          background: transparent;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          padding: var(--space-xs);
          border-radius: var(--radius-sm);
        }
        
        .remove-btn:hover {
          color: var(--color-danger);
          background: var(--color-danger-bg);
        }
        
        .upload-results {
          margin-top: var(--space-lg);
        }
        
        .upload-results h4 {
          font-size: 0.875rem;
          margin-bottom: var(--space-md);
          color: var(--text-secondary);
        }
        
        .result-item {
          display: flex;
          align-items: flex-start;
          gap: var(--space-md);
          padding: var(--space-md);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
          margin-bottom: var(--space-sm);
        }
        
        .result-item.success {
          border-left: 3px solid var(--color-success);
        }
        
        .result-item.error {
          border-left: 3px solid var(--color-danger);
        }
        
        .result-info {
          flex: 1;
        }
        
        .result-filename {
          display: block;
          font-weight: 500;
          color: var(--text-primary);
          font-size: 0.875rem;
        }
        
        .result-message {
          display: block;
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
        
        .result-records {
          display: block;
          font-size: 0.7rem;
          color: var(--text-muted);
          margin-top: var(--space-xs);
        }
      `}</style>
    </div>
  )
}

export default FileUpload
