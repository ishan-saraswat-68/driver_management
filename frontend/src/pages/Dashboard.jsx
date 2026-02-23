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
import {
    Users,
    BarChart3,
    AlertTriangle,
    History,
    RefreshCw,
    Search,
    ChevronRight,
    ArrowUpRight,
    Loader2
} from "lucide-react";

const API_BASE = "http://127.0.0.1:8000";
const ALERT_THRESHOLD = 2.5;

function ScoreColor(score) {
    if (score >= 3.5) return "#34d399";
    if (score <= 1.5) return "#f87171";
    return "#fbbf24";
}

function ScoreBadge({ score }) {
    if (score >= 3.5) return <span className="badge badge-positive">Positive</span>;
    if (score <= 1.5) return <span className="badge badge-negative">Negative</span>;
    return <span className="badge badge-neutral">Neutral</span>;
}

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        const d = payload[0].payload;
        return (
            <div
                style={{
                    background: "rgba(15, 23, 42, 0.9)",
                    backdropFilter: "blur(8px)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    borderRadius: 12,
                    padding: "16px",
                    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.5)",
                    fontSize: 14,
                }}
            >
                <div style={{ color: "var(--text-secondary)", marginBottom: 8, fontSize: 12, fontWeight: 600 }}>
                    {d.driver_id}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: ScoreColor(d.score) }} />
                    <span style={{ fontWeight: 600, color: "white" }}>
                        {d.score.toFixed(2)}/5.0
                    </span>
                </div>
                <div style={{ color: "var(--text-muted)", marginTop: 8, fontSize: 12 }}>
                    Based on {d.total_count} responses
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
            setError("Connectivity issue detected. Please check your network.");
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
            ? (drivers.reduce((a, b) => a + b.score, 0) / drivers.length).toFixed(2)
            : "0.00";
    const totalFeedback = drivers.reduce((a, b) => a + b.total_count, 0);

    const chartData = [...drivers]
        .sort((a, b) => a.score - b.score)
        .slice(0, 15)
        .map((d) => ({
            ...d,
            shortId: d.driver_id.slice(0, 6) + "..",
        }));

    return (
        <div>
            <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
                <div>
                    <h1>Insights Platform</h1>
                    <p>Real-time sentiment monitoring and predictive fleet health metrics.</p>
                </div>
                <button className="btn btn-outline" onClick={fetchDrivers} style={{ padding: '10px 20px', fontSize: 14 }}>
                    <RefreshCw size={16} className={loading ? "spin" : ""} />
                    Sync Data
                </button>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div className="stat-label">Total Fleet</div>
                        <Users size={16} color="var(--accent)" />
                    </div>
                    <div className="stat-value">{loading ? "—" : drivers.length}</div>
                    <div className="stat-sub">Active identifiers</div>
                </div>
                <div className="stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div className="stat-label">Fleet Sentiment</div>
                        <BarChart3 size={16} color="var(--accent2)" />
                    </div>
                    <div className="stat-value" style={{ color: ScoreColor(parseFloat(avgScore)) }}>
                        {loading ? "—" : avgScore}
                    </div>
                    <div className="stat-sub">Aggregate EMA score</div>
                </div>
                <div className="stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div className="stat-label">At-Risk Nodes</div>
                        <AlertTriangle size={16} color={atRisk > 0 ? "var(--danger)" : "var(--success)"} />
                    </div>
                    <div className="stat-value" style={{ color: atRisk > 0 ? "var(--danger)" : "var(--success)" }}>
                        {loading ? "—" : atRisk}
                    </div>
                    <div className="stat-sub">Below {ALERT_THRESHOLD} threshold</div>
                </div>
                <div className="stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div className="stat-label">Total Volume</div>
                        <History size={16} color="var(--text-muted)" />
                    </div>
                    <div className="stat-value">{loading ? "—" : totalFeedback.toLocaleString()}</div>
                    <div className="stat-sub">Feedback entries</div>
                </div>
            </div>

            {!loading && !error && chartData.length > 0 && (
                <div className="card" style={{ marginBottom: 48 }}>
                    <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <BarChart3 size={14} />
                        Sentiment Distribution — Lowest Performers
                    </div>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={chartData} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
                                <XAxis
                                    dataKey="shortId"
                                    tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <YAxis
                                    domain={[0, 5]}
                                    ticks={[0, 2.5, 5]}
                                    tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                                <ReferenceLine
                                    y={ALERT_THRESHOLD}
                                    stroke="var(--danger)"
                                    strokeDasharray="4 4"
                                    opacity={0.5}
                                />
                                <Bar dataKey="score" radius={[6, 6, 0, 0]} barSize={32}>
                                    {chartData.map((entry, i) => (
                                        <Cell key={i} fill={ScoreColor(entry.score)} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            <div className="card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
                    <div className="card-title" style={{ margin: 0 }}>Fleet Registry</div>
                    <div style={{ position: 'relative' }}>
                        <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input
                            className="input"
                            style={{ maxWidth: 300, paddingLeft: 40 }}
                            placeholder="Filter by identifier..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                </div>

                {loading ? (
                    <div className="empty-state"><Loader2 size={32} className="spin" style={{ margin: "0 auto", opacity: 0.3 }} /></div>
                ) : error ? (
                    <div className="empty-state"><p style={{ color: "var(--danger)" }}>{error}</p></div>
                ) : filtered.length === 0 ? (
                    <div className="empty-state"><p>No results matching your query.</p></div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Identifier</th>
                                    <th>EMA Performance</th>
                                    <th style={{ textAlign: 'center' }}>Classification</th>
                                    <th style={{ textAlign: 'center' }}>Sample Size</th>
                                    <th style={{ textAlign: 'right' }}>Last Signal</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map((driver) => (
                                    <tr key={driver.driver_id}>
                                        <td style={{ fontFamily: "Outfit", fontWeight: 500 }}>{driver.driver_id}</td>
                                        <td>
                                            <div className="score-bar-wrap">
                                                <div className="score-bar">
                                                    <div className="score-bar-fill" style={{ width: `${(driver.score / 5) * 100}%` }} />
                                                </div>
                                                <span className="score-val">{driver.score.toFixed(2)}</span>
                                            </div>
                                        </td>
                                        <td style={{ textAlign: 'center' }}><ScoreBadge score={driver.score} /></td>
                                        <td style={{ textAlign: 'center', color: "var(--text-secondary)" }}>{driver.total_count}</td>
                                        <td style={{ textAlign: 'right' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                                                <span style={{ fontSize: 13 }}>{driver.last_updated ? new Date(driver.last_updated).toLocaleDateString() : '—'}</span>
                                                <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{driver.last_updated ? new Date(driver.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</span>
                                            </div>
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