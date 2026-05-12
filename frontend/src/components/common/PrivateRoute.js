import React from 'react';
import { Navigate } from 'react-router-dom';

// Simple auth guard - redirects to login if no token
function PrivateRoute({ children }) {
    const token = localStorage.getItem('token');
    if (!token) {
        return <Navigate to="/login" replace />;
    }
    return children;
}

export default PrivateRoute;
