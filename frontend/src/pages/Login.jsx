import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Eye, EyeOff } from "lucide-react";

export default function Login() {
    const { signIn } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleLogin = async (e) => {
        e.preventDefault();
        if (!email || !password) {
            setError("Please enter your credentials.");
            return;
        }
        setLoading(true);
        setError(null);

        const { error: authError } = await signIn(email, password);
        if (authError) {
            setError(authError.message || "Invalid credentials. Please try again.");
            setLoading(false);
            return;
        }

        
        navigate("/");
    };

    return (
        <div className="login-page">
            <div className="login-card">
                {/* Logo */}
                <div className="login-logo">
                    <div className="logo-icon"></div>
                    <div>
                        <div className="login-brand">SentimentIQ</div>
                        <div className="login-tagline">Driver Intelligence Platform</div>
                    </div>
                </div>

                <div className="login-divider" />

                <div className="login-heading">
                    <h2>Welcome back</h2>
                    <p>Sign in to continue to your workspace</p>
                </div>

                <form onSubmit={handleLogin} autoComplete="on">
                    <div className="form-group">
                        <label>Email address</label>
                        <input
                            className="input"
                            type="email"
                            placeholder="your@email.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            autoComplete="email"
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <div className="input-with-icon">
                            <input
                                className="input input-icon-right"
                                type={showPassword ? "text" : "password"}
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                autoComplete="current-password"
                            />
                            <button
                                type="button"
                                className="input-eye"
                                onClick={() => setShowPassword(!showPassword)}
                                tabIndex={-1}
                            >
                                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>

                    {error && (
                        <div className="login-error">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={loading}
                        style={{ width: "100%", marginTop: 8 }}
                    >
                        {loading ? (
                            <span className="spinner-ring" style={{ width: 17, height: 17 }} />
                        ) : (
                            "Sign in"
                        )}
                    </button>
                </form>

                <div className="login-roles-hint">
                    <div className="role-badge role-admin">Admin · Full access</div>
                    <div className="role-badge role-employee">Employee · Feedback only</div>
                </div>

                <div style={{ textAlign: "center", marginTop: 24, fontSize: 14, color: "var(--text-muted)" }}>
                    Don't have an account?{" "}
                    <Link to="/signup" style={{ color: "var(--accent)", textDecoration: "none", fontWeight: 600 }}>
                        Create one
                    </Link>
                </div>
            </div>
        </div>
    );
}
