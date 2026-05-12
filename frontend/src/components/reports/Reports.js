import React from 'react';

function Reports() {
    const reports = [
        { name: 'Workforce Attrition Analysis', desc: 'Comprehensive report on attrition risk across all 7 companies', icon: '📊', type: 'PDF', date: '2024-04-16' },
        { name: 'Shift Collapse Report', desc: 'Shift collapse scores and contributing factors by company', icon: '⚡', type: 'PDF', date: '2024-04-16' },
        { name: 'Company Comparison Matrix', desc: 'Side-by-side comparison of Swiggy, Zomato, Amazon, Flipkart, L&T', icon: '📋', type: 'PDF', date: '2024-04-16' },
        { name: 'Overtime & Compliance Report', desc: 'Labour law compliance check - weekly hours and rest period analysis', icon: '⏱️', type: 'PDF', date: '2024-04-15' },
        { name: 'Night Shift Impact Study', desc: 'Health and performance impact of night shifts on workforce', icon: '🌙', type: 'PDF', date: '2024-04-14' },
        { name: 'AI Optimization Results', desc: 'Cost savings from AI-optimized shift assignments', icon: '🤖', type: 'PDF', date: '2024-04-13' },
    ];

    return (
        <div className="animate-fade-up">
            <div className="page-header">
                <div>
                    <h1 className="page-title">📄 Reports & Analytics</h1>
                    <p className="page-subtitle">Generate AI-powered workforce intelligence reports</p>
                </div>
                <button className="btn btn-primary">📥 Generate New Report</button>
            </div>

            <div className="cards-grid">
                {reports.map((r, i) => (
                    <div key={i} className="card" style={{ cursor: 'pointer' }}>
                        <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                            <div style={{
                                width: '48px', height: '48px', borderRadius: 'var(--radius-sm)',
                                background: 'rgba(99,102,241,0.08)', display: 'flex',
                                alignItems: 'center', justifyContent: 'center', fontSize: '22px', flexShrink: 0,
                            }}>
                                {r.icon}
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: '600', fontSize: '14px', marginBottom: '4px' }}>{r.name}</div>
                                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>{r.desc}</div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{r.date}</span>
                                    <span className="badge badge-low">{r.type}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Reports;
