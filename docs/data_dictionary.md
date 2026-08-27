# Pedestrian AEB Performance Analytics & Validation Platform

## Data Dictionary

**Project:** ADAS Performance Analytics & Validation Platform  
**Focus:** Pedestrian Automatic Emergency Braking (AEB)  
**Repository:** `adas-performance-validation`  
**Status:** Synthetic validation simulation

---

## 1. Purpose

This document defines the data contract for the synthetic pedestrian/AEB telemetry dataset used by the project.

The dataset represents timestamped observations of an ego vehicle and a pedestrian target within a defined driving scenario. A scenario contains multiple observations over time.

The dataset is designed to support:

- ADAS performance analysis
- data-quality validation
- feature engineering
- pedestrian detection evaluation
- Forward Collision Warning (FCW) evaluation
- AEB braking evaluation
- scenario analysis
- statistical analysis
- SQL analytics
- Power BI reporting
- reproducible validation workflows

> **Important:** This is a synthetic simulation created for portfolio and learning purposes. Thresholds, scenario rules, and simulated ADAS behavior are project-defined assumptions. They are **not** official Toyota, Euro NCAP, UNECE, regulatory, or OEM requirements.

---

# 2. Dataset Grain

One row represents:

> **One timestamped observation of an ego vehicle and a pedestrian target within a defined driving scenario.**

A single scenario contains many timestamped observations.

The planned initial dataset size is **10,000+ observations** so that scenario-level and statistical analysis are meaningful.

---

# 3. Field Categories

The dataset is organized into the following logical groups:

| Category | Purpose |
|---|---|
| Identification | Identify observations, scenarios, vehicles, and pedestrians |
| Ego Vehicle | Describe ego-vehicle motion |
| Pedestrian | Describe pedestrian state and relationship to the ego vehicle |
| Environment | Describe external driving conditions |
| Ground Truth | Represent the simulated reference/actual scenario state |
| ADAS Output | Represent simulated perception, warning, and braking outputs |
| Derived Features | Calculated variables used for analysis and validation |
| Validation | Classify system performance and failures |

---

# 4. Identification Fields

## 4.1 `event_id`

| Property | Definition |
|---|---|
| Type | string / categorical identifier |
| Unit | None |
| Required | Yes |
| Null allowed | No |
| Uniqueness | Must be unique |
| Example | `E000001` |

### Meaning

Unique identifier for each timestamped observation.

### Data-quality rules

- Must not be null.
- Must be unique across the dataset.
- Must not contain accidental duplicates.

---

## 4.2 `timestamp`

| Property | Definition |
|---|---|
| Type | datetime |
| Unit | timestamp / seconds through elapsed time |
| Required | Yes |
| Null allowed | No |
| Example | `2026-01-01 08:00:00.100` |

### Meaning

Timestamp associated with the telemetry observation.

### Data-quality rules

Check for:

- invalid datetime values
- duplicate timestamps within a scenario
- out-of-order timestamps
- missing observations
- unexpected time gaps

---

## 4.3 `scenario_id`

| Property | Definition |
|---|---|
| Type | categorical string |
| Unit | None |
| Required | Yes |
| Null allowed | No |
| Allowed values | `P01`–`P10` |
| Example | `P02` |

### Meaning

Identifies the driving scenario from which the observation was generated.

### Scenario mapping

| ID | Scenario | Objective |
|---|---|---|
| `P01` | Normal Crossing | Baseline pedestrian detection/AEB |
| `P02` | Sudden Crossing | Reaction to rapid pedestrian entry |
| `P03` | Night Crossing | Low-light performance |
| `P04` | Rain Crossing | Rain/wet-road performance |
| `P05` | Partial Occlusion | Partially visible pedestrian |
| `P06` | Outside Path | False-positive/unnecessary intervention |
| `P07` | Multiple Pedestrians | Multiple-target handling |
| `P08` | High-Speed Approach | High-speed collision risk |
| `P09` | Fog / Low Visibility | Degraded visibility |
| `P10` | Safe Avoidance | Avoid unnecessary AEB |

---

## 4.4 `vehicle_id`

| Property | Definition |
|---|---|
| Type | categorical string |
| Unit | None |
| Required | Yes |
| Null allowed | No |
| Example | `V001` |

### Meaning

Identifier for the ego vehicle generating the telemetry.

---

## 4.5 `pedestrian_id`

| Property | Definition |
|---|---|
| Type | categorical string |
| Unit | None |
| Required | Context-dependent |
| Null allowed | Yes |
| Example | `PED001` |

### Meaning

Identifier for the pedestrian target associated with the observation.

### Rule

May be null when there is no relevant pedestrian for the observation.

---

# 5. Ego Vehicle Variables

## 5.1 `vehicle_speed_kmh`

| Property | Definition |
|---|---|
| Type | float |
| Unit | km/h |
| Required | Yes |
| Null allowed | No for valid telemetry |
| Valid project range | `0 <= value <= 150` |
| Example | `42.5` |

### Meaning

Longitudinal speed of the ego vehicle.

### Validation rules

- Must be numeric.
- Must be within the project validation range.
- Negative speed values are invalid for this simplified longitudinal model.

---

## 5.2 `vehicle_acceleration_ms2`

| Property | Definition |
|---|---|
| Type | float |
| Unit | m/s² |
| Required | Yes for valid telemetry |
| Null allowed | Possible after failure/data-quality injection |
| Valid project range | `-10 <= value <= 5` |
| Example | `-3.2` |

### Meaning

Longitudinal acceleration or deceleration of the ego vehicle.

### Interpretation

- Positive value → acceleration
- Zero → approximately constant speed
- Negative value → deceleration/braking

### Validation rules

Values outside the project range are treated as invalid.

---

## 5.3 `vehicle_yaw_rate_dps`

| Property | Definition |
|---|---|
| Type | float |
| Unit | degrees/second |
| Required | Yes for valid telemetry |
| Null allowed | Possible after failure/data-quality injection |
| Valid project range | `-50 <= value <= 50` |
| Example | `3.5` |

### Meaning

Vehicle rotational rate around the vertical axis.

### Purpose

Used to provide contextual information about turning or curved-road behavior.

---

# 6. Pedestrian Variables

## 6.1 `pedestrian_distance_m`

| Property | Definition |
|---|---|
| Type | float |
| Unit | m |
| Required | Yes when a relevant pedestrian exists |
| Null allowed | Context-dependent |
| Valid project range | `0 < value <= 150` |
| Example | `18.4` |

### Meaning

Distance between the ego vehicle and the pedestrian reference point.

### Validation rules

- Must be positive when present.
- Negative values are invalid.
- Values above the project maximum should be investigated.

---

## 6.2 `pedestrian_relative_speed_ms`

| Property | Definition |
|---|---|
| Type | float |
| Unit | m/s |
| Required | Context-dependent |
| Null allowed | Possible |
| Example | `8.1` |

### Meaning

Relative velocity between the ego vehicle and pedestrian along the relevant collision direction.

### Interpretation

- Positive → closing / increasing collision risk
- Zero → no relative movement in the modeled collision direction
- Negative → separating

This field is used in collision-risk and TTC analysis.

---

## 6.3 `pedestrian_lateral_position_m`

| Property | Definition |
|---|---|
| Type | float |
| Unit | m |
| Required | Yes for modeled pedestrian trajectories |
| Example | `0.25` |

### Meaning

Pedestrian position relative to the ego vehicle's lateral centerline.

### Interpretation

- `0 m` → directly on the modeled vehicle centerline/path
- Positive → one side of the vehicle
- Negative → opposite side

The sign convention is project-defined and must remain consistent throughout the dataset.

---

## 6.4 `pedestrian_longitudinal_position_m`

| Property | Definition |
|---|---|
| Type | float |
| Unit | m |
| Required | Yes for modeled pedestrian trajectories |
| Example | `15.2` |

### Meaning

Pedestrian position along the modeled longitudinal direction relative to the ego vehicle.

### Purpose

Used together with distance, relative movement, and lateral position to reconstruct simplified pedestrian/ego geometry.

---

## 6.5 `pedestrian_lane_relation`

| Property | Definition |
|---|---|
| Type | categorical |
| Unit | None |
| Allowed values | `same_path`, `crossing_path`, `adjacent`, `outside_path` |
| Required | Yes for relevant pedestrian states |

### Meaning

Relationship between the pedestrian and the ego vehicle's predicted/relevant path.

### Categories

| Value | Meaning |
|---|---|
| `same_path` | Pedestrian occupies the modeled vehicle path |
| `crossing_path` | Pedestrian is moving across the modeled vehicle path |
| `adjacent` | Pedestrian is near but not currently in the modeled path |
| `outside_path` | Pedestrian is outside the relevant path |

---

## 6.6 `pedestrian_type`

| Property | Definition |
|---|---|
| Type | categorical |
| Unit | None |
| Allowed values | `adult`, `child`, `unknown` |
| Required | Yes for modeled targets |

### Meaning

Broad simulated pedestrian category used for scenario analysis.

### Purpose

Allows performance comparisons across simulated target types.

---

## 6.7 `pedestrian_visibility`

| Property | Definition |
|---|---|
| Type | categorical |
| Unit | None |
| Allowed values | `clear`, `partial`, `occluded` |
| Required | Yes for relevant targets |

### Meaning

Represents how visible the pedestrian is to the simulated perception system.

### Purpose

Used to study perception difficulty and detection failures.

---

# 7. Environment Variables

## 7.1 `weather`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `dry`, `rain`, `fog` |
| Required | Yes |

### Meaning

Simulated environmental weather condition.

---

## 7.2 `lighting`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `day`, `night` |
| Required | Yes |

### Meaning

Lighting condition during the scenario.

---

## 7.3 `road_condition`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `dry`, `wet`, `low_friction` |
| Required | Yes |

### Meaning

Simulated road-surface condition.

### Purpose

Used for contextual analysis of vehicle response and braking scenarios.

---

## 7.4 `road_type`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `urban`, `rural`, `highway` |
| Required | Yes |

### Meaning

Broad road-environment category.

---

## 7.5 `traffic_density`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `low`, `medium`, `high` |
| Required | Yes |

### Meaning

Simulated surrounding traffic density.

### Purpose

Provides contextual information for multiple-object and perception-difficulty analysis.

---

# 8. Ground Truth Variables

Ground truth represents the modeled reference state of the scenario. It is the validation reference and must be generated independently from simulated ADAS outputs.

## 8.1 `ground_truth_pedestrian`

| Property | Definition |
|---|---|
| Type | boolean |
| Unit | None |
| Required | Yes |
| Allowed values | `True`, `False` |

### Meaning

Indicates whether a relevant pedestrian is actually present according to the scenario ground truth.

---

## 8.2 `ground_truth_collision_risk`

| Property | Definition |
|---|---|
| Type | boolean |
| Unit | None |
| Required | Yes |
| Allowed values | `True`, `False` |

### Meaning

Indicates whether the pedestrian represents a meaningful collision threat under the project's scenario logic.

### Important

This label is based on project-defined simulation rules rather than a production collision-prediction algorithm.

---

## 8.3 `ground_truth_warning_required`

| Property | Definition |
|---|---|
| Type | boolean |
| Unit | None |
| Required | Yes |
| Allowed values | `True`, `False` |

### Meaning

Indicates whether an FCW warning should be issued at that observation according to the project-defined ground-truth rules.

---

## 8.4 `ground_truth_braking_required`

| Property | Definition |
|---|---|
| Type | boolean |
| Unit | None |
| Required | Yes |
| Allowed values | `True`, `False` |

### Meaning

Indicates whether AEB braking should be triggered at that observation according to project-defined validation logic.

### Important

This threshold is a synthetic simulation rule and must not be represented as an official OEM or regulatory requirement.

---

# 9. ADAS System Output Variables

These fields represent the behavior of the **simulated ADAS system**.

They are intentionally imperfect so that the validation pipeline has meaningful failures to identify.

## 9.1 `pedestrian_detected`

| Property | Definition |
|---|---|
| Type | boolean |
| Unit | None |
| Required | Yes |
| Allowed values | `True`, `False` |

### Meaning

Indicates whether the simulated ADAS perception system detected the relevant pedestrian.

---

## 9.2 `detection_confidence`

| Property | Definition |
|---|---|
| Type | float |
| Unit | probability-like score |
| Valid range | `0 <= value <= 1` |
| Example | `0.91` |

### Meaning

Simulated confidence associated with the pedestrian detection.

### Important

Confidence is **not equivalent to correctness**. The simulation may produce high-confidence incorrect detections to support false-positive analysis.

---

## 9.3 `warning_triggered`

| Property | Definition |
|---|---|
| Type | boolean |
| Unit | None |
| Required | Yes |
| Allowed values | `True`, `False` |

### Meaning

Indicates whether the simulated FCW warning was triggered.

---

## 9.4 `brake_triggered`

| Property | Definition |
|---|---|
| Type | boolean |
| Unit | None |
| Required | Yes |
| Allowed values | `True`, `False` |

### Meaning

Indicates whether the simulated AEB braking action was triggered.

---

# 10. Derived Features

Derived features are calculated by the project pipeline rather than treated as primary raw measurements.

## 10.1 `relative_closing_speed_ms`

| Property | Definition |
|---|---|
| Type | float |
| Unit | m/s |
| Derived | Yes |

### Meaning

Relative velocity used for simplified collision-risk analysis.

### Conceptual formulation

```text
relative_closing_speed = ego_vehicle_velocity - pedestrian_velocity_component
```

### Interpretation

- Positive → closing
- Zero → approximately no closing
- Negative → separating

The exact implementation will be defined in `src/feature_engineering.py`.

---

## 10.2 `ttc_seconds`

| Property | Definition |
|---|---|
| Type | float |
| Unit | seconds |
| Derived | Yes |
| Example | `2.0` |

### Meaning

Simplified Time-to-Collision (TTC) indicator.

### Formula

```text
TTC = pedestrian_distance_m / relative_closing_speed_ms
```

### Example

```text
Distance = 20 m
Closing speed = 10 m/s

TTC = 20 / 10 = 2 seconds
```

### Edge case

When the relative closing speed is zero or negative, the simplified model does not represent a closing collision state. In those cases:

```text
ttc_seconds = NaN
```

or another explicitly documented non-collision representation.

### Important limitation

TTC is a simplified collision-risk indicator. It does not represent a complete production AEB algorithm.

---

## 10.3 `warning_lead_time_seconds`

| Property | Definition |
|---|---|
| Type | float |
| Unit | seconds |
| Derived | Yes |

### Meaning

Time between the simulated ADAS warning and the defined critical event.

### Formula

```text
warning_lead_time = critical_event_time - warning_time
```

### Example

```text
Warning time       = 10.0 s
Critical event     = 12.4 s

Lead time          = 2.4 s
```

### Interpretation

A larger positive lead time generally means the warning occurred earlier relative to the project-defined critical event.

---

# 11. Validation Classification Fields

These fields compare the simulated ADAS output against ground truth.

## 11.1 `detection_result`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `TP`, `TN`, `FP`, `FN` |

### Classification

| Result | Condition |
|---|---|
| `TP` | Relevant pedestrian exists and system detects it |
| `TN` | No relevant pedestrian and system does not detect one |
| `FP` | System detects a pedestrian when it should not |
| `FN` | Relevant pedestrian exists but system fails to detect it |

---

## 11.2 `warning_result`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `TP`, `TN`, `FP`, `FN` |

### Classification

| Result | Condition |
|---|---|
| `TP` | Warning required and warning triggered |
| `TN` | Warning not required and warning not triggered |
| `FP` | Warning triggered when not required |
| `FN` | Warning required but warning not triggered |

---

## 11.3 `braking_result`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `TP`, `TN`, `FP`, `FN` |

### Classification

The same confusion-matrix logic is applied to AEB braking:

| Result | Condition |
|---|---|
| `TP` | Braking required and braking triggered |
| `TN` | Braking not required and braking not triggered |
| `FP` | Braking triggered when not required |
| `FN` | Braking required but braking not triggered |

---

## 11.4 `validation_result`

| Property | Definition |
|---|---|
| Type | categorical |
| Allowed values | `PASS`, `FAIL`, `WARNING_LATE`, `DETECTION_FAILURE`, `FALSE_POSITIVE`, `FALSE_NEGATIVE` |

### Meaning

Overall classification assigned by the validation pipeline based on the observed system behavior and project-defined validation logic.

### Implementation

The exact classification logic will be implemented in:

```text
src/validation.py
```

---

## 11.5 `failure_type`

| Property | Definition |
|---|---|
| Type | categorical |
| Unit | None |
| Allowed values | `none`, `detection_failure`, `false_positive_detection`, `warning_missed`, `warning_late`, `braking_missed`, `false_positive_warning`, `false_positive_braking`, `sensor_data_quality` |

### Meaning

Provides a more specific explanation of a validation failure.

### Purpose

The goal is to move from:

> "The system failed."

to:

> "Most failures occurred during night-time pedestrian crossing scenarios."

This supports engineering-oriented root-cause analysis.

---

# 12. Validation Metrics Supported by the Dataset

The dataset should allow calculation of the following metrics.

## Detection metrics

- True positives
- True negatives
- False positives
- False negatives
- Precision
- Recall
- F1 score
- False-positive rate
- False-negative rate

## Warning metrics

- Warning true-positive rate
- Warning false-positive rate
- Warning false-negative rate
- Warning lead time
- Median warning lead time
- Warning lead-time percentiles

## AEB metrics

- Braking true-positive rate
- Braking false-positive rate
- Braking false-negative rate
- Missed braking events
- Unnecessary braking events

## Risk metrics

- TTC distribution
- TTC at warning
- TTC at braking
- TTC by scenario
- TTC by vehicle speed

---

# 13. Project Validation Targets

These are **demonstration targets defined by this portfolio project**.

They must never be represented as official automotive, Toyota, Euro NCAP, regulatory, or OEM thresholds.

| Metric | Project Target |
|---|---:|
| Pedestrian detection recall | `>= 95%` |
| False-positive detection rate | `<= 5%` |
| Warning false-negative rate | `<= 3%` |
| Median warning lead time | `>= 2.0 s` |
| Critical-event detection | `>= 98%` |

The validation pipeline will compare measured dataset performance against these project-defined targets.

---

# 14. Data Quality Contract

Before analysis, the pipeline must verify the following dimensions.

## 14.1 Completeness

Important non-null fields include:

```text
event_id
timestamp
scenario_id
vehicle_id
vehicle_speed_kmh
```

Additional fields may be conditionally required depending on scenario state.

---

## 14.2 Range validity

Examples:

```text
vehicle_speed_kmh >= 0
0 < pedestrian_distance_m <= 150
0 <= detection_confidence <= 1
-10 <= vehicle_acceleration_ms2 <= 5
-50 <= vehicle_yaw_rate_dps <= 50
```

---

## 14.3 Uniqueness

```text
event_id must be unique
```

Duplicate `event_id` values represent a data-quality problem.

---

## 14.4 Timestamp quality

The pipeline should check for:

- duplicate timestamps
- out-of-order timestamps
- missing timestamps/observations
- unexpected time gaps
- inconsistent sampling intervals

---

## 14.5 Logical consistency

The pipeline should investigate inconsistent combinations such as:

```text
warning_triggered = True
```

without a corresponding valid warning event under the project logic.

Also investigate cases such as:

```text
brake_triggered = True
and
ground_truth_braking_required = False
```

which may indicate an unnecessary intervention or false-positive braking event.

---

# 15. Intentionally Injected Data-Quality Problems

The synthetic data generator should intentionally introduce a controlled number of realistic data-quality issues.

Planned examples:

```text
missing values
duplicate observations
invalid vehicle speeds
negative distances
timestamp anomalies
sensor dropouts
low-confidence detections
inconsistent records
```

The exact injection rates will be defined in the data-generation implementation and documented there.

The purpose is to demonstrate that the analytics pipeline can identify and handle imperfect data rather than relying on an unrealistically clean dataset.

---

# 16. Scenario Coverage

The final synthetic dataset should contain enough observations for each scenario to support comparative analysis.

The generator should preserve meaningful differences between scenarios without changing the underlying data contract.

### Scenario-level analysis questions

- Which scenario produces the most detection failures?
- Does sudden crossing increase missed warnings?
- Does occlusion increase missed detections?
- Does night operation reduce detection performance?
- Does fog increase false negatives?
- Does high speed reduce available warning lead time?
- Does the safe-avoidance scenario produce unnecessary AEB interventions?

---

# 17. Statistical Analysis Supported

The dataset should support questions such as:

> Does rain significantly affect pedestrian detection performance?

> Does vehicle speed affect warning lead time?

> Are scenario-level performance differences statistically significant?

Potential variables for comparison include:

- weather
- lighting
- visibility
- road condition
- vehicle speed
- TTC
- scenario
- pedestrian type

The statistical methodology will be documented separately in the project methodology and analysis notebooks.

---

# 18. SQL Analytical Model

The telemetry/validation dataset can later be transformed into analytical tables such as:

```text
vehicles
scenarios
pedestrians
telemetry
detections
warnings
braking_events
environment
validation_results
```

The exact relational design will be documented in:

```text
sql/schema.sql
```

and the analytical queries in:

```text
sql/analysis_queries.sql
sql/validation_queries.sql
```

---

# 19. Python Source Mapping

Production data logic will belong in `src/`, while notebooks will primarily be used for exploration and interpretation.

| File | Responsibility |
|---|---|
| `src/data_generation.py` | Synthetic scenario and telemetry generation |
| `src/data_quality.py` | Data-quality checks and validation rules |
| `src/preprocessing.py` | Cleaning and preprocessing |
| `src/feature_engineering.py` | Derived variables such as TTC |
| `src/event_detection.py` | Event identification |
| `src/metrics.py` | Metric calculations |
| `src/validation.py` | Validation classification and failure logic |

---

# 20. Testing Requirements

Pytest will eventually cover at least:

```text
TTC calculation
data-quality rules
metric calculations
TP/TN/FP/FN classification
validation logic
```

Example test concept:

```python
def test_ttc():
    assert calculate_ttc(20, 10) == 2
```

---

# 21. Dataset Design Principles

The dataset must follow these principles:

1. **Ground truth is independent from ADAS output.**
2. **Scenario behavior is generated from explicit rules rather than arbitrary random columns.**
3. **Derived variables are calculated consistently from underlying measurements.**
4. **Synthetic failures are intentional, controlled, and documented.**
5. **Data-quality failures are distinguishable from ADAS performance failures.**
6. **Project thresholds are clearly labeled as simulation assumptions.**
7. **The same data contract must support Python, SQL, and Power BI analysis.**
8. **The dataset must be reproducible through the generator.**

---

# 22. Complete Field Summary

| Field | Category | Type | Unit | Required | Derived |
|---|---|---|---|---|---|
| `event_id` | Identification | string | — | Yes | No |
| `timestamp` | Identification | datetime | time | Yes | No |
| `scenario_id` | Identification | categorical | — | Yes | No |
| `vehicle_id` | Identification | string | — | Yes | No |
| `pedestrian_id` | Identification | string | — | Conditional | No |
| `vehicle_speed_kmh` | Ego Vehicle | float | km/h | Yes | No |
| `vehicle_acceleration_ms2` | Ego Vehicle | float | m/s² | Yes | No |
| `vehicle_yaw_rate_dps` | Ego Vehicle | float | deg/s | Yes | No |
| `pedestrian_distance_m` | Pedestrian | float | m | Conditional | No |
| `pedestrian_relative_speed_ms` | Pedestrian | float | m/s | Conditional | No |
| `pedestrian_lateral_position_m` | Pedestrian | float | m | Conditional | No |
| `pedestrian_longitudinal_position_m` | Pedestrian | float | m | Conditional | No |
| `pedestrian_lane_relation` | Pedestrian | categorical | — | Conditional | No |
| `pedestrian_type` | Pedestrian | categorical | — | Conditional | No |
| `pedestrian_visibility` | Pedestrian | categorical | — | Conditional | No |
| `weather` | Environment | categorical | — | Yes | No |
| `lighting` | Environment | categorical | — | Yes | No |
| `road_condition` | Environment | categorical | — | Yes | No |
| `road_type` | Environment | categorical | — | Yes | No |
| `traffic_density` | Environment | categorical | — | Yes | No |
| `ground_truth_pedestrian` | Ground Truth | boolean | — | Yes | No |
| `ground_truth_collision_risk` | Ground Truth | boolean | — | Yes | No |
| `ground_truth_warning_required` | Ground Truth | boolean | — | Yes | No |
| `ground_truth_braking_required` | Ground Truth | boolean | — | Yes | No |
| `pedestrian_detected` | ADAS Output | boolean | — | Yes | No |
| `detection_confidence` | ADAS Output | float | 0–1 | Yes | No |
| `warning_triggered` | ADAS Output | boolean | — | Yes | No |
| `brake_triggered` | ADAS Output | boolean | — | Yes | No |
| `relative_closing_speed_ms` | Derived | float | m/s | Calculated | Yes |
| `ttc_seconds` | Derived | float | s | Calculated | Yes |
| `warning_lead_time_seconds` | Derived | float | s | Calculated | Yes |
| `detection_result` | Validation | categorical | — | Calculated | Yes |
| `warning_result` | Validation | categorical | — | Calculated | Yes |
| `braking_result` | Validation | categorical | — | Calculated | Yes |
| `validation_result` | Validation | categorical | — | Calculated | Yes |
| `failure_type` | Validation | categorical | — | Calculated | Yes |

---

# 23. Source of Truth and Scope

This document defines the current synthetic-data contract for the portfolio project.

It should be updated whenever the project intentionally changes:

- field names
- data types
- units
- valid ranges
- categorical values
- scenario definitions
- derived-feature formulas
- validation logic

Any such change should be reflected in the relevant implementation, tests, SQL schema, and documentation.
