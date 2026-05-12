import React, { useState } from 'react';

function ScenarioSimulator() {
    const [params, setParams] = useState({
        overtime_reduction: 30,
        night_shift_cap: 3,
        salary_increase: 15,
        rest_hours: 12,
        weekly_cap: 48,
    });
    const [result, setResult] = useState(null);
    const [simulating, setSimulating] = useState(false);

    const runSimulation = async () => {
        setSimulating(true);
        // Simulate processing
        await new Promise(r => setTimeout(r, 1500));

        const attritionReduction = Math.round(
            (params.overtime_reduction * 0.4) +
            (params.salary_increase * 0.35) +
            ((48 - params.weekly_cap + 10) * 0.15) +
            (params.rest_hours * 0.1)
        );

        const costImpact = Math.round(
            (params.salary_increase * 1200) -
            (attritionReduction * 8500 * 0.5)
        );

        setResult({
            attrition_reduction: Math.min(65, attritionReduction),
            cost_impact: costImpact,
            shift_collapse_improvement: Math.min(40, Math.round(params.overtime_reduction * 0.8)),
            productivity_gain: Math.round(params.rest_hours * 1.5 + params.salary_increase * 0.5),
            compliance_score: Math.min(100, 60 + (params.weekly_cap <= 48 ? 30 : 0) + (params.rest_hours >= 12 ? 10 : 0)),
        });
        setSimulating(false);
    };

    return (
        <div className="animate-fade-up">
            <div className="page-header">
                <div>
                    <h1 className="page-title">🔮 What-If Simulator</h1>
                    <p className="page-subtitle">Simulate policy changes and see predicted impact on attrition & shift collapse</p>
                </div>
                <button className="btn btn-primary" onClick={runSimulation} disabled={simulating}>
                    {simulating ? (
                        <><div className="loading-spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }} /> Simulating...</>
                    ) : '⚡ Run Simulation'}
                </button>
            </div>

            <div className="two-col">
                {/* Parameters */}
                <div className="card">
                    <h3 style={{ fontSize: '16px', marginBottom: '24px' }}>📐 Simulation Parameters</h3>

                    {[
                        { key: 'overtime_reduction', label: '⏱️ Overtime Reduction', unit: '%', min: 0, max: 100, desc: 'How much to reduce overtime hours' },
                        { key: 'night_shift_cap', label: '🌙 Max Consecutive Night Shifts', unit: 'shifts', min: 1, max: 7, desc: 'Cap on back-to-back night shifts' },
                        { key: 'salary_increase', label: '💰 Base Salary Increase', unit: '%', min: 0, max: 50, desc: 'Salary bump to reduce gig-hopping' },
                        { key: 'rest_hours', label: '😴 Min Rest Between Shifts', unit: 'hours', min: 8, max: 24, desc: 'Mandatory rest period' },
                        { key: 'weekly_cap', label: '📊 Weekly Hours Cap', unit: 'hours', min: 36, max: 60, desc: 'Maximum working hours per week' },
                    ].map(({ key, label, unit, min, max, desc }) => (
                        <div key={key} style={{ marginBottom: '24px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                <div>
                                    <div style={{ fontSize: '13px', fontWeight: '600' }}>{label}</div>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{desc}</div>
                                </div>
                                <div style={{
                                    padding: '4px 12px', background: 'var(--bg-secondary)',
                                    borderRadius: '6px', fontSize: '14px', fontWeight: '700',
                                    color: 'var(--accent-primary)', fontFamily: "'JetBrains Mono'",
                                }}>
                                    {params[key]} {unit}
                                </div>
                            </div>
                            <input type="range" min={min} max={max}
                                value={params[key]}
                                onChange={(e) => setParams({ ...params, [key]: parseInt(e.target.value) })}
                                style={{
                                    width: '100%', height: '6px', borderRadius: '3px',
                                    appearance: 'none', background: 'var(--bg-secondary)',
                                    outline: 'none', cursor: 'pointer',
                                    accentColor: 'var(--accent-primary)',
                                }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>
                                <span>{min}</span>
                                <span>{max}</span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Results */}
                <div>
                    {result ? (
                        <div className="card animate-fade-up">
                            <h3 style={{ fontSize: '16px', marginBottom: '24px' }}>📊 Predicted Impact</h3>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                <div style={{ padding: '20px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--success)' }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Attrition Reduction</div>
                                    <div style={{ fontSize: '32px', fontWeight: '800', color: 'var(--success)' }}>↓ {result.attrition_reduction}%</div>
                                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', marginTop: '8px' }}>
                                        <div style={{ height: '100%', width: `${result.attrition_reduction}%`, background: 'var(--success)', borderRadius: '3px' }} />
                                    </div>
                                </div>

                                <div style={{ padding: '20px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', borderLeft: `3px solid ${result.cost_impact < 0 ? 'var(--success)' : 'var(--warning)'}` }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>Net Cost Impact (Monthly)</div>
                                    <div style={{ fontSize: '28px', fontWeight: '800', color: result.cost_impact < 0 ? 'var(--success)' : 'var(--warning)' }}>
                                        {result.cost_impact < 0 ? '↓' : '↑'} ₹{Math.abs(result.cost_impact).toLocaleString()}
                                    </div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                                        {result.cost_impact < 0 ? 'Net savings after salary increase' : 'Additional investment needed'}
                                    </div>
                                </div>

                                <div style={{ padding: '20px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent-primary)' }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>Shift Collapse Improvement</div>
                                    <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--accent-primary)' }}>↓ {result.shift_collapse_improvement} pts</div>
                                </div>

                                <div style={{ padding: '20px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--info)' }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>Productivity Gain</div>
                                    <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--info)' }}>↑ {result.productivity_gain}%</div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
                            <div className="empty-state">
                                <div className="empty-icon">🔬</div>
                                <div className="empty-title">Adjust parameters & run simulation</div>
                                <div className="empty-text">See how policy changes would impact attrition and shift collapse across your workforce</div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ScenarioSimulator;
