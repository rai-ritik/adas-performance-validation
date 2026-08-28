
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="ADAS Performance Validation", page_icon="🚗", layout="wide")

st.title("ADAS Performance Validation")
st.caption("Synthetic pedestrian AEB performance investigation dashboard")

REQUIRED = [
    "scenario_id", "timestamp", "vehicle_speed_kmh", "pedestrian_distance_m",
    "relative_closing_speed_ms", "ttc_seconds",
    "ground_truth_collision_risk", "ground_truth_warning_required",
    "ground_truth_braking_required", "pedestrian_detected",
    "detection_confidence", "warning_triggered", "brake_triggered"
]

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

def bool_col(s):
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().isin(["true", "1", "yes"])

uploaded = st.sidebar.file_uploader("Upload telemetry CSV", type=["csv"])

if uploaded is None:
    st.info("Upload the generated ADAS telemetry CSV to begin.")
    st.markdown("""
    ### Expected project data
    The dashboard is designed around the existing ADAS validation data model:
    - physics: speed, distance, closing speed, TTC
    - ground truth: collision / warning / braking requirements
    - perception: detection and confidence
    - ADAS outputs: warning and braking
    - validation: TP/TN/FP/FN and failure classification

    **Project assumptions:** FCW TTC = 2.5 s, AEB TTC = 1.5 s, telemetry = 10 Hz.
    These are synthetic portfolio assumptions, not production or regulatory thresholds.
    """)
    st.stop()

df = load_csv(uploaded).copy()

missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    st.error("Missing required columns:")
    st.code("\n".join(missing))
    st.stop()

# Normalize booleans
for c in [
    "ground_truth_collision_risk", "ground_truth_warning_required",
    "ground_truth_braking_required", "pedestrian_detected",
    "warning_triggered", "brake_triggered"
]:
    df[c] = bool_col(df[c])

# Numeric conversion
for c in ["vehicle_speed_kmh", "pedestrian_distance_m",
          "relative_closing_speed_ms", "ttc_seconds", "detection_confidence"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Scenario filter
scenarios = sorted(df["scenario_id"].dropna().astype(str).unique())
selected = st.sidebar.multiselect("Scenarios", scenarios, default=scenarios)
view = df[df["scenario_id"].astype(str).isin(selected)].copy()

# ---------------- Overview ----------------
st.header("1. Safety Overview")

gt_brake = view["ground_truth_braking_required"]
aeb = view["brake_triggered"]

tp = int((gt_brake & aeb).sum())
tn = int((~gt_brake & ~aeb).sum())
fp = int((~gt_brake & aeb).sum())
fn = int((gt_brake & ~aeb).sum())

precision = tp / (tp + fp) if tp + fp else np.nan
recall = tp / (tp + fn) if tp + fn else np.nan
f1 = 2 * precision * recall / (precision + recall) if precision + recall else np.nan

cols = st.columns(7)
cards = [
    ("Observations", len(view)),
    ("Scenarios", view["scenario_id"].nunique()),
    ("AEB TP", tp),
    ("AEB FN", fn),
    ("AEB FP", fp),
    ("Recall", f"{recall:.1%}" if pd.notna(recall) else "N/A"),
    ("F1", f"{f1:.1%}" if pd.notna(f1) else "N/A"),
]
for col, (label, value) in zip(cols, cards):
    col.metric(label, value)

st.subheader("AEB Confusion Matrix")
cm = pd.DataFrame(
    [[tn, fp], [fn, tp]],
    index=["GT: No Braking", "GT: Braking"],
    columns=["ADAS: No Brake", "ADAS: Brake"]
)
st.dataframe(cm, use_container_width=True)

# ---------------- Scenario ----------------
st.header("2. Scenario Performance")

scenario_rows = []
for sid, g in view.groupby("scenario_id"):
    gt = g["ground_truth_braking_required"]
    out = g["brake_triggered"]
    n_gt = int(gt.sum())
    n_tp = int((gt & out).sum())
    n_fn = int((gt & ~out).sum())
    n_fp = int((~gt & out).sum())
    min_ttc = g["ttc_seconds"].replace([np.inf, -np.inf], np.nan).min()

    scenario_rows.append({
        "scenario_id": sid,
        "observations": len(g),
        "min_ttc_s": min_ttc,
        "GT braking samples": n_gt,
        "AEB TP": n_tp,
        "AEB FN": n_fn,
        "AEB FP": n_fp,
        "exercised": "YES" if n_gt > 0 else "N/A"
    })

scenario_table = pd.DataFrame(scenario_rows).sort_values("scenario_id")
st.dataframe(scenario_table, use_container_width=True, hide_index=True)

# ---------------- Telemetry ----------------
st.header("3. Telemetry Investigation")

scenario_for_plot = st.selectbox("Select scenario", scenarios)
g = view[view["scenario_id"].astype(str) == scenario_for_plot].copy()

if not g.empty:
    try:
        time = pd.to_datetime(g["timestamp"])
        x = (time - time.iloc[0]).dt.total_seconds()
        x_title = "Time since scenario start (s)"
    except Exception:
        x = np.arange(len(g)) / 10.0
        x_title = "Sample time (s)"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=g["ttc_seconds"], name="TTC", mode="lines"))
    fig.add_hline(y=2.5, line_dash="dash", annotation_text="FCW threshold")
    fig.add_hline(y=1.5, line_dash="dash", annotation_text="AEB threshold")
    fig.update_layout(
        title="Time-to-Collision",
        xaxis_title=x_title,
        yaxis_title="TTC (s)",
        height=420
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=x, y=g["vehicle_speed_kmh"], name="Vehicle speed", mode="lines"))
    fig2.add_trace(go.Scatter(x=x, y=g["pedestrian_distance_m"], name="Pedestrian distance", mode="lines"))
    fig2.update_layout(
        title="Vehicle / Target Dynamics",
        xaxis_title=x_title,
        yaxis_title="Value",
        height=420
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=x, y=g["detection_confidence"], name="Detection confidence", mode="lines"))
    fig3.add_trace(go.Scatter(
        x=x, y=g["ground_truth_braking_required"].astype(int),
        name="GT braking required", mode="lines", line_shape="hv"
    ))
    fig3.add_trace(go.Scatter(
        x=x, y=g["brake_triggered"].astype(int),
        name="AEB brake triggered", mode="lines", line_shape="hv"
    ))
    fig3.update_layout(
        title="Perception vs AEB Decision",
        xaxis_title=x_title,
        yaxis_title="State / confidence",
        height=420
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- Root cause ----------------
st.header("4. Failure Investigation")

failures = []
for sid, g in view.groupby("scenario_id"):
    gt = g["ground_truth_braking_required"]
    out = g["brake_triggered"]
    fn_rows = g[gt & ~out]

    for _, r in fn_rows.iterrows():
        failures.append({
            "scenario_id": sid,
            "timestamp": r["timestamp"],
            "TTC_s": r["ttc_seconds"],
            "distance_m": r["pedestrian_distance_m"],
            "detected": r["pedestrian_detected"],
            "confidence": r["detection_confidence"],
            "GT_braking": r["ground_truth_braking_required"],
            "AEB": r["brake_triggered"],
        })

if failures:
    failure_df = pd.DataFrame(failures)
    st.warning(f"{len(failure_df)} AEB false-negative samples found.")
    st.dataframe(failure_df, use_container_width=True, hide_index=True)

    st.markdown("**Investigation logic:** first check whether the target was detected and whether confidence was adequate during the critical TTC window. A perception miss should be distinguished from a decision-layer failure.")
else:
    st.success("No AEB false-negative samples found in the selected scenarios.")

# ---------------- Data quality ----------------
st.header("5. Data Quality")
dq = pd.DataFrame({
    "Check": [
        "Required columns present",
        "Missing vehicle speed",
        "Missing TTC",
        "Confidence outside [0, 1]",
        "Duplicate rows",
    ],
    "Result": [
        "PASS",
        int(view["vehicle_speed_kmh"].isna().sum()),
        int(view["ttc_seconds"].isna().sum()),
        int(((view["detection_confidence"] < 0) | (view["detection_confidence"] > 1)).sum()),
        int(view.duplicated().sum()),
    ]
})
st.dataframe(dq, use_container_width=True, hide_index=True)

st.caption("This dashboard is an analysis/validation interface for the synthetic portfolio project. It does not establish production ADAS or regulatory compliance.")
