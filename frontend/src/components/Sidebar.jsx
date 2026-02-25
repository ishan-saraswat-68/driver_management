import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
    const { user, role, signOut } = useAuth();

    const isAdmin = role === "admin";

    const navItems = [
        { label: "Feedback", path: "/" },
        // Dashboard only visible to admins
        ...(isAdmin ? [{ label: "Insights", path: "/dashboard" }] : []),
    ];

    const initials = user?.email?.slice(0, 2).toUpperCase() ?? "??";
    const displayEmail = user?.email ?? "";

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="logo-icon"></div>
                <span>SentimentIQ</span>
            </div>

            <nav>
                <ul className="sidebar-nav">
                    {navItems.map((item) => (
                        <li key={item.path}>
                            <NavLink
                                to={item.path}
                                end
                                className={({ isActive }) => (isActive ? "active" : "")}
                            >
                                {item.label}
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>

            {/* Role badge */}
            <div style={{ padding: "0 20px", marginTop: "auto" }}>
                <div className="sidebar-role-badge">
                    {isAdmin ? "Admin" : "Employee"}
                </div>
                {/* User card */}
                <div className="sidebar-user">
                    <div className="user-avatar">{initials}</div>
                    <div className="user-info">
                        <div className="user-email" title={displayEmail}>{displayEmail}</div>
                    </div>
                    <button className="user-signout" onClick={signOut} title="Sign out" style={{ fontSize: "12px", fontWeight: "600", padding: "4px 8px" }}>
                        Sign out
                    </button>
                </div>
            </div>
        </aside>
    );
}
