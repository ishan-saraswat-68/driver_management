import { useState } from "react";
import axios from "axios";
import { Loader2 } from "lucide-react";

const API_BASE = "http://127.0.0.1:8000";

export default function Feedback() {
    const [driverId, setDriverId] = useState("");
    const [tripId, setTripId] = useState("");
    const [text, setText] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [toast, setToast] = useState(null);

    const showToast = (type, msg) => {
        setToast({ type, msg });
        setTimeout(() => setToast(null), 5000);
    };

    const handleSubmit = async () => {
        if (!driverId.trim() || !tripId.trim() || !text.trim()) {
            showToast("error", "Please ensure all details are filled in before submitting.");
            return;
        }
        setSubmitting(true);
        try {
            const res = await axios.post(`${API_BASE}/feedback`, {
                driver_id: driverId.trim(),
                trip_id: tripId.trim(),
                text: text.trim(),
                entity_type: "driver",
                external_feedback_id: crypto.randomUUID(),
            });

            if (res.data.success) {
                showToast("success", "Feedback recorded. Our AI is analyzing it now.");
                setText("");
            } else {
                showToast("error", res.data.message || "An unexpected error occurred.");
            }
        } catch (err) {
            const detail = err?.response?.data?.detail;
            showToast("error", detail || "Connection failed. Is the engine running?");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div style={{ maxWidth: 680 }}>
            <div className="page-header">
                <h1>Submit Feedback</h1>
                <p>Share your experience with the driver. Your input is analyzed in real-time and contributes to fleet safety.</p>
            </div>

            <div className="card">
                <div className="form-group">
                    <label>Driver Identifier</label>
                    <input
                        className="input"
                        placeholder="e.g. drv_9921"
                        value={driverId}
                        onChange={(e) => setDriverId(e.target.value)}
                    />
                </div>

                <div className="form-group">
                    <label>Trip Identifier</label>
                    <input
                        className="input"
                        placeholder="e.g. trip_8820"
                        value={tripId}
                        onChange={(e) => setTripId(e.target.value)}
                    />
                </div>

                <div className="form-group">
                    <label>Your Observation</label>
                    <textarea
                        className="textarea"
                        placeholder="Describe the driver's conduct, professionalism, and overall experience during this trip..."
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                    />
                    <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 10 }}>
                        Sentiment is analyzed automatically. Negative patterns trigger a supervisor alert.
                    </div>
                </div>

                <button
                    className="btn btn-primary"
                    onClick={handleSubmit}
                    disabled={submitting}
                    style={{ width: "100%", marginTop: 8 }}
                >
                    {submitting ? (
                        <><Loader2 size={18} className="spin" /> Submitting...</>
                    ) : (
                        "Submit Feedback"
                    )}
                </button>

                {toast && (
                    <div className={`toast toast-${toast.type}`} style={{ marginTop: 24 }}>
                        {toast.msg}
                    </div>
                )}
            </div>
        </div>
    );
}