import { useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

// Feature Flags — controls which feedback types are visible
const FEEDBACK_TYPES = [
    { key: "driver", label: "Driver", icon: "🚗", enabled: true },
    { key: "trip", label: "Trip", icon: "📍", enabled: true },
    { key: "app", label: "Mobile App", icon: "📱", enabled: true },
    { key: "marshal", label: "Marshal", icon: "👮", enabled: true },
];

export default function Feedback() {
    const [activeType, setActiveType] = useState("driver");
    const [driverId, setDriverId] = useState("");
    const [tripId, setTripId] = useState("");
    const [text, setText] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [toast, setToast] = useState(null); // { type: 'success'|'error', msg }

    const showToast = (type, msg) => {
        setToast({ type, msg });
        setTimeout(() => setToast(null), 4000);
    };

    const handleSubmit = async () => {
        if (!driverId.trim() || !tripId.trim() || !text.trim()) {
            showToast("error", "Please fill in all fields.");
            return;
        }
        setSubmitting(true);
        try {
            const res = await axios.post(`${API_BASE}/feedback`, {
                driver_id: driverId.trim(),
                trip_id: tripId.trim(),
                text: text.trim(),
                external_feedback_id: crypto.randomUUID(),
            });

            if (res.data.success) {
                showToast("success", "✓ Feedback submitted successfully!");
                setText("");
            } else {
                showToast("error", res.data.message || "Something went wrong.");
            }
        } catch (err) {
            const detail = err?.response?.data?.detail;
            showToast("error", detail || "Failed to submit feedback. Is the server running?");
        } finally {
            setSubmitting(false);
        }
    };

    const enabledTypes = FEEDBACK_TYPES.filter((t) => t.enabled);

    return (
        <div>
            <div className="page-header">
                <h1>Submit Feedback</h1>
                <p>Collect and analyze rider feedback for drivers, trips, and operations.</p>
            </div>

            {/* Feedback Type Selector */}
            <div className="segment-control">
                {enabledTypes.map((type) => (
                    <button
                        key={type.key}
                        className={`segment-btn ${activeType === type.key ? "active" : ""}`}
                        onClick={() => setActiveType(type.key)}
                    >
                        {type.icon} {type.label}
                    </button>
                ))}
            </div>

            <div className="card" style={{ maxWidth: 680 }}>
                <div className="form-group">
                    <label>Driver ID</label>
                    <input
                        className="input"
                        placeholder="e.g. drv_12345"
                        value={driverId}
                        onChange={(e) => setDriverId(e.target.value)}
                    />
                </div>

                <div className="form-group">
                    <label>Trip ID</label>
                    <input
                        className="input"
                        placeholder="e.g. trip_98765"
                        value={tripId}
                        onChange={(e) => setTripId(e.target.value)}
                    />
                </div>

                <div className="form-group">
                    <label>
                        Feedback — <span style={{ textTransform: "capitalize" }}>{activeType}</span>
                    </label>
                    <textarea
                        className="textarea"
                        placeholder={getPlaceholder(activeType)}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                    />
                    <div className="hint">
                        Sentiment will be analyzed automatically. Negative scores trigger alerts.
                    </div>
                </div>

                <button
                    className="btn btn-primary"
                    onClick={handleSubmit}
                    disabled={submitting}
                    style={{ width: "100%" }}
                >
                    {submitting ? <span className="spinner" /> : "🚀 Submit Feedback"}
                </button>

                {toast && (
                    <div className={`toast toast-${toast.type}`}>
                        {toast.msg}
                    </div>
                )}
            </div>
        </div>
    );
}

function getPlaceholder(type) {
    const map = {
        driver: "Describe the driver's behaviour, professionalism, and overall experience...",
        trip: "Describe the trip quality — route taken, ETAs, safety during the ride...",
        app: "Share your experience using the mobile app — UI, speed, bugs, or crashes...",
        marshal: "Describe the marshal's conduct, helpfulness, and safety protocols...",
    };
    return map[type] || "Write your feedback here...";
}