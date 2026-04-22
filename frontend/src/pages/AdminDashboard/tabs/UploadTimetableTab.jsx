import React, { useRef, useState, useEffect } from 'react';
import { uploadTimetable } from '../../../services/api';

export default function UploadTimetableTab({ showToast }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [isUploadedSuccessfully, setIsUploadedSuccessfully] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const fileInputRef = useRef(null);

  // Check if timetable was previously uploaded (from localStorage)
  useEffect(() => {
    const uploadedStatus = localStorage.getItem('timetable_uploaded');
    if (uploadedStatus === 'true') {
      setIsUploadedSuccessfully(true);
    }
  }, []);

  const validateFile = (candidate) => {
    if (!candidate) return false;
    if (!candidate.name.toLowerCase().endsWith('.csv')) {
      showToast('Please select a CSV file', 'warning');
      return false;
    }
    return true;
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (validateFile(selectedFile)) {
      setFile(selectedFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files[0];
    if (validateFile(droppedFile)) {
      setFile(droppedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      showToast('Please select a CSV file', 'warning');
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const formDataObj = new FormData();
      formDataObj.append('file', file);

      const response = await uploadTimetable(formDataObj);
      showToast('Timetable uploaded successfully!', 'success');
      setResult({ success: true, data: response.data });
      setIsUploadedSuccessfully(true);
      localStorage.setItem('timetable_uploaded', 'true');
      setFile(null);
      setShowUploadForm(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      showToast(err.response?.data?.detail || 'Upload failed', 'error');
      setResult({ success: false, error: err.response?.data?.detail || 'Upload failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {!isUploadedSuccessfully && !showUploadForm && (
        <div
          style={{
            padding: '24px',
            borderRadius: 'var(--border-radius-md)',
            background: 'var(--color-info-light)',
            border: '1px solid var(--color-info)',
            textAlign: 'center',
          }}
        >
          <p style={{ color: 'var(--color-info)', fontSize: '16px', fontWeight: 500, margin: 0 }}>
            Click to upload your timetable
          </p>
          <button
            onClick={() => setShowUploadForm(true)}
            style={{
              marginTop: '16px',
              padding: '10px 20px',
              background: 'var(--color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--border-radius-sm)',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '14px',
              transition: 'var(--transition)',
            }}
          >
            Upload Now
          </button>
        </div>
      )}

      {isUploadedSuccessfully && !showUploadForm && (
        <div
          style={{
            padding: '24px',
            borderRadius: 'var(--border-radius-md)',
            background: 'var(--color-success-light)',
            border: '1px solid var(--color-success)',
          }}
        >
          <p style={{ color: '#166534', fontSize: '16px', fontWeight: 500, margin: '0 0 12px 0' }}>
            ✓ Your timetable has been uploaded
          </p>
          <button
            onClick={() => setShowUploadForm(true)}
            style={{
              padding: '10px 16px',
              background: 'transparent',
              color: 'var(--color-primary)',
              border: '1px solid var(--color-primary)',
              borderRadius: 'var(--border-radius-sm)',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '14px',
              transition: 'var(--transition)',
            }}
          >
            Want to reload? Click here
          </button>
        </div>
      )}

      {showUploadForm && (
        <>
          <p style={{ marginBottom: '24px', color: 'var(--color-text-muted)', fontSize: '14px' }}>
            Upload the weekly timetable in CSV format. It stays stored even after logout.
          </p>

          <div
            style={{
              background: 'var(--color-white)',
              padding: '24px',
              borderRadius: 'var(--border-radius-md)',
              boxShadow: 'var(--shadow-sm)',
              marginBottom: '24px',
            }}
          >
            <form onSubmit={handleSubmit}>
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                style={{
                  marginTop: '8px',
                  padding: '40px 20px',
                  border: '2px dashed var(--color-border)',
                  borderRadius: 'var(--border-radius-md)',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'var(--transition)',
                  background: file ? 'var(--color-info-light)' : 'var(--color-bg)',
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
                {file ? (
                  <p style={{ color: 'var(--color-info)', fontWeight: 500 }}>{file.name}</p>
                ) : (
                  <>
                    <p style={{ marginBottom: '8px', color: 'var(--color-text)' }}>
                      Drop CSV file here or click to browse
                    </p>
                    <p style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>.csv</p>
                  </>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  marginTop: '24px',
                  width: '100%',
                  padding: '12px',
                  background: 'var(--color-primary)',
                  color: 'white',
                  border: 'none',
                  borderRadius: 'var(--border-radius-sm)',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontSize: '14px',
                  transition: 'var(--transition)',
                }}
              >
                {loading ? 'Uploading...' : 'Upload Timetable'}
              </button>
            </form>
          </div>

          {result && (
            <div
              style={{
                padding: '16px',
                borderRadius: 'var(--border-radius-md)',
                background: result.success ? 'var(--color-success-light)' : 'var(--color-error-light)',
                color: result.success ? '#166534' : '#991b1b',
                border: `1px solid ${result.success ? 'var(--color-success)' : 'var(--color-error)'}`,
                fontSize: '14px',
              }}
            >
              {result.success ? <p>Upload successful. Timetable has been processed.</p> : <p>{result.error}</p>}
            </div>
          )}
        </>
      )}
    </div>
  );
}
