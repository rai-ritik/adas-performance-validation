from src.scenario_config import get_scenario
from src.data_generation import generate_scenario_telemetry

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ADAS Performance Validation",
    page_icon="🚗",
    layout="wide",
)

st.title("ADAS Performance Validation")
st.caption(
    "Synthetic Pedestrian AEB Performance Investigation & Validation"
)


# ============================================================
# CONSTANTS
# ============================================================

AVAILABLE_SCENARIOS = [
    "P01",
    "P02",
    "P03",
    "P04",
    "P05",
    "P06",
    "P07",
    "P08",
    "P09",
    "P10",
]

REQUIRED_COLUMNS = [
    "scenario_id",
    "timestamp",
    "vehicle_speed_kmh",
    "vehicle_acceleration_ms2",
    "vehicle_yaw_rate_dps",
    "pedestrian_lateral_position_m",
    "pedestrian_longitudinal_position_m",
    "pedestrian_distance_m",
    "relative_closing_speed_ms",
    "ttc_seconds",
    "ground_truth_pedestrian",
    "ground_truth_collision_risk",
    "ground_truth_warning_required",
    "ground_truth_braking_required",
    "pedestrian_detected",
    "detection_confidence",
    "pedestrian_in_path",
    "warning_triggered",
    "brake_triggered",
]

FCW_THRESHOLD = 2.5
AEB_THRESHOLD = 1.5


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_bool(series):
    """
    Convert common boolean representations to True/False.
    """
    if pd.api.types.is_bool_dtype(series):
        return series

    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes", "y", "t"])
    )


def generate_all_scenarios(scenario_ids):
    """
    Generate telemetry for all selected scenarios.
    """

    frames = []

    for scenario_id in scenario_ids:

        scenario = get_scenario(scenario_id)

        telemetry = generate_scenario_telemetry(
            scenario=scenario
        )

        telemetry = telemetry.copy()

        frames.append(telemetry)

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True
    )


def prepare_dataframe(df):
    """
    Validate and prepare telemetry dataframe.
    """

    df = df.copy()

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        st.error("Missing required telemetry columns:")

        for column in missing:
            st.write(f"- `{column}`")

        st.stop()

    boolean_columns = [
        "ground_truth_pedestrian",
        "ground_truth_collision_risk",
        "ground_truth_warning_required",
        "ground_truth_braking_required",
        "pedestrian_detected",
        "pedestrian_in_path",
        "warning_triggered",
        "brake_triggered",
    ]

    for column in boolean_columns:
        df[column] = normalize_bool(df[column])

    numeric_columns = [
        "vehicle_speed_kmh",
        "vehicle_acceleration_ms2",
        "vehicle_yaw_rate_dps",
        "pedestrian_lateral_position_m",
        "pedestrian_longitudinal_position_m",
        "pedestrian_distance_m",
        "relative_closing_speed_ms",
        "ttc_seconds",
        "detection_confidence",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


def get_time_axis(df):
    """
    Convert timestamp into seconds from scenario start.
    """

    try:

        timestamps = pd.to_datetime(
            df["timestamp"]
        )

        elapsed = (
            timestamps - timestamps.iloc[0]
        ).dt.total_seconds()

        return elapsed, "Time since scenario start (s)"

    except Exception:

        elapsed = (
            np.arange(len(df)) / 10.0
        )

        return elapsed, "Time (s)"


def classify_aeb_event(row):
    """
    Basic engineering classification for the critical observation.
    """

    gt_braking = bool(
        row["ground_truth_braking_required"]
    )

    aeb_triggered = bool(
        row["brake_triggered"]
    )

    detected = bool(
        row["pedestrian_detected"]
    )

    confidence = row["detection_confidence"]

    if gt_braking and aeb_triggered:

        return (
            "PASS",
            "AEB triggered when braking was required."
        )

    if gt_braking and not aeb_triggered:

        if not detected:

            return (
                "DETECTION FAILURE",
                "Braking was required, but the pedestrian "
                "was not detected during the critical window."
            )

        if pd.notna(confidence) and confidence < 0.5:

            return (
                "LOW-CONFIDENCE PERCEPTION FAILURE",
                "The pedestrian was detected, but detection "
                "confidence was low during the critical window."
            )

        return (
            "AEB DECISION FAILURE",
            "The pedestrian was detected during the critical "
            "window, but AEB did not trigger."
        )

    if not gt_braking and aeb_triggered:

        return (
            "FALSE POSITIVE BRAKING",
            "AEB triggered although ground truth did not "
            "require braking."
        )

    return (
        "NO AEB EVENT",
        "The selected observation did not require AEB intervention."
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Scenario Configuration")

selected_scenarios = st.sidebar.multiselect(
    "Select scenarios",
    AVAILABLE_SCENARIOS,
    default=AVAILABLE_SCENARIOS,
)

if not selected_scenarios:

    st.warning(
        "Select at least one scenario from the sidebar."
    )

    st.stop()


# ============================================================
# DATA GENERATION
# ============================================================

@st.cache_data
def cached_generation(scenario_ids):

    return generate_all_scenarios(
        scenario_ids
    )


df = cached_generation(
    tuple(selected_scenarios)
)

df = prepare_dataframe(df)


# ============================================================
# OVERVIEW
# ============================================================

st.header("1. Safety Overview")

gt_brake = df[
    "ground_truth_braking_required"
]

aeb_output = df[
    "brake_triggered"
]

tp = int(
    (gt_brake & aeb_output).sum()
)

tn = int(
    (~gt_brake & ~aeb_output).sum()
)

fp = int(
    (~gt_brake & aeb_output).sum()
)

fn = int(
    (gt_brake & ~aeb_output).sum()
)

precision = (
    tp / (tp + fp)
    if (tp + fp) > 0
    else np.nan
)

recall = (
    tp / (tp + fn)
    if (tp + fn) > 0
    else np.nan
)

f1 = (
    2 * precision * recall
    / (precision + recall)
    if (
        pd.notna(precision)
        and pd.notna(recall)
        and (precision + recall) > 0
    )
    else np.nan
)


metrics = st.columns(7)

metrics[0].metric(
    "Observations",
    len(df)
)

metrics[1].metric(
    "Scenarios",
    df["scenario_id"].nunique()
)

metrics[2].metric(
    "AEB TP",
    tp
)

metrics[3].metric(
    "AEB FN",
    fn
)

metrics[4].metric(
    "AEB FP",
    fp
)

metrics[5].metric(
    "Recall",
    f"{recall:.1%}"
    if pd.notna(recall)
    else "N/A"
)

metrics[6].metric(
    "F1",
    f"{f1:.1%}"
    if pd.notna(f1)
    else "N/A"
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

st.subheader("AEB Confusion Matrix")

confusion_matrix = pd.DataFrame(
    [
        [tn, fp],
        [fn, tp],
    ],
    index=[
        "Ground Truth: No Braking",
        "Ground Truth: Braking",
    ],
    columns=[
        "ADAS: No Brake",
        "ADAS: Brake",
    ],
)

st.dataframe(
    confusion_matrix,
    use_container_width=True,
)


# ============================================================
# SCENARIO PERFORMANCE
# ============================================================

st.header("2. Scenario Performance")

scenario_rows = []

for scenario_id, group in df.groupby(
    "scenario_id"
):

    group = group.sort_values(
        "timestamp"
    ).copy()

    gt_braking = group[
        "ground_truth_braking_required"
    ]

    aeb = group[
        "brake_triggered"
    ]

    gt_warning = group[
        "ground_truth_warning_required"
    ]

    warning = group[
        "warning_triggered"
    ]

    valid_ttc = (
        group["ttc_seconds"]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .dropna()
    )

    min_ttc = (
        valid_ttc.min()
        if not valid_ttc.empty
        else np.nan
    )

    min_distance = group[
        "pedestrian_distance_m"
    ].min()

    max_speed = group[
        "vehicle_speed_kmh"
    ].max()

    aeb_required = bool(
        gt_braking.any()
    )

    warning_required = bool(
        gt_warning.any()
    )

    aeb_triggered = bool(
        aeb.any()
    )

    warning_triggered = bool(
        warning.any()
    )

    aeb_fn = bool(
        (gt_braking & ~aeb).any()
    )

    aeb_fp = bool(
        (~gt_braking & aeb).any()
    )

    if not aeb_required:

        aeb_status = (
            "N/A — AEB not exercised"
        )

    elif aeb_fn:

        aeb_status = (
            "FAIL — AEB missed"
        )

    elif aeb_fp:

        aeb_status = (
            "FAIL — unnecessary braking"
        )

    else:

        aeb_status = "PASS"

    scenario_rows.append(
        {
            "Scenario": scenario_id,

            "Min TTC (s)": (
                round(min_ttc, 3)
                if pd.notna(min_ttc)
                else np.nan
            ),

            "Min Distance (m)": (
                round(min_distance, 2)
            ),

            "Max Speed (km/h)": (
                round(max_speed, 1)
            ),

            "Warning Required": (
                "YES"
                if warning_required
                else "NO"
            ),

            "Warning Triggered": (
                "YES"
                if warning_triggered
                else "NO"
            ),

            "AEB Required": (
                "YES"
                if aeb_required
                else "NO"
            ),

            "AEB Triggered": (
                "YES"
                if aeb_triggered
                else "NO"
            ),

            "AEB Status": aeb_status,
        }
    )


scenario_table = pd.DataFrame(
    scenario_rows
)

st.dataframe(
    scenario_table,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "N/A means the scenario did not exercise the relevant "
    "AEB intervention condition. It is not treated as a failure."
)


# ============================================================
# AEB EVENT INVESTIGATOR
# ============================================================

st.header("3. AEB Event Investigator")

investigation_scenario = st.selectbox(
    "Select scenario to investigate",
    selected_scenarios,
    key="aeb_investigation_scenario",
)

event_df = df[
    df["scenario_id"].astype(str)
    == str(investigation_scenario)
].copy()

event_df = event_df.sort_values(
    "timestamp"
)


critical = event_df[
    event_df["ground_truth_braking_required"]
].copy()


if critical.empty:

    st.info(
        "AEB was not exercised in this scenario. "
        "There is no positive AEB event to investigate."
    )

else:

    valid_critical = (
        critical[
            critical["ttc_seconds"].notna()
        ]
        .sort_values("ttc_seconds")
    )

    if valid_critical.empty:

        critical_row = critical.iloc[0]

    else:

        critical_row = valid_critical.iloc[0]


    classification, explanation = (
        classify_aeb_event(
            critical_row
        )
    )


    st.subheader(
        "Critical Event"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    ttc = critical_row[
        "ttc_seconds"
    ]

    distance = critical_row[
        "pedestrian_distance_m"
    ]

    speed = critical_row[
        "vehicle_speed_kmh"
    ]

    confidence = critical_row[
        "detection_confidence"
    ]

    aeb_triggered = bool(
        critical_row[
            "brake_triggered"
        ]
    )


    c1.metric(
        "Minimum TTC",
        (
            f"{ttc:.3f} s"
            if pd.notna(ttc)
            else "N/A"
        ),
    )

    c2.metric(
        "Distance",
        (
            f"{distance:.2f} m"
            if pd.notna(distance)
            else "N/A"
        ),
    )

    c3.metric(
        "Vehicle Speed",
        (
            f"{speed:.1f} km/h"
            if pd.notna(speed)
            else "N/A"
        ),
    )

    c4.metric(
        "Detection Confidence",
        (
            f"{confidence:.2f}"
            if pd.notna(confidence)
            else "N/A"
        ),
    )

    c5.metric(
        "AEB",
        (
            "TRIGGERED"
            if aeb_triggered
            else "NOT TRIGGERED"
        ),
    )


    st.subheader(
        "Engineering Classification"
    )

    if classification == "PASS":

        st.success(
            classification
        )

    elif classification.startswith("FAIL"):

        st.error(
            classification
        )

    elif "FAILURE" in classification:

        st.error(
            classification
        )

    else:

        st.warning(
            classification
        )

    st.write(
        explanation
    )


    st.subheader(
        "Critical Telemetry"
    )

    investigation_columns = [
        "timestamp",
        "vehicle_speed_kmh",
        "pedestrian_distance_m",
        "relative_closing_speed_ms",
        "ttc_seconds",
        "pedestrian_detected",
        "detection_confidence",
        "pedestrian_in_path",
        "ground_truth_braking_required",
        "brake_triggered",
    ]

    st.dataframe(
        critical[
            investigation_columns
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# TELEMETRY INVESTIGATION
# ============================================================

st.header("4. Telemetry Investigation")

plot_scenario = st.selectbox(
    "Select scenario for telemetry analysis",
    selected_scenarios,
    key="telemetry_scenario",
)

plot_df = df[
    df["scenario_id"].astype(str)
    == str(plot_scenario)
].copy()

plot_df = plot_df.sort_values(
    "timestamp"
)

if not plot_df.empty:

    x, x_title = get_time_axis(
        plot_df
    )


    # --------------------------------------------------------
    # TTC
    # --------------------------------------------------------

    st.subheader(
        "Time-to-Collision"
    )

    fig_ttc = go.Figure()

    fig_ttc.add_trace(
        go.Scatter(
            x=x,
            y=plot_df["ttc_seconds"],
            name="TTC",
            mode="lines",
        )
    )

    fig_ttc.add_hline(
        y=FCW_THRESHOLD,
        line_dash="dash",
        annotation_text="FCW = 2.5 s",
    )

    fig_ttc.add_hline(
        y=AEB_THRESHOLD,
        line_dash="dash",
        annotation_text="AEB = 1.5 s",
    )

    fig_ttc.update_layout(
        xaxis_title=x_title,
        yaxis_title="TTC (s)",
        height=420,
    )

    st.plotly_chart(
        fig_ttc,
        use_container_width=True,
    )


    # --------------------------------------------------------
    # VEHICLE / PEDESTRIAN
    # --------------------------------------------------------

    st.subheader(
        "Vehicle and Pedestrian Dynamics"
    )

    fig_dynamics = go.Figure()

    fig_dynamics.add_trace(
        go.Scatter(
            x=x,
            y=plot_df[
                "vehicle_speed_kmh"
            ],
            name="Vehicle speed (km/h)",
            mode="lines",
        )
    )

    fig_dynamics.add_trace(
        go.Scatter(
            x=x,
            y=plot_df[
                "pedestrian_distance_m"
            ],
            name="Pedestrian distance (m)",
            mode="lines",
        )
    )

    fig_dynamics.update_layout(
        xaxis_title=x_title,
        yaxis_title="Value",
        height=420,
    )

    st.plotly_chart(
        fig_dynamics,
        use_container_width=True,
    )


    # --------------------------------------------------------
    # PERCEPTION / AEB
    # --------------------------------------------------------

    st.subheader(
        "Perception vs AEB Decision"
    )

    fig_decision = go.Figure()

    fig_decision.add_trace(
        go.Scatter(
            x=x,
            y=plot_df[
                "detection_confidence"
            ],
            name="Detection confidence",
            mode="lines",
        )
    )

    fig_decision.add_trace(
        go.Scatter(
            x=x,
            y=plot_df[
                "pedestrian_detected"
            ].astype(int),
            name="Pedestrian detected",
            mode="lines",
            line_shape="hv",
        )
    )

    fig_decision.add_trace(
        go.Scatter(
            x=x,
            y=plot_df[
                "ground_truth_braking_required"
            ].astype(int),
            name="GT braking required",
            mode="lines",
            line_shape="hv",
        )
    )

    fig_decision.add_trace(
        go.Scatter(
            x=x,
            y=plot_df[
                "brake_triggered"
            ].astype(int),
            name="AEB brake triggered",
            mode="lines",
            line_shape="hv",
        )
    )

    fig_decision.update_layout(
        xaxis_title=x_title,
        yaxis_title="State / Confidence",
        height=450,
    )

    st.plotly_chart(
        fig_decision,
        use_container_width=True,
    )


# ============================================================
# FAILURE INVESTIGATION
# ============================================================

st.header("5. Failure Investigation")

failure_rows = []

for scenario_id, group in df.groupby(
    "scenario_id"
):

    gt = group[
        "ground_truth_braking_required"
    ]

    aeb = group[
        "brake_triggered"
    ]

    false_negative_rows = group[
        gt & ~aeb
    ]

    for _, row in false_negative_rows.iterrows():

        failure_rows.append(
            {
                "Scenario": scenario_id,
                "Timestamp": row[
                    "timestamp"
                ],
                "TTC (s)": row[
                    "ttc_seconds"
                ],
                "Distance (m)": row[
                    "pedestrian_distance_m"
                ],
                "Vehicle Speed (km/h)": row[
                    "vehicle_speed_kmh"
                ],
                "Detected": row[
                    "pedestrian_detected"
                ],
                "Confidence": row[
                    "detection_confidence"
                ],
                "GT Braking": row[
                    "ground_truth_braking_required"
                ],
                "AEB": row[
                    "brake_triggered"
                ],
            }
        )


if failure_rows:

    failure_df = pd.DataFrame(
        failure_rows
    )

    st.warning(
        f"{len(failure_df)} AEB false-negative "
        "telemetry samples found."
    )

    st.dataframe(
        failure_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
        **Investigation principle**

        A missed AEB event should not immediately be
        interpreted as an AEB decision failure.

        First investigate:

        1. Was the pedestrian detected?
        2. What was the detection confidence?
        3. Was the pedestrian in path?
        4. What was the TTC?
        5. Was braking required by ground truth?
        6. Did the AEB decision trigger?

        This separates perception failures from
        decision-layer failures.
        """
    )

else:

    st.success(
        "No AEB false-negative telemetry samples "
        "found in the selected scenarios."
    )


# ============================================================
# DATA QUALITY
# ============================================================

st.header("6. Data Quality")

confidence_invalid = (
    (
        df["detection_confidence"] < 0
    )
    |
    (
        df["detection_confidence"] > 1
    )
).sum()

quality_table = pd.DataFrame(
    {
        "Check": [
            "Required columns",
            "Missing vehicle speed",
            "Missing pedestrian distance",
            "Missing TTC",
            "Invalid confidence",
            "Duplicate rows",
        ],

        "Result": [
            "PASS",

            int(
                df[
                    "vehicle_speed_kmh"
                ].isna().sum()
            ),

            int(
                df[
                    "pedestrian_distance_m"
                ].isna().sum()
            ),

            int(
                df[
                    "ttc_seconds"
                ].isna().sum()
            ),

            int(
                confidence_invalid
            ),

            int(
                df.duplicated().sum()
            ),
        ],
    }
)

st.dataframe(
    quality_table,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Synthetic portfolio validation environment. "
    "Project thresholds are demonstration assumptions "
    "and do not represent Toyota, UNECE, Euro NCAP, "
    "regulatory, or production requirements."
)