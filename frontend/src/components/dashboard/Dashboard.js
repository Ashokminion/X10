import React, { useState, useEffect } from 'react';
import { dashboardAPI, companyAPI } from '../../services/api';

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [comparison, setComparison] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [statsRes, compRes] = await Promise.all([
                dashboardAPI.getStats(),
                companyAPI.compareAll(),
            ]);
            setStats(statsRes.data);
            setComparison(compRes.data.comparison || []);
        } catch (err) {
            console.error('Dashboard load error:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-screen">
                <div className="loading-spinner" />
                <div className="loading-text">Loading intelligence data...</div>
            </div>
        );
    }

    if (!stats) {
        return (
            <div className="empty-state">
                <div className="empty-icon">⚠️</div>
                <div className="empty-title">Cannot connect to AI Service</div>
                <div className="empty-text">Make sure the AI service is running on port 8000</div>
            </div>
        );
    }

    const getCollapseColor = (score) => {
        if (score >= 60) return 'var(--danger)';
        if (score >= 35) return 'var(--warning)';
        return 'var(--success)';
    };

    const getCollapseLevel = (score) => {
        if (score >= 60) return 'CRITICAL';
        if (score >= 35) return 'WARNING';
        return 'HEALTHY';
    };

    return (
        <div className="animate-fade-up">
            <div className="page-header">
                <div>
                    <h1 className="page-title">
                        <span className="text-gradient">Intelligence Dashboard</span>
                    </h1>
                    <p className="page-subtitle">
                        Real-time workforce analytics across {stats.total_companies} companies • {stats.total_employees} employees
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span style={{
                        display: 'flex', alignItems: 'center', gap: '6px',
                        padding: '8px 14px', borderRadius: '20px',
                        background: 'var(--success-glow)', border: '1px solid rgba(16,185,129,0.2)',
                        fontSize: '12px', fontWeight: '600', color: 'var(--success)',
                    }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)', animation: 'pulse-glow 2s infinite' }} />
                        AI Service Online
                    </span>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="stats-grid stagger-children">
                <div className="stat-card">
                    <div className="stat-icon purple">👥</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.total_employees}</div>
                        <div className="stat-label">Total Employees</div>
                        <div className="stat-change">{stats.total_companies} Companies</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon red">🔴</div>
                    <div className="stat-content">
                        <div className="stat-value" style={{ color: 'var(--danger)' }}>{stats.high_risk_employees}</div>
                        <div className="stat-label">High Risk Attrition</div>
                        <div className="stat-change up">
                            {Math.round(stats.high_risk_employees / stats.total_employees * 100)}% of workforce
                        </div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon orange">⚡</div>
                    <div className="stat-content">
                        <div className="stat-value" style={{ color: getCollapseColor(stats.overall_shift_collapse_score) }}>
                            {stats.overall_shift_collapse_score}
                        </div>
                        <div className="stat-label">Shift Collapse Score</div>
                        <div className="stat-change up">{getCollapseLevel(stats.overall_shift_collapse_score)}</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon green">💰</div>
                    <div className="stat-content">
                        <div className="stat-value" style={{ color: 'var(--success)' }}>
                            ₹{(stats.estimated_monthly_savings / 1000).toFixed(0)}K
                        </div>
                        <div className="stat-label">Potential Monthly Savings</div>
                        <div className="stat-change down">By reducing attrition 30%</div>
                    </div>
                </div>
            </div>

            {/* Additional Metrics Row */}
            <div className="stats-grid" style={{ marginBottom: '28px' }}>
                <div className="stat-card">
                    <div className="stat-icon blue">⏱️</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.avg_weekly_hours}h</div>
                        <div className="stat-label">Avg Weekly Hours</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon orange">📈</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.avg_overtime_3m}h</div>
                        <div className="stat-label">Avg Overtime (3M)</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon green">⭐</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.avg_performance}</div>
                        <div className="stat-label">Avg Performance</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon red">🚫</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.avg_absenteeism}%</div>
                        <div className="stat-label">Avg Absenteeism</div>
                    </div>
                </div>
            </div>

            {/* Attrition Breakdown */}
            <div className="two-col" style={{ marginBottom: '24px' }}>
                <div className="card">
                    <h3 style={{ fontSize: '16px', marginBottom: '20px' }}>🎯 Attrition Risk Breakdown</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {[
                            { label: 'High Risk', value: stats.attrition_breakdown.high, color: 'var(--danger)', pct: Math.round(stats.attrition_breakdown.high / stats.total_employees * 100) },
                            { label: 'Medium Risk', value: stats.attrition_breakdown.medium, color: 'var(--warning)', pct: Math.round(stats.attrition_breakdown.medium / stats.total_employees * 100) },
                            { label: 'Low Risk', value: stats.attrition_breakdown.low, color: 'var(--success)', pct: Math.round(stats.attrition_breakdown.low / stats.total_employees * 100) },
                        ].map((item) => (
                            <div key={item.label}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                                    <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>{item.label}</span>
                                    <span style={{ fontSize: '13px', fontWeight: '700', color: item.color }}>{item.value} ({item.pct}%)</span>
                                </div>
                                <div style={{ height: '8px', background: 'rgba(255,255,255,0.04)', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{ height: '100%', width: `${item.pct}%`, background: item.color, borderRadius: '4px', transition: 'width 1s ease' }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="card">
                    <h3 style={{ fontSize: '16px', marginBottom: '20px' }}>🏭 Sector Analysis</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {Object.entries(stats.sectors || {}).map(([sector, data]) => (
                            <div key={sector} style={{
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                padding: '12px 16px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)',
                            }}>
                                <div>
                                    <div style={{ fontSize: '14px', fontWeight: '600' }}>{sector}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{data.count} employees</div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <span className={`badge badge-${data.high_risk > data.count * 0.4 ? 'high' : data.high_risk > data.count * 0.2 ? 'medium' : 'low'}`}>
                                        {data.high_risk} at risk
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Company Shift Collapse Ranking */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '16px', marginBottom: '20px' }}>
                    🏆 Company Shift Collapse Ranking <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '400' }}>— worst to best</span>
                </h3>
                <div style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Company</th>
                                <th>Sector</th>
                                <th>Employees</th>
                                <th>Collapse Score</th>
                                <th>High Risk %</th>
                                <th>Avg Weekly Hrs</th>
                                <th>Avg Overtime</th>
                                <th>Absenteeism</th>
                            </tr>
                        </thead>
                        <tbody>
                            {comparison.map((c, i) => (
                                <tr key={c.company}>
                                    <td style={{ fontWeight: '700', color: i === 0 ? 'var(--danger)' : 'var(--text-primary)' }}>
                                        #{i + 1}
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span>{c.icon}</span>
                                            <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{c.company}</span>
                                        </div>
                                    </td>
                                    <td>{c.sector}</td>
                                    <td>{c.total_employees}</td>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <div style={{ flex: 1, height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', maxWidth: '80px' }}>
                                                <div style={{
                                                    height: '100%', borderRadius: '3px',
                                                    width: `${c.shift_collapse_score}%`,
                                                    background: getCollapseColor(c.shift_collapse_score),
                                                    transition: 'width 1s ease',
                                                }} />
                                            </div>
                                            <span style={{ fontWeight: '700', color: getCollapseColor(c.shift_collapse_score), fontFamily: "'JetBrains Mono', monospace", fontSize: '13px' }}>
                                                {c.shift_collapse_score}
                                            </span>
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`badge badge-${c.high_risk_pct > 50 ? 'high' : c.high_risk_pct > 25 ? 'medium' : 'low'}`}>
                                            {c.high_risk_pct}%
                                        </span>
                                    </td>
                                    <td style={{ color: c.avg_weekly_hours > 52 ? 'var(--danger)' : 'var(--text-secondary)' }}>
                                        {c.avg_weekly_hours}h
                                    </td>
                                    <td style={{ color: c.avg_overtime > 35 ? 'var(--danger)' : 'var(--text-secondary)' }}>
                                        {c.avg_overtime}h
                                    </td>
                                    <td style={{ color: c.avg_absenteeism > 10 ? 'var(--danger)' : 'var(--text-secondary)' }}>
                                        {c.avg_absenteeism}%
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
