import React, { useState, useEffect } from 'react';
import { companyAPI } from '../../services/api';

function CompanyView() {
    const [companies, setCompanies] = useState([]);
    const [selectedCompany, setSelectedCompany] = useState(null);
    const [detail, setDetail] = useState(null);
    const [loading, setLoading] = useState(true);
    const [detailLoading, setDetailLoading] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [isAdding, setIsAdding] = useState(false);
    const [formData, setFormData] = useState({});

    useEffect(() => {
        loadCompanies();
    }, []);

    const loadCompanies = async () => {
        try {
            const res = await companyAPI.getAll();
            setCompanies(res.data.companies || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const loadDetail = async (companyName) => {
        setSelectedCompany(companyName);
        setDetailLoading(true);
        try {
            const res = await companyAPI.getDetail(companyName);
            setDetail(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setDetailLoading(false);
        }
    };

    const handleDelete = async (name) => {
        if (!window.confirm(`Are you sure you want to delete company ${name}? This will NOT delete employees but they will lose their company branding.`)) return;
        try {
            await companyAPI.delete(name);
            setSelectedCompany(null);
            setDetail(null);
            loadCompanies();
        } catch (err) {
            alert('Failed to delete company: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            if (isAdding) {
                await companyAPI.create(formData);
            } else {
                await companyAPI.update(selectedCompany, formData);
            }
            setIsEditing(false);
            setIsAdding(false);
            setSelectedCompany(null);
            loadCompanies();
        } catch (err) {
            alert('Failed to save company: ' + (err.response?.data?.detail || err.message));
        }
    };

    const openEdit = (c) => {
        setFormData({
            name: c.company,
            sector: c.sector,
            color: c.color,
            icon: c.icon,
            hq: c.hq || 'India'
        });
        setIsEditing(true);
        setIsAdding(false);
    };

    const openAdd = () => {
        setFormData({
            name: '',
            sector: 'Logistics',
            color: '#6366f1',
            icon: '🏢',
            hq: 'India'
        });
        setIsAdding(true);
        setIsEditing(true);
    };

    const getCollapseClass = (score) => score >= 60 ? 'high' : score >= 35 ? 'medium' : 'low';
    const getCollapseColor = (score) => score >= 60 ? 'var(--danger)' : score >= 35 ? 'var(--warning)' : 'var(--success)';

    if (loading) {
        return <div className="loading-screen"><div className="loading-spinner" /><div className="loading-text">Loading companies...</div></div>;
    }

    return (
        <div className="animate-fade-up">
            <div className="page-header">
                <div>
                    <h1 className="page-title">🏢 Company Analytics</h1>
                    <p className="page-subtitle">Shift collapse & attrition analysis across {companies.length} companies</p>
                </div>
                <button className="btn btn-primary" onClick={openAdd}>
                    <span style={{ marginRight: '8px' }}>➕</span> Add Company
                </button>
            </div>

            {/* Company Cards Grid */}
            <div className="cards-grid stagger-children" style={{ marginBottom: '24px' }}>
                {companies.map((c) => (
                    <div key={c.company}
                        className="company-card"
                        style={{ '--company-color': c.color, borderColor: selectedCompany === c.company ? c.color : undefined }}
                        onClick={() => loadDetail(c.company)}>
                        
                        <div className="company-header">
                            <div className="company-icon" style={{ background: `${c.color}15` }}>
                                {c.icon}
                            </div>
                            <div>
                                <div className="company-name">{c.company}</div>
                                <div className="company-sector">{c.sector}</div>
                            </div>
                            <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                                <div style={{ fontSize: '22px', fontWeight: '800', color: c.color }}>{c.total_employees}</div>
                                <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>EMPLOYEES</div>
                            </div>
                        </div>

                        <div className="company-metrics">
                            <div className="metric">
                                <div className="metric-value" style={{ color: 'var(--danger)' }}>{c.high_risk_count}</div>
                                <div className="metric-label">High Risk</div>
                            </div>
                            <div className="metric">
                                <div className="metric-value">{c.avg_weekly_hours}h</div>
                                <div className="metric-label">Avg Hrs/Week</div>
                            </div>
                            <div className="metric">
                                <div className="metric-value">{c.avg_overtime}h</div>
                                <div className="metric-label">Avg Overtime</div>
                            </div>
                            <div className="metric">
                                <div className="metric-value">{c.avg_absenteeism}%</div>
                                <div className="metric-label">Absenteeism</div>
                            </div>
                        </div>

                        <div className="collapse-meter">
                            <div className="collapse-header">
                                <span className="collapse-label">Shift Collapse Score</span>
                                <span className="collapse-value" style={{ color: getCollapseColor(c.shift_collapse_score) }}>
                                    {c.shift_collapse_score}/100
                                </span>
                            </div>
                            <div className="collapse-bar">
                                <div className={`collapse-fill ${getCollapseClass(c.shift_collapse_score)}`}
                                    style={{ width: `${c.shift_collapse_score}%` }} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Company Detail Panel */}
            {selectedCompany && (
                <div className="card animate-fade-up" style={{ marginBottom: '24px' }}>
                    {detailLoading ? (
                        <div className="loading-screen" style={{ minHeight: '200px' }}>
                            <div className="loading-spinner" />
                        </div>
                    ) : detail ? (
                        <>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                                <div>
                                    <h2 style={{ fontSize: '20px', fontWeight: '800' }}>
                                        {detail.icon} {detail.company} — Deep Analysis
                                    </h2>
                                    <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{detail.sector} • HQ: {detail.hq}</p>
                                </div>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(detail.company)}>🗑️ Delete</button>
                                    <button className="btn btn-primary btn-sm" onClick={() => openEdit(detail)}>✏️ Edit</button>
                                    <button className="btn btn-secondary btn-sm" onClick={() => { setSelectedCompany(null); setDetail(null); }}>
                                        ✕ Close
                                    </button>
                                </div>
                            </div>

                            {/* Risk Pie */}
                            <div className="three-col" style={{ marginBottom: '24px' }}>
                                <div style={{ padding: '16px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                                    <div style={{ fontSize: '32px', fontWeight: '800', color: 'var(--danger)' }}>{detail.high_risk_count}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>🔴 High Risk</div>
                                    <div style={{ fontSize: '11px', color: 'var(--danger)' }}>
                                        {Math.round(detail.high_risk_count / detail.total_employees * 100)}%
                                    </div>
                                </div>
                                <div style={{ padding: '16px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                                    <div style={{ fontSize: '32px', fontWeight: '800', color: 'var(--warning)' }}>{detail.medium_risk_count}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>🟡 Medium Risk</div>
                                    <div style={{ fontSize: '11px', color: 'var(--warning)' }}>
                                        {Math.round(detail.medium_risk_count / detail.total_employees * 100)}%
                                    </div>
                                </div>
                                <div style={{ padding: '16px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                                    <div style={{ fontSize: '32px', fontWeight: '800', color: 'var(--success)' }}>{detail.low_risk_count}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>🟢 Low Risk</div>
                                    <div style={{ fontSize: '11px', color: 'var(--success)' }}>
                                        {Math.round(detail.low_risk_count / detail.total_employees * 100)}%
                                    </div>
                                </div>
                            </div>

                            {/* Department & City */}
                            <div className="two-col">
                                <div>
                                    <h4 style={{ fontSize: '14px', marginBottom: '12px' }}>Department Breakdown</h4>
                                    {detail.departments && Object.entries(detail.departments).map(([dept, data]) => (
                                        <div key={dept} style={{
                                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                            padding: '10px 12px', background: 'var(--bg-secondary)',
                                            borderRadius: '6px', marginBottom: '6px',
                                        }}>
                                            <div>
                                                <div style={{ fontSize: '13px', fontWeight: '600' }}>{dept}</div>
                                                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{data.count} employees</div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                {data.high_risk > 0 && (
                                                    <span className="badge badge-high" style={{ fontSize: '10px' }}>{data.high_risk} at risk</span>
                                                )}
                                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                                                    OT: {data.avg_overtime}h
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div>
                                    <h4 style={{ fontSize: '14px', marginBottom: '12px' }}>City Distribution</h4>
                                    {detail.city_distribution && Object.entries(detail.city_distribution)
                                        .sort((a, b) => b[1] - a[1])
                                        .map(([city, count]) => (
                                            <div key={city} style={{
                                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                                padding: '10px 12px', background: 'var(--bg-secondary)',
                                                borderRadius: '6px', marginBottom: '6px',
                                            }}>
                                                <span style={{ fontSize: '13px', fontWeight: '500' }}>📍 {city}</span>
                                                <span style={{ fontSize: '13px', fontWeight: '700', color: detail.color }}>{count}</span>
                                            </div>
                                        ))}

                                    <h4 style={{ fontSize: '14px', marginBottom: '12px', marginTop: '20px' }}>Shift Distribution</h4>
                                    {detail.shift_distribution && Object.entries(detail.shift_distribution).map(([shift, count]) => (
                                        <div key={shift} style={{
                                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                            padding: '10px 12px', background: 'var(--bg-secondary)',
                                            borderRadius: '6px', marginBottom: '6px',
                                        }}>
                                            <span style={{ fontSize: '13px' }}>
                                                {shift === 'NIGHT' ? '🌙' : shift === 'MORNING' ? '☀️' : shift === 'ROTATING' ? '🔄' : '🌤️'} {shift}
                                            </span>
                                            <span style={{ fontSize: '13px', fontWeight: '700' }}>{count}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Employee Table */}
                            {detail.employees && (
                                <div style={{ marginTop: '24px' }}>
                                    <h4 style={{ fontSize: '14px', marginBottom: '12px' }}>All Employees</h4>
                                    <div style={{ overflowX: 'auto', maxHeight: '400px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                                        <table className="data-table">
                                            <thead>
                                                <tr>
                                                    <th>Code</th>
                                                    <th>Name</th>
                                                    <th>Position</th>
                                                    <th>Shift</th>
                                                    <th>Hrs/Week</th>
                                                    <th>OT (3M)</th>
                                                    <th>Perf</th>
                                                    <th>Risk</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {detail.employees.map(emp => (
                                                    <tr key={emp.employee_code}>
                                                        <td style={{ fontFamily: "'JetBrains Mono'", fontSize: '11px' }}>{emp.employee_code}</td>
                                                        <td style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{emp.full_name}</td>
                                                        <td>{emp.position}</td>
                                                        <td>{emp.shift_type}</td>
                                                        <td style={{ color: emp.weekly_hours > 52 ? 'var(--danger)' : 'inherit' }}>{emp.weekly_hours}h</td>
                                                        <td style={{ color: emp.overtime_hours_3m > 40 ? 'var(--danger)' : 'inherit' }}>{emp.overtime_hours_3m}h</td>
                                                        <td>{emp.performance_score}</td>
                                                        <td>
                                                            <span className={`badge badge-${emp.attrition_risk?.toLowerCase()}`}>
                                                                {emp.attrition_risk}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                        </>
                    ) : null}
                </div>
            )}

            {/* Company Form Modal */}
            {isEditing && (
                <div className="modal-overlay" onClick={() => { setIsEditing(false); setIsAdding(false); }}>
                    <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '500px' }}>
                        <div className="modal-header">
                            <div className="modal-title">{isAdding ? 'Add New Company' : `Edit: ${formData.name}`}</div>
                            <button className="modal-close" onClick={() => { setIsEditing(false); setIsAdding(false); }}>×</button>
                        </div>
                        <div className="modal-body">
                            <form onSubmit={handleSave}>
                                <div className="form-group" style={{ marginBottom: '12px' }}>
                                    <label className="label">Company Name</label>
                                    <input className="input" value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })} required />
                                </div>
                                <div className="form-group" style={{ marginBottom: '12px' }}>
                                    <label className="label">Sector</label>
                                    <input className="input" value={formData.sector}
                                        onChange={e => setFormData({ ...formData, sector: e.target.value })} required />
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                    <div className="form-group" style={{ marginBottom: '12px' }}>
                                        <label className="label">Icon (Emoji)</label>
                                        <input className="input" value={formData.icon}
                                            onChange={e => setFormData({ ...formData, icon: e.target.value })} required />
                                    </div>
                                    <div className="form-group" style={{ marginBottom: '12px' }}>
                                        <label className="label">Brand Color</label>
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <input type="color" className="input" style={{ width: '40px', padding: '2px' }} value={formData.color}
                                                onChange={e => setFormData({ ...formData, color: e.target.value })} />
                                            <input className="input" value={formData.color}
                                                onChange={e => setFormData({ ...formData, color: e.target.value })} required />
                                        </div>
                                    </div>
                                </div>
                                <div className="form-group" style={{ marginBottom: '12px' }}>
                                    <label className="label">Headquarters</label>
                                    <input className="input" value={formData.hq}
                                        onChange={e => setFormData({ ...formData, hq: e.target.value })} required />
                                </div>
                                <div className="modal-footer" style={{ marginTop: '20px', padding: 0, border: 0 }}>
                                    <button type="button" className="btn btn-secondary" onClick={() => { setIsEditing(false); setIsAdding(false); }}>Cancel</button>
                                    <button type="submit" className="btn btn-primary">Save Company</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default CompanyView;
