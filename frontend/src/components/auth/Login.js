import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../../services/api';

function Login() {
    const [formData, setFormData] = useState({ username: 'admin', password: 'admin123' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await authAPI.login(formData);
            const { token, id, username, email, role } = response.data;
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify({ id, username, email, role }));
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.message || 'Login failed. Check credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--bg-primary)',
            position: 'relative',
            overflow: 'hidden',
        }}>
            {/* Background gradient orbs */}
            <div style={{
                position: 'absolute', width: '500px', height: '500px', borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(99,102,241,0.15), transparent 70%)',
                top: '-150px', right: '-100px', pointerEvents: 'none',
            }} />
            <div style={{
                position: 'absolute', width: '400px', height: '400px', borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(139,92,246,0.1), transparent 70%)',
                bottom: '-100px', left: '-100px', pointerEvents: 'none',
            }} />

            <div className="animate-fade-up" style={{
                width: '420px', padding: '44px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-xl)',
                boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
                position: 'relative', zIndex: 1,
            }}>
                <div style={{ textAlign: 'center', marginBottom: '36px' }}>
                    <div style={{ fontSize: '42px', marginBottom: '12px' }}>🧠</div>
                    <h1 style={{ fontSize: '24px', fontWeight: '800', letterSpacing: '-0.03em', marginBottom: '6px' }}>
                        <span className="text-gradient">WorkforceAI</span>
                    </h1>
                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', fontWeight: '500' }}>
                        AI-Powered Shift Optimization for India's Blue-Collar Workforce
                    </p>
                </div>

                {error && (
                    <div style={{
                        background: 'var(--danger-glow)', border: '1px solid rgba(239,68,68,0.2)',
                        borderRadius: 'var(--radius-sm)', padding: '10px 14px', marginBottom: '20px',
                        fontSize: '13px', color: 'var(--danger)',
                    }}>{error}</div>
                )}

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                            Username
                        </label>
                        <input
                            className="input"
                            type="text"
                            value={formData.username}
                            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                            placeholder="Enter username"
                            required
                        />
                    </div>

                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                            Password
                        </label>
                        <input
                            className="input"
                            type="password"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            placeholder="Enter password"
                            required
                        />
                    </div>

                    <button className="btn btn-primary" type="submit" disabled={loading} style={{
                        width: '100%', padding: '12px', fontSize: '14px', fontWeight: '700',
                    }}>
                        {loading ? (
                            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                                <div className="loading-spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} />
                                Signing in...
                            </span>
                        ) : 'Sign In →'}
                    </button>
                </form>

                <div style={{ textAlign: 'center', marginTop: '24px' }}>
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        Demo: <span style={{ color: 'var(--text-secondary)', fontFamily: "'JetBrains Mono', monospace" }}>admin / admin123</span>
                    </p>
                </div>

                {/* Company logos */}
                <div style={{
                    display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '28px',
                    paddingTop: '20px', borderTop: '1px solid var(--border-subtle)',
                }}>
                    {['🍕 Swiggy', '🍔 Zomato', '⚡ Blinkit', '📦 Amazon', '🏗️ L&T'].map((c) => (
                        <span key={c} style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: '500' }}>{c}</span>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Login;
