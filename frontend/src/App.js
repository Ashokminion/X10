import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import './index.css';

// Pages
import Login from './components/auth/Login';
import Dashboard from './components/dashboard/Dashboard';
import EmployeeList from './components/employee/Employeelist';
import CompanyView from './components/company/CompanyView';
import ShiftManagement from './components/shift/ShiftManagement';
import ChatbotInterface from './components/chatbot/ChatbotInterface';
import Reports from './components/reports/Reports';
import ScenarioSimulator from './components/dashboard/ScenarioSimulator';
import UploadPage from './components/employee/UploadPage';

// Sidebar Component
function Sidebar({ onLogout }) {
    const navigate = useNavigate();
    const location = useLocation();
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    const navItems = [
        { section: 'Overview' },
        { path: '/dashboard', icon: '📊', label: 'Dashboard', badge: null },
        { path: '/companies', icon: '🏢', label: 'Company Analytics', badge: null },
        { section: 'Workforce' },
        { path: '/employees', icon: '👥', label: 'Employees', badge: null },
        { path: '/upload', icon: '📤', label: 'Upload CSV', badge: null },
        { path: '/shifts', icon: '📅', label: 'Shift Optimizer', badge: null },
        { section: 'Intelligence' },
        { path: '/scenario', icon: '🔮', label: 'What-If Simulator', badge: null },
        { path: '/chatbot', icon: '🤖', label: 'HR Chatbot', badge: null },
        { path: '/reports', icon: '📄', label: 'Reports', badge: null },
    ];

    return (
        <div className="sidebar">
            <div className="sidebar-brand">
                <h1 className="text-gradient">WorkforceAI</h1>
                <div className="subtitle">Shift Optimization Platform</div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item, i) => {
                    if (item.section) {
                        return <div key={i} className="nav-section-label">{item.section}</div>;
                    }
                    return (
                        <div
                            key={item.path}
                            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                            onClick={() => navigate(item.path)}
                        >
                            <span className="nav-item-icon">{item.icon}</span>
                            <span>{item.label}</span>
                            {item.badge && <span className="nav-item-badge">{item.badge}</span>}
                        </div>
                    );
                })}
            </nav>

            <div className="sidebar-footer">
                <div className="user-info" onClick={onLogout}>
                    <div className="user-avatar">
                        {(user.username || 'A').charAt(0).toUpperCase()}
                    </div>
                    <div className="user-details">
                        <div className="user-name">{user.username || 'Admin'}</div>
                        <div className="user-role">{user.role || 'ADMIN'}</div>
                    </div>
                    <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>⏻</span>
                </div>
            </div>
        </div>
    );
}

// Auth Guard
function PrivateRoute({ children }) {
    const token = localStorage.getItem('token');
    if (!token) return <Navigate to="/login" replace />;
    return children;
}

// App Layout with Sidebar
function AppLayout() {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
    };

    return (
        <div className="app-layout">
            <Sidebar onLogout={handleLogout} />
            <main className="main-content">
                <Routes>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/companies" element={<CompanyView />} />
                    <Route path="/employees" element={<EmployeeList />} />
                    <Route path="/upload" element={<UploadPage />} />
                    <Route path="/shifts" element={<ShiftManagement />} />
                    <Route path="/scenario" element={<ScenarioSimulator />} />
                    <Route path="/chatbot" element={<ChatbotInterface />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </main>
        </div>
    );
}

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/*" element={
                    <PrivateRoute>
                        <AppLayout />
                    </PrivateRoute>
                } />
            </Routes>
        </Router>
    );
}

export default App;
