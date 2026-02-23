import { useState, useEffect } from "react";
import axios from "axios";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    Cell,
    ReferenceLine,
} from "recharts";

const API_BASE = "http://127.0.0.1:8000";
const ALERT_THRESHOLD = -0.5;

function ScoreColor(score) {
    if (score >= 0.25) return "var(--success)";
    if (score <= -0.25) return "var(--danger)";
    return "var(--warning)";
}

function ScoreBadge({ score }) {
    if (score >= 0.25) return <span className="badge badge-positive">Positive</span>;
    if (score <= -0.25) return <span className="badge badge-negative">Negative</span>;
    return <span className="badge badge-neutral">Neutral</span>;
}

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        const d = payload[0].payload;
        return (
            <div
                style={{
                    background: "var(--bg-card)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                    padding: "10px 14px",
                    fontSize: 13,
                }}
            >
                <div style={{ color: "var(--text-secondary)", marginBottom: 4 }}>
                    {d.driver_id}
                </div>
                <div style={{ fontWeight: 600, color: ScoreColor(d.score) }}>
                    Score: {d.score.toFixed(3)}
                </div>
                <div style={{ color: "var(--text-muted)", marginTop: 2 }}>
                    Feedbacks: {d.total_count}
                </div>
            </div>
        );
    }
    return null;
};

export default function Dashboard() {
    const [drivers, setDrivers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState("");

    const fetchDrivers = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await axios.get(`${API_BASE}/drivers`);
            setDrivers(res.data.data || []);
        } catch (err) {
            setError("Could not connect to the server. Make sure the backend is running.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDrivers();
    }, []);

    const filtered = drivers.filter((d) =>
        d.driver_id.toLowerCase().includes(search.toLowerCase())
    );

    const atRisk = drivers.filter((d) => d.score < ALERT_THRESHOLD).length;
    const avgScore =
        drivers.length > 0
            ? (drivers.reduce((a, b) => a + b.score, 0) / drivers.length).toFixed(3)
            : "N/A";
    const totalFeedback = drivers.reduce((a, b) => a + b.total_count, 0);

    const chartData = [...drivers]
        .sort((a, b) => a.score - b.score)
        .slice(0, 15)
        .map((d) => ({
            ...d,
            shortId: d.driver_id.slice(0, 8) + "...",
        }));

    return (
        <div>
            <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                    <h1>Admin Dashboard</h1>
                    <p>Real-time driver sentiment analytics and alert monitoring.</p>
                </div>
                <button className="btn btn-outline" onClick={fetchDrivers}>
                    ↻ Refresh
                </button>
            </div>

            {/* Stats */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-label">Total Drivers</div>
                    <div className="stat-value" style={{ color: "var(--accent)" }}>
                        {loading ? "—" : drivers.length}
                    </div>
                    <div className="stat-sub">Active in system</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Avg Sentiment Score</div>
                    <div
                        className="stat-value"
                        style={{ color: avgScore !== "N/A" ? ScoreColor(parseFloat(avgScore)) : "var(--text-secondary)" }}
                    >
                        {loading ? "—" : avgScore}
                    </div>
                    <div className="stat-sub">Fleet EMA average</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">At-Risk Drivers</div>
                    <div className="stat-value" style={{ color: atRisk > 0 ? "var(--danger)" : "var(--success)" }}>
                        {loading ? "—" : atRisk}
                    </div>
                    <div className="stat-sub">Score below {ALERT_THRESHOLD}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Total Feedback</div>
                    <div className="stat-value" style={{ color: "var(--accent2)" }}>
                        {loading ? "—" : totalFeedback.toLocaleString()}
                    </div>
                    <div className="stat-sub">Processed submissions</div>
                </div>
            </div>

            {/* Chart */}
            {!loading && !error && chartData.length > 0 && (
                <div className="card" style={{ marginBottom: 28 }}>
                    <div className="card-title">Driver Score Distribution (Bottom 15)</div>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={240}>
                            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <XAxis
                                    dataKey="shortId"
                                    tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <YAxis
                                    domain={[-1, 1]}
                                    tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(99,102,241,0.07)" }} />
                                <ReferenceLine
                                    y={ALERT_THRESHOLD}
                                    stroke="var(--danger)"
                                    strokeDasharray="4 3"
                                    label={{
                                        value: "Alert threshold",
                                        position: "insideTopRight",
                                        fill: "var(--danger)",
                                        fontSize: 10,
                                    }}
                                />
                                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                                    {chartData.map((entry, i) => (
                                        <Cell key={i} fill={ScoreColor(entry.score)} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* Driver Table */}
            <div className="card">
                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginBottom: 20,
                    }}
                >
                    <div className="card-title" style={{ margin: 0 }}>All Drivers</div>
                    <input
                        className="input"
                        style={{ maxWidth: 260 }}
                        placeholder="Search by Driver ID..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                {loading ? (
                    <div className="empty-state">
                        <div className="spinner" style={{ margin: "0 auto" }} />
                    </div>
                ) : error ? (
                    <div className="empty-state">
                        <div className="empty-icon">⚠️</div>
                        <p style={{ color: "var(--danger)" }}>{error}</p>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">🔍</div>
                        <p>No drivers found.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Driver ID</th>
                                    <th>EMA Score</th>
                                    <th>Status</th>
                                    <th>Feedbacks</th>
                                    <th>Last Updated</th>
                                    <th>Last Alert</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map((driver) => (
                                    <tr key={driver.driver_id}>
                                        <td style={{ fontFamily: "monospace", fontSize: 13 }}>
                                            {driver.driver_id}
                                        </td>
                                        <td>
                                            <div className="score-bar-wrap">
                                                <div className="score-bar">
                                                    <div
                                                        className="score-bar-fill"
                                                        style={{
                                                            width: `${((driver.score + 1) / 2) * 100}%`,
                                                            background: ScoreColor(driver.score),
                                                        }}
                                                    />
                                                </div>
                                                <span
                                                    className="score-val"
                                                    style={{ color: ScoreColor(driver.score) }}
                                                >
                                                    {driver.score.toFixed(2)}
                                                </span>
                                            </div>
                                        </td>
                                        <td>
                                            <ScoreBadge score={driver.score} />
                                            {driver.score < ALERT_THRESHOLD && (
                                                <span className="badge badge-alert" style={{ marginLeft: 6 }}>
                                                    🚨 Alert
                                                </span>
                                            )}
                                        </td>
                                        <td style={{ color: "var(--text-secondary)" }}>
                                            {driver.total_count}
                                        </td>
                                        <td style={{ color: "var(--text-muted)", fontSize: 12 }}>
                                            {driver.last_updated
                                                ? new Date(driver.last_updated).toLocaleString()
                                                : "—"}
                                        </td>
                                        <td style={{ color: "var(--text-muted)", fontSize: 12 }}>
                                            {driver.last_alert_at
                                                ? new Date(driver.last_alert_at).toLocaleString()
                                                : "—"}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}