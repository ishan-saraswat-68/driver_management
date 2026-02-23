import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Wraps a component and redirects to /login if not authenticated.
 * If allowedRoles is provided, also enforces role-based access.
 */
export default function ProtectedRoute({ children, allowedRoles }) {
    const { user, role, loading } = useAuth();

    if (loading) {
        return (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh" }}>
                <div className="auth-loading">
                    <div className="spinner-ring" />
                </div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(role)) {
        // Logged in but insufficient role → redirect to home
        return <Navigate to="/" replace />;
    }

    return children;
}
