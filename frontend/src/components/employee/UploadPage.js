import React, { useState, useRef } from 'react';
import { employeeAPI } from '../../services/api';

function UploadPage() {
    const [dragOver, setDragOver] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const fileRef = useRef(null);

    const handleUpload = async (file) => {
        if (!file || !file.name.endsWith('.csv')) {
            setError('Please select a valid CSV file');
            return;
        }

        setUploading(true);
        setError('');
        setResult(null);

        try {
            const res = await employeeAPI.uploadCSV(file);
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed. Make sure the AI service is running.');
        } finally {
            setUploading(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        handleUpload(file);
    };

    const sampleHeaders = 'employee_code,first_name,last_name,email,phone,company,department,position,hourly_wage,base_salary,date_of_joining,shift_type,weekly_hours,overtime_hours_3m,night_shifts_count_3m,performance_score,absenteeism_rate,tenure_months,attrition_risk,skills,city';

    return (
        <div className="animate-fade-up">
            <div className="page-header">
                <div>
                    <h1 className="page-title">📤 Upload Employee Data</h1>
                    <p className="page-subtitle">Import employee CSV files to add workforce data</p>
                </div>
            </div>

            {/* Upload Zone */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div
                    className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                    onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={handleDrop}
                    onClick={() => fileRef.current?.click()}
                >
                    {uploading ? (
                        <>
                            <div className="loading-spinner" style={{ margin: '0 auto 16px' }} />
                            <div className="upload-text">Uploading & Processing...</div>
                            <div className="upload-hint">This may take a moment for large files</div>
                        </>
                    ) : (
                        <>
                            <div className="upload-icon">📁</div>
                            <div className="upload-text">
                                Drag & drop your CSV file here, or <span style={{ color: 'var(--accent-primary)' }}>click to browse</span>
                            </div>
                            <div className="upload-hint">Supports .csv files with employee data</div>
                        </>
                    )}
                    <input
                        ref={fileRef}
                        type="file"
                        accept=".csv"
                        style={{ display: 'none' }}
                        onChange={(e) => handleUpload(e.target.files[0])}
                    />
                </div>
            </div>

            {/* Result */}
            {result && (
                <div className="card animate-fade-up" style={{
                    marginBottom: '24px',
                    borderLeft: '3px solid var(--success)',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                        <span style={{ fontSize: '28px' }}>✅</span>
                        <div>
                            <h3 style={{ fontSize: '18px', fontWeight: '700' }}>{result.message}</h3>
                            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                                Total employees in system: {result.total_employees}
                            </p>
                        </div>
                    </div>

                    <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
                        <div style={{ padding: '12px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                            <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--success)' }}>{result.loaded}</div>
                            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Records Imported</div>
                        </div>
                        <div style={{ padding: '12px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                            <div style={{ fontSize: '24px', fontWeight: '800', color: result.errors?.length > 0 ? 'var(--warning)' : 'var(--success)' }}>
                                {result.errors?.length || 0}
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Errors</div>
                        </div>
                        <div style={{ padding: '12px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                            <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--accent-primary)' }}>{result.total_employees}</div>
                            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Total in System</div>
                        </div>
                    </div>

                    {result.errors?.length > 0 && (
                        <div style={{ marginTop: '16px' }}>
                            <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--warning)', marginBottom: '8px' }}>⚠️ Errors:</div>
                            {result.errors.map((e, i) => (
                                <div key={i} style={{
                                    fontSize: '12px', color: 'var(--text-muted)',
                                    padding: '6px 10px', background: 'var(--bg-primary)',
                                    borderRadius: '4px', marginBottom: '4px',
                                    fontFamily: "'JetBrains Mono', monospace",
                                }}>{e}</div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="card animate-fade-up" style={{
                    marginBottom: '24px',
                    borderLeft: '3px solid var(--danger)',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '24px' }}>❌</span>
                        <div>
                            <div style={{ fontWeight: '600', color: 'var(--danger)' }}>Upload Failed</div>
                            <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{error}</div>
                        </div>
                    </div>
                </div>
            )}

            {/* CSV Format Guide */}
            <div className="card">
                <h3 style={{ fontSize: '16px', marginBottom: '16px' }}>📋 CSV Format Guide</h3>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                    Your CSV file should include the following headers. The system will auto-detect column names.
                </p>

                <div style={{
                    background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)',
                    padding: '16px', fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '11px', color: 'var(--text-muted)', overflowX: 'auto',
                    border: '1px solid var(--border-subtle)',
                }}>
                    <div style={{ color: 'var(--accent-tertiary)', marginBottom: '8px' }}>// Required headers:</div>
                    <div style={{ wordBreak: 'break-all', lineHeight: '1.8' }}>
                        {sampleHeaders.split(',').map((h, i) => (
                            <span key={h}>
                                <span style={{ color: '#fbbf24' }}>{h}</span>
                                {i < sampleHeaders.split(',').length - 1 && <span style={{ color: 'var(--text-muted)' }}>, </span>}
                            </span>
                        ))}
                    </div>
                </div>

                <div style={{ marginTop: '20px' }}>
                    <h4 style={{ fontSize: '13px', fontWeight: '600', marginBottom: '10px' }}>Key Fields:</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                        {[
                            ['shift_type', 'MORNING, AFTERNOON, NIGHT, ROTATING'],
                            ['attrition_risk', 'HIGH, MEDIUM, LOW'],
                            ['weekly_hours', 'Number (e.g., 48)'],
                            ['overtime_hours_3m', 'Hours in last 3 months'],
                            ['performance_score', '0-100 scale'],
                            ['absenteeism_rate', 'Percentage (e.g., 5.5)'],
                        ].map(([field, desc]) => (
                            <div key={field} style={{
                                padding: '8px 12px', background: 'var(--bg-secondary)', borderRadius: '6px',
                                display: 'flex', gap: '8px', alignItems: 'baseline',
                            }}>
                                <code style={{ fontSize: '11px', color: 'var(--accent-primary)', fontFamily: "'JetBrains Mono', monospace" }}>{field}</code>
                                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>— {desc}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div style={{ marginTop: '20px', padding: '14px', background: 'rgba(99,102,241,0.06)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(99,102,241,0.1)' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--accent-tertiary)', marginBottom: '4px' }}>💡 Tip</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        Check the <code style={{ fontFamily: "'JetBrains Mono'", color: 'var(--accent-primary)' }}>sample_data/</code> folder for example CSVs from Swiggy, Zomato, Amazon India, and more.
                        Pre-loaded datasets are already available when the AI service starts.
                    </div>
                </div>
            </div>
        </div>
    );
}

export default UploadPage;
