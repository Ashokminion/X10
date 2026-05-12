import React, { useState, useEffect } from 'react';
import { employeeAPI, companyAPI } from '../../services/api';

function EmployeeList() {
    const [employees, setEmployees] = useState([]);
    const [companies, setCompanies] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [companyFilter, setCompanyFilter] = useState('');
    const [riskFilter, setRiskFilter] = useState('');
    const [page, setPage] = useState(1);
    const [selectedEmployee, setSelectedEmployee] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [isAdding, setIsAdding] = useState(false);
    const [formData, setFormData] = useState({});

    useEffect(() => {
        loadCompanies();
    }, []);

    useEffect(() => {
        loadEmployees();
    }, [search, companyFilter, riskFilter, page]);

    const loadCompanies = async () => {
        try {
            const res = await companyAPI.getAll();
            setCompanies(res.data.companies || []);
        } catch (e) { console.error(e); }
    };

    const loadEmployees = async () => {
        setLoading(true);
        try {
            const params = { page, limit: 30 };
            if (search) params.search = search;
            if (companyFilter) params.company = companyFilter;
            if (riskFilter) params.risk = riskFilter;
            const res = await employeeAPI.getAll(params);
            setEmployees(res.data.employees || []);
            setTotal(res.data.total || 0);
        } catch (err) {
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (code) => {
        if (!window.confirm(`Are you sure you want to delete employee ${code}?`)) return;
        try {
            await employeeAPI.delete(code);
            setSelectedEmployee(null);
            loadEmployees();
        } catch (err) {
            alert('Failed to delete employee: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            if (isAdding) {
                await employeeAPI.create(formData);
            } else {
                await employeeAPI.update(formData.employee_code, formData);
            }
            setIsEditing(false);
            setIsAdding(false);
            setSelectedEmployee(null);
            loadEmployees();
        } catch (err) {
            alert('Failed to save employee: ' + (err.response?.data?.detail || err.message));
        }
    };

    const openEdit = (emp) => {
        setFormData(emp);
        setIsEditing(true);
        setIsAdding(false);
    };

    const openAdd = () => {
        setFormData({
            employee_code: 'EMP' + Math.floor(1000 + Math.random() * 9000),
            first_name: '',
            last_name: '',
            email: '',
            phone: '',
            company: companyFilter || companies[0]?.company || 'Swiggy',
            department: 'Operations',
            position: 'Associate',
            hourly_wage: 150,
            base_salary: 25000,
            date_of_joining: new Date().toISOString().split('T')[0],
            shift_type: 'MORNING',
            weekly_hours: 48,
            overtime_hours_3m: 0,
            night_shifts_count_3m: 0,
            performance_score: 70,
            absenteeism_rate: 0,
            tenure_months: 12,
            attrition_risk: 'LOW',
            skills: '',
            city: ''
        });
        setIsAdding(true);
        setIsEditing(true);
        setSelectedEmployee({ full_name: 'New Employee' }); // Placeholder to trigger modal
    };

    const getRiskBadge = (risk) => {
        const r = (risk || 'LOW').toUpperCase();
        return <span className={`badge badge-${r.toLowerCase()}`}>● {r}</span>;
    };

    const companyColors = {
        'Swiggy': '#FC8019', 'Zomato': '#E23744', 'Blinkit': '#F8CB46',
        'Zepto': '#8B5CF6', 'Amazon India': '#FF9900', 'Flipkart': '#2974F0',
        'Larsen & Toubro': '#003B73',
    };

    return (
        <div className="animate-fade-up">
            <div className="page-header">
                <div>
                    <h1 className="page-title">👥 Employee Management</h1>
                    <p className="page-subtitle">{total} employees across all companies</p>
                </div>
                <button className="btn btn-primary" onClick={openAdd}>
                    <span style={{ marginRight: '8px' }}>➕</span> Add Employee
                </button>
            </div>

            {/* Filters */}
            <div className="filter-bar">
                <div className="search-box" style={{ flex: 1, maxWidth: '320px' }}>
                    <span className="search-icon">🔍</span>
                    <input
                        className="input"
                        placeholder="Search by name, code, email, city..."
                        value={search}
                        onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                    />
                </div>

                <select className="select" value={companyFilter}
                    onChange={(e) => { setCompanyFilter(e.target.value); setPage(1); }}>
                    <option value="">All Companies</option>
                    {companies.map(c => (
                        <option key={c.company} value={c.company}>{c.icon} {c.company}</option>
                    ))}
                </select>

                <div style={{ display: 'flex', gap: '6px' }}>
                    {['', 'HIGH', 'MEDIUM', 'LOW'].map(r => (
                        <button key={r}
                            className={`filter-chip ${riskFilter === r ? 'active' : ''}`}
                            onClick={() => { setRiskFilter(r); setPage(1); }}>
                            {r === '' ? 'All Risk' : r === 'HIGH' ? '🔴 High' : r === 'MEDIUM' ? '🟡 Medium' : '🟢 Low'}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                {loading ? (
                    <div className="loading-screen" style={{ minHeight: '300px' }}>
                        <div className="loading-spinner" />
                    </div>
                ) : employees.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">📭</div>
                        <div className="empty-title">No employees found</div>
                        <div className="empty-text">Try adjusting your filters or upload employee data</div>
                    </div>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Employee</th>
                                    <th>Company</th>
                                    <th>Department</th>
                                    <th>Position</th>
                                    <th>Shift</th>
                                    <th>Weekly Hrs</th>
                                    <th>Overtime (3M)</th>
                                    <th>Performance</th>
                                    <th>Absent %</th>
                                    <th>Risk</th>
                                    <th>City</th>
                                </tr>
                            </thead>
                            <tbody>
                                {employees.map((emp) => (
                                    <tr key={emp.employee_code}
                                        onClick={() => setSelectedEmployee(emp)}
                                        style={{ cursor: 'pointer' }}>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                <div style={{
                                                    width: '32px', height: '32px', borderRadius: '8px',
                                                    background: `${companyColors[emp.company] || '#6366f1'}22`,
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    fontSize: '12px', fontWeight: '700',
                                                    color: companyColors[emp.company] || '#6366f1',
                                                }}>
                                                    {emp.first_name?.charAt(0)}{emp.last_name?.charAt(0)}
                                                </div>
                                                <div>
                                                    <div style={{ fontWeight: '600', color: 'var(--text-primary)', fontSize: '13px' }}>
                                                        {emp.full_name}
                                                    </div>
                                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
                                                        {emp.employee_code}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <span style={{
                                                display: 'inline-flex', alignItems: 'center', gap: '4px',
                                                padding: '3px 8px', borderRadius: '6px',
                                                background: `${companyColors[emp.company] || '#666'}15`,
                                                color: companyColors[emp.company] || '#666',
                                                fontSize: '11px', fontWeight: '600',
                                            }}>
                                                {emp.company}
                                            </span>
                                        </td>
                                        <td>{emp.department}</td>
                                        <td style={{ fontSize: '12px' }}>{emp.position}</td>
                                        <td>
                                            <span style={{
                                                padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '600',
                                                background: emp.shift_type === 'NIGHT' ? 'rgba(99,102,241,0.1)' :
                                                    emp.shift_type === 'ROTATING' ? 'rgba(245,158,11,0.1)' : 'rgba(16,185,129,0.1)',
                                                color: emp.shift_type === 'NIGHT' ? '#818cf8' :
                                                    emp.shift_type === 'ROTATING' ? '#fbbf24' : '#34d399',
                                            }}>
                                                {emp.shift_type}
                                            </span>
                                        </td>
                                        <td style={{ color: emp.weekly_hours > 52 ? 'var(--danger)' : 'var(--text-secondary)', fontWeight: emp.weekly_hours > 52 ? '700' : '400' }}>
                                            {emp.weekly_hours}h
                                        </td>
                                        <td style={{ color: emp.overtime_hours_3m > 40 ? 'var(--danger)' : 'var(--text-secondary)' }}>
                                            {emp.overtime_hours_3m}h
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                <div style={{ width: '40px', height: '4px', background: 'rgba(255,255,255,0.06)', borderRadius: '2px' }}>
                                                    <div style={{
                                                        height: '100%', borderRadius: '2px',
                                                        width: `${emp.performance_score}%`,
                                                        background: emp.performance_score >= 75 ? 'var(--success)' : emp.performance_score >= 55 ? 'var(--warning)' : 'var(--danger)',
                                                    }} />
                                                </div>
                                                <span style={{ fontSize: '12px' }}>{emp.performance_score}</span>
                                            </div>
                                        </td>
                                        <td style={{ color: emp.absenteeism_rate > 10 ? 'var(--danger)' : 'var(--text-secondary)' }}>
                                            {emp.absenteeism_rate}%
                                        </td>
                                        <td>{getRiskBadge(emp.attrition_risk)}</td>
                                        <td style={{ fontSize: '12px' }}>{emp.city}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Pagination */}
            {total > 30 && (
                <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '20px' }}>
                    <button className="btn btn-secondary btn-sm" disabled={page <= 1}
                        onClick={() => setPage(p => p - 1)}>← Prev</button>
                    <span style={{ display: 'flex', alignItems: 'center', padding: '0 12px', fontSize: '13px', color: 'var(--text-muted)' }}>
                        Page {page} of {Math.ceil(total / 30)}
                    </span>
                    <button className="btn btn-secondary btn-sm" disabled={page >= Math.ceil(total / 30)}
                        onClick={() => setPage(p => p + 1)}>Next →</button>
                </div>
            )}

            {/* Employee Detail / Edit Modal */}
            {selectedEmployee && (
                <div className="modal-overlay" onClick={() => {
                    setSelectedEmployee(null);
                    setIsEditing(false);
                    setIsAdding(false);
                }}>
                    <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px' }}>
                        <div className="modal-header">
                            <div>
                                <div className="modal-title">
                                    {isAdding ? 'Add New Employee' : (isEditing ? `Edit: ${selectedEmployee.full_name}` : selectedEmployee.full_name)}
                                </div>
                                {!isAdding && (
                                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
                                        {selectedEmployee.employee_code} • {selectedEmployee.company}
                                    </div>
                                )}
                            </div>
                            <button className="modal-close" onClick={() => {
                                setSelectedEmployee(null);
                                setIsEditing(false);
                                setIsAdding(false);
                            }}>×</button>
                        </div>
                        <div className="modal-body">
                            {isEditing ? (
                                <form onSubmit={handleSave}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                                        <div className="form-group">
                                            <label className="label">Employee Code</label>
                                            <input className="input" value={formData.employee_code} disabled={!isAdding}
                                                onChange={e => setFormData({ ...formData, employee_code: e.target.value })} required />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">First Name</label>
                                            <input className="input" value={formData.first_name}
                                                onChange={e => setFormData({ ...formData, first_name: e.target.value })} required />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Last Name</label>
                                            <input className="input" value={formData.last_name}
                                                onChange={e => setFormData({ ...formData, last_name: e.target.value })} required />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Email</label>
                                            <input className="input" type="email" value={formData.email}
                                                onChange={e => setFormData({ ...formData, email: e.target.value })} required />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Phone</label>
                                            <input className="input" value={formData.phone}
                                                onChange={e => setFormData({ ...formData, phone: e.target.value })} />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Company</label>
                                            <select className="select" value={formData.company}
                                                onChange={e => setFormData({ ...formData, company: e.target.value })}>
                                                {companies.map(c => <option key={c.company} value={c.company}>{c.company}</option>)}
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Department</label>
                                            <input className="input" value={formData.department}
                                                onChange={e => setFormData({ ...formData, department: e.target.value })} required />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Position</label>
                                            <input className="input" value={formData.position}
                                                onChange={e => setFormData({ ...formData, position: e.target.value })} required />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">City</label>
                                            <input className="input" value={formData.city}
                                                onChange={e => setFormData({ ...formData, city: e.target.value })} />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Hourly Wage (₹)</label>
                                            <input className="input" type="number" value={formData.hourly_wage}
                                                onChange={e => setFormData({ ...formData, hourly_wage: parseFloat(e.target.value) })} />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Base Salary (₹)</label>
                                            <input className="input" type="number" value={formData.base_salary}
                                                onChange={e => setFormData({ ...formData, base_salary: parseFloat(e.target.value) })} />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Shift Type</label>
                                            <select className="select" value={formData.shift_type}
                                                onChange={e => setFormData({ ...formData, shift_type: e.target.value })}>
                                                <option value="MORNING">MORNING</option>
                                                <option value="AFTERNOON">AFTERNOON</option>
                                                <option value="NIGHT">NIGHT</option>
                                                <option value="ROTATING">ROTATING</option>
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Weekly Hours</label>
                                            <input className="input" type="number" value={formData.weekly_hours}
                                                onChange={e => setFormData({ ...formData, weekly_hours: parseFloat(e.target.value) })} />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Perf Score (0-100)</label>
                                            <input className="input" type="number" value={formData.performance_score}
                                                onChange={e => setFormData({ ...formData, performance_score: parseFloat(e.target.value) })} />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Attrition Risk</label>
                                            <select className="select" value={formData.attrition_risk}
                                                onChange={e => setFormData({ ...formData, attrition_risk: e.target.value })}>
                                                <option value="LOW">LOW</option>
                                                <option value="MEDIUM">MEDIUM</option>
                                                <option value="HIGH">HIGH</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="form-group" style={{ marginTop: '12px' }}>
                                        <label className="label">Skills (comma separated)</label>
                                        <input className="input" value={formData.skills}
                                            onChange={e => setFormData({ ...formData, skills: e.target.value })} />
                                    </div>
                                    <div className="modal-footer" style={{ marginTop: '20px', padding: 0, border: 0 }}>
                                        <button type="button" className="btn btn-secondary" onClick={() => {
                                            if (isAdding) setSelectedEmployee(null);
                                            setIsEditing(false);
                                            setIsAdding(false);
                                        }}>Cancel</button>
                                        <button type="submit" className="btn btn-primary">Save Changes</button>
                                    </div>
                                </form>
                            ) : (
                                <>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                        {[
                                            ['📧 Email', selectedEmployee.email],
                                            ['📱 Phone', selectedEmployee.phone],
                                            ['🏢 Department', selectedEmployee.department],
                                            ['💼 Position', selectedEmployee.position],
                                            ['📅 Joined', selectedEmployee.date_of_joining],
                                            ['🏙️ City', selectedEmployee.city],
                                            ['💰 Base Salary', `₹${selectedEmployee.base_salary?.toLocaleString()}`],
                                            ['⏱️ Hourly Wage', `₹${selectedEmployee.hourly_wage}`],
                                            ['📊 Shift Type', selectedEmployee.shift_type],
                                            ['🕐 Weekly Hours', `${selectedEmployee.weekly_hours}h`],
                                            ['📈 Overtime (3M)', `${selectedEmployee.overtime_hours_3m}h`],
                                            ['🌙 Night Shifts (3M)', selectedEmployee.night_shifts_count_3m],
                                            ['⭐ Performance', `${selectedEmployee.performance_score}/100`],
                                            ['🚫 Absenteeism', `${selectedEmployee.absenteeism_rate}%`],
                                            ['📆 Tenure', `${selectedEmployee.tenure_months} months`],
                                            ['⚠️ Attrition Risk', selectedEmployee.attrition_risk],
                                        ].map(([label, value]) => (
                                            <div key={label} style={{ padding: '10px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
                                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>{label}</div>
                                                <div style={{ fontSize: '14px', fontWeight: '600' }}>{value || 'N/A'}</div>
                                            </div>
                                        ))}
                                    </div>
                                    {selectedEmployee.skills && (
                                        <div style={{ marginTop: '16px' }}>
                                            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>🛠️ Skills</div>
                                            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                                                {selectedEmployee.skills.split(',').map(s => (
                                                    <span key={s} style={{
                                                        padding: '4px 10px', borderRadius: '6px',
                                                        background: 'rgba(99,102,241,0.1)', color: 'var(--accent-tertiary)',
                                                        fontSize: '12px', fontWeight: '500',
                                                    }}>{s.trim()}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    <div className="modal-footer" style={{ marginTop: '24px', padding: 0, border: 0, justifyContent: 'space-between' }}>
                                        <button className="btn btn-danger" onClick={() => handleDelete(selectedEmployee.employee_code)}>
                                            🗑️ Delete Employee
                                        </button>
                                        <button className="btn btn-primary" onClick={() => openEdit(selectedEmployee)}>
                                            ✏️ Edit Details
                                        </button>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default EmployeeList;
