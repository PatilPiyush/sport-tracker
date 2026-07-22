import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Half Marathon Tracker", layout="wide")

PLAN = [
    {"week": 1, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Easy strides", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 9 km", "sunday": "Recovery walk / rest", "target_weekly_km": 22},
    {"week": 2, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Tempo 3 km", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 10 km", "sunday": "Recovery walk / rest", "target_weekly_km": 24},
    {"week": 3, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Intervals 4x800 m", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 11 km", "sunday": "Recovery walk / rest", "target_weekly_km": 26},
    {"week": 4, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Tempo 4 km", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 12 km", "sunday": "Recovery walk / rest", "target_weekly_km": 28},
    {"week": 5, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Progression run", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 13 km", "sunday": "Recovery walk / rest", "target_weekly_km": 30},
    {"week": 6, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Intervals 5x800 m", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 14 km", "sunday": "Recovery walk / rest", "target_weekly_km": 32},
    {"week": 7, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Tempo 5 km", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 15 km", "sunday": "Recovery walk / rest", "target_weekly_km": 34},
    {"week": 8, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Intervals 6x800 m", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 16 km", "sunday": "Recovery walk / rest", "target_weekly_km": 36},
    {"week": 9, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Tempo 6 km", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 17 km", "sunday": "Recovery walk / rest", "target_weekly_km": 38},
    {"week": 10, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Race pace 8 km", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 18 km", "sunday": "Recovery walk / rest", "target_weekly_km": 40},
    {"week": 11, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Dress rehearsal 10 km", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 19 km", "sunday": "Recovery walk / rest", "target_weekly_km": 42},
    {"week": 12, "monday": "Rest / mobility", "tuesday": "Easy run 5-7 km", "wednesday": "Taper", "thursday": "Rest or cross-training", "friday": "Easy run 5-8 km", "saturday": "Long run 12 km", "sunday": "Recovery walk / rest", "target_weekly_km": 22},
]

PACES = {
    "Easy": ("7:00-7:30", "< 150"),
    "Long run": ("6:55-7:25", "< 155"),
    "Tempo": ("6:20-6:40", "155-170"),
    "Intervals": ("5:50-6:15", "165-180"),
    "Recovery": ("7:20-8:00", "< 145"),
}

LOG_COLUMNS = [
    "week", "date", "run_type", "distance_km", "avg_pace_min_per_km",
    "avg_hr_bpm", "cadence_spm", "rpe", "notes"
]

st.title("Half Marathon Trainer")
st.caption("12-week plan, run log, pace zones, dashboard, and HTML export")

plan_df = pd.DataFrame(PLAN)
log_path = Path("run_log.csv")

if not log_path.exists() or log_path.stat().st_size == 0:
    pd.DataFrame(columns=LOG_COLUMNS).to_csv(log_path, index=False)

st.sidebar.header("Quick Pace Zones")
zone_df = pd.DataFrame(
    [{"Run type": k, "Target pace": v[0], "Target HR": v[1]} for k, v in PACES.items()]
)
st.sidebar.dataframe(zone_df, hide_index=True, use_container_width=True)

page = st.sidebar.radio("Navigate", ["Dashboard", "Plan", "Log Session"])

def load_logs():
    try:
        if log_path.exists() and log_path.stat().st_size > 0:
            df = pd.read_csv(log_path)
            if df.empty:
                return pd.DataFrame(columns=LOG_COLUMNS)
            return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=LOG_COLUMNS)
    return pd.DataFrame(columns=LOG_COLUMNS)

def generate_html_report(logs: pd.DataFrame, plan_df: pd.DataFrame) -> str:
    if logs.empty:
        weekly_html = "<p>No sessions logged yet.</p>"
        raw_html = "<p>No sessions logged yet.</p>"
    else:
        disp = logs.copy()
        for c in ["distance_km", "avg_hr_bpm", "cadence_spm", "rpe"]:
            if c in disp.columns:
                disp[c] = pd.to_numeric(disp[c], errors="coerce")
        weekly = disp.groupby("week", as_index=False).agg(
            total_km=("distance_km", "sum"),
            avg_hr=("avg_hr_bpm", "mean"),
            avg_cadence=("cadence_spm", "mean"),
            avg_rpe=("rpe", "mean")
        )
        weekly_html = weekly.to_html(index=False, classes="table")
        raw_html = disp.to_html(index=False, classes="table")

    return f"""
<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Half Marathon Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
h1, h2 {{ color: #111827; }}
.card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; margin-bottom: 18px; }}
.table {{ border-collapse: collapse; width: 100%; }}
.table th, .table td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; }}
.table th {{ background: #f9fafb; }}
.small {{ color: #6b7280; }}
</style>
</head>
<body>
<h1>Half Marathon Training Report</h1>
<p class='small'>Generated from your Streamlit training tracker.</p>
<div class='card'>
<h2>Plan Summary</h2>
{plan_df.to_html(index=False, classes='table')}
</div>
<div class='card'>
<h2>Weekly Log Summary</h2>
{weekly_html}
</div>
<div class='card'>
<h2>Raw Sessions</h2>
{raw_html}
</div>
</body>
</html>
"""

if page == "Dashboard":
    st.subheader("Training Dashboard")
    logs = load_logs()

    if not logs.empty:
        for c in ["distance_km", "avg_hr_bpm", "cadence_spm", "rpe"]:
            if c in logs.columns:
                logs[c] = pd.to_numeric(logs[c], errors="coerce")

        weekly = logs.groupby("week", as_index=False).agg(
            total_km=("distance_km", "sum"),
            avg_hr=("avg_hr_bpm", "mean"),
            avg_cadence=("cadence_spm", "mean"),
            avg_rpe=("rpe", "mean")
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Logged sessions", len(logs))
        c2.metric("Total distance (km)", round(logs["distance_km"].sum(), 1))
        c3.metric(
            "Avg HR",
            round(logs["avg_hr_bpm"].mean(), 0) if logs["avg_hr_bpm"].notna().any() else "-"
        )

        st.dataframe(weekly, use_container_width=True, hide_index=True)

        fig = px.line(weekly, x="week", y="total_km", markers=True, title="Weekly Distance")
        st.plotly_chart(fig, use_container_width=True)

        html_report = generate_html_report(logs, plan_df)
        st.download_button(
            "Download HTML report",
            data=html_report,
            file_name="half_marathon_report.html",
            mime="text/html",
        )
    else:
        st.info("No run log found yet. Add sessions in Log Session.")

elif page == "Plan":
    st.subheader("12-Week Plan")
    st.dataframe(plan_df, use_container_width=True, hide_index=True)
    fig = px.bar(plan_df, x="week", y="target_weekly_km", title="Target Weekly Mileage")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.subheader("Log a Session")
    with st.form("run_form"):
        week = st.number_input("Week", 1, 12, 1)
        date = st.date_input("Date")
        run_type = st.selectbox("Run Type", ["Easy", "Long run", "Tempo", "Intervals", "Recovery"])
        distance_km = st.number_input("Distance (km)", min_value=0.0, step=0.1, value=5.0)
        avg_pace = st.text_input("Average pace (min/km)", value="6:54")
        avg_hr = st.number_input("Average heart rate (bpm)", min_value=0, step=1, value=0)
        cadence = st.number_input("Cadence (spm)", min_value=0, step=1, value=0)
        rpe = st.slider("RPE", 1, 10, 5)
        notes = st.text_area("Notes")
        save = st.form_submit_button("Save")

    if save:
        row = pd.DataFrame([{
            "week": week,
            "date": str(date),
            "run_type": run_type,
            "distance_km": distance_km,
            "avg_pace_min_per_km": avg_pace,
            "avg_hr_bpm": avg_hr,
            "cadence_spm": cadence,
            "rpe": rpe,
            "notes": notes,
        }])

        old = load_logs()
        out = pd.concat([old, row], ignore_index=True)
        out.to_csv(log_path, index=False)
        st.success("Session saved")

    current = load_logs()
    if not current.empty:
        st.dataframe(current, use_container_width=True, hide_index=True)
    else:
        st.info("No sessions logged yet.")
