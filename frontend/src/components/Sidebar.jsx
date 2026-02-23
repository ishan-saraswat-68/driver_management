import React from "react";
import { NavLink } from "react-router-dom";

const navItems = [
    { label: "Feedback", path: "/", icon: "💬" },
    { label: "Dashboard", path: "/dashboard", icon: "📊" },
];

export default function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="logo-icon">🚗</div>
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
                                <span className="nav-icon">{item.icon}</span>
                                {item.label}
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>
        </aside>
    );
}
