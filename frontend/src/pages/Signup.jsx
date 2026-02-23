import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";
import { Lock, Mail, Zap, Eye, EyeOff, AlertCircle, CheckCircle2, User } from "lucide-react";

export default function Signup() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [fullName, setFullName] = useState("");
    const [password, setPassword] = useState("");
    const [confirm, setConfirm] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleSignup = async (e) => {
        e.preventDefault();
        setError(null);

        if (!fullName.trim() || !email || !password || !confirm) {
            setError("Please fill in all fields.");
            return;
        }
        if (password.length < 6) {
            setError("Password must be at least 6 characters.");
            return;
        }
        if (password !== confirm) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);
        const { error: authError } = await supabase.auth.signUp({
            email,
            password,
            options: { data: { full_name: fullName.trim() } },
        });
        setLoading(false);

        if (authError) {
            const msg = authError.message?.toLowerCase() || "";
            if (authError.status === 429 || msg.includes("rate limit") || msg.includes("too many")) {
                setError("Too many signup attempts. Please wait a few minutes and try again.");
            } else if (authError.status === 400 || msg.includes("already registered") || msg.includes("already exists")) {
                setError("An account with this email already exists. Try signing in instead.");
            } else {
                setError(authError.message || "Signup failed. Please try again.");
            }
            setLoading(false);
            return;
        }

        setSuccess(true);
    };

    if (success) {
        return (
            <div className="login-page">
                <div className="login-glow login-glow-1" />
                <div className="login-glow login-glow-2" />
                <div className="login-card" style={{ textAlign: "center" }}>
                    <div style={{ display: "flex", justifyContent: "center", marginBottom: 24 }}>
                        <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(52, 211, 153, 0.1)", border: "1px solid rgba(52, 211, 153, 0.3)", display: "grid", placeItems: "center" }}>
                            <CheckCircle2 size={28} color="var(--success)" />
                        </div>
                    </div>
                    <h2 style={{ fontFamily: "Outfit", fontSize: 24, fontWeight: 700, marginBottom: 12 }}>You're registered!</h2>
                    <p style={{ color: "var(--text-secondary)", fontSize: 15, lineHeight: 1.6, marginBottom: 32 }}>
                        Check your inbox and confirm your email. You'll have <strong>Employee access</strong> by default. Contact your admin for elevated permissions.
                    </p>
                    <Link to="/login" className="btn btn-primary" style={{ display: "inline-flex", textDecoration: "none" }}>
                        Go to Sign In
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="login-page">
            <div className="login-glow login-glow-1" />
            <div className="login-glow login-glow-2" />

            <div className="login-card">
                <div className="login-logo">
                    <div className="logo-icon">
                        <Zap size={24} color="white" fill="white" />
                    </div>
                    <div>
                        <div className="login-brand">SentimentIQ</div>
                        <div className="login-tagline">Driver Intelligence Platform</div>
                    </div>
                </div>

                <div className="login-divider" />

                <div className="login-heading">
                    <h2>Create an account</h2>
                    <p>New accounts get Employee access by default</p>
                </div>

                <form onSubmit={handleSignup} autoComplete="off">
                    <div className="form-group">
                        <label>Full Name</label>
                        <input
                            className="input"
                            type="text"
                            placeholder="Your full name"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            autoComplete="name"
                        />
                    </div>

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
                                placeholder="Min. 6 characters"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                            <button type="button" className="input-eye" onClick={() => setShowPassword(!showPassword)} tabIndex={-1}>
                                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Confirm Password</label>
                        <input
                            className="input"
                            type={showPassword ? "text" : "password"}
                            placeholder="Re-enter password"
                            value={confirm}
                            onChange={(e) => setConfirm(e.target.value)}
                        />
                    </div>

                    {error && (
                        <div className="login-error">
                            <AlertCircle size={16} />
                            {error}
                        </div>
                    )}

                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: "100%", marginTop: 8 }}>
                        {loading ? <span className="spinner-ring" style={{ width: 18, height: 18 }} /> : "Create Account"}
                    </button>
                </form>

                <div style={{ textAlign: "center", marginTop: 28, fontSize: 14, color: "var(--text-muted)" }}>
                    Already have an account?{" "}
                    <Link to="/login" style={{ color: "var(--accent)", textDecoration: "none", fontWeight: 500 }}>
                        Sign in
                    </Link>
                </div>
            </div>
        </div>
    );
}
