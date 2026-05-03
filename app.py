import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Team Capacity Analytics Simulator",
    page_icon="T",
    layout="wide",
)


@st.cache_data
def generate_workflow_data(days: int = 90, seed: int = 13) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    analysts = [
        {"analyst": "Avery", "team": "Risk Analytics", "capacity_hours": 34},
        {"analyst": "Blake", "team": "Risk Analytics", "capacity_hours": 32},
        {"analyst": "Casey", "team": "Controls", "capacity_hours": 30},
        {"analyst": "Devon", "team": "Controls", "capacity_hours": 28},
        {"analyst": "Emerson", "team": "Operations", "capacity_hours": 35},
        {"analyst": "Finley", "team": "Operations", "capacity_hours": 30},
    ]
    priority_hours = {"P1": 10, "P2": 6, "P3": 3, "P4": 1.5}
    sla_days = {"P1": 1, "P2": 3, "P3": 5, "P4": 10}
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days)

    records = []
    task_id = 1000
    for date in dates:
        volume = int(rng.poisson(18))
        if date >= dates.max() - pd.Timedelta(days=21):
            volume += int(rng.poisson(5))
        for _ in range(volume):
            analyst = rng.choice(analysts)
            priority = rng.choice(["P1", "P2", "P3", "P4"], p=[0.12, 0.28, 0.42, 0.18])
            estimated_hours = max(0.5, rng.normal(priority_hours[priority], priority_hours[priority] * 0.25))
            cycle_days = max(0.25, rng.normal(sla_days[priority] * 0.75, 1.1))
            completed = rng.random() > 0.14
            completed_date = date + pd.Timedelta(days=float(cycle_days)) if completed else pd.NaT
            sla_due = date + pd.Timedelta(days=sla_days[priority])
            sla_breached = bool(completed_date > sla_due) if completed else bool(pd.Timestamp.today().normalize() > sla_due)

            records.append(
                {
                    "task_id": task_id,
                    "created_date": date,
                    "completed_date": completed_date,
                    "analyst": analyst["analyst"],
                    "team": analyst["team"],
                    "priority": priority,
                    "estimated_hours": round(float(estimated_hours), 2),
                    "cycle_days": round(float(cycle_days), 2),
                    "sla_due": sla_due,
                    "sla_breached": sla_breached,
                    "status": "Completed" if completed else "Open",
                    "capacity_hours": analyst["capacity_hours"],
                }
            )
            task_id += 1

    return pd.DataFrame(records)


def apply_scenario(df: pd.DataFrame, volume_change: int, staffing_delta: int, p1_shift: int) -> dict:
    baseline_volume = len(df)
    adjusted_volume = baseline_volume * (1 + volume_change / 100)
    baseline_capacity = df[["analyst", "capacity_hours"]].drop_duplicates()["capacity_hours"].sum()
    adjusted_capacity = baseline_capacity + staffing_delta * 30
    priority_multiplier = 1 + (p1_shift / 100) * 0.45
    demand_hours = df["estimated_hours"].sum() * (1 + volume_change / 100) * priority_multiplier
    utilization = demand_hours / max(adjusted_capacity * (df["created_date"].nunique() / 7), 1)
    breach_risk = min(0.95, max(0.02, df["sla_breached"].mean() * (1 + volume_change / 120) * priority_multiplier * (1 - staffing_delta * 0.08)))
    return {
        "adjusted_volume": adjusted_volume,
        "adjusted_capacity": adjusted_capacity,
        "demand_hours": demand_hours,
        "utilization": utilization,
        "breach_risk": breach_risk,
    }


st.title("Team Capacity Analytics Simulator")
st.caption("Synthetic workflow analytics for manager-level capacity planning and delivery-risk decisions.")

with st.sidebar:
    st.header("Scenario")
    days = st.slider("History window", 45, 180, 90, step=15)
    seed = st.number_input("Synthetic data seed", min_value=1, max_value=999, value=13)
    volume_change = st.slider("Volume change", -20, 60, 20, step=5)
    staffing_delta = st.slider("Staffing change", -2, 3, 0, step=1)
    p1_shift = st.slider("P1 priority mix shift", -20, 50, 10, step=5)

tasks = generate_workflow_data(days=days, seed=seed)
scenario = apply_scenario(tasks, volume_change, staffing_delta, p1_shift)

completed = tasks[tasks["status"] == "Completed"]
open_tasks = tasks[tasks["status"] == "Open"]
throughput = len(completed) / max(tasks["created_date"].nunique(), 1)
breach_rate = tasks["sla_breached"].mean()
avg_cycle = completed["cycle_days"].mean()
backlog = len(open_tasks)

metric_cols = st.columns(5)
metric_cols[0].metric("Daily Throughput", f"{throughput:.1f}")
metric_cols[1].metric("Open Backlog", f"{backlog:,}")
metric_cols[2].metric("SLA Breach Rate", f"{breach_rate:.1%}")
metric_cols[3].metric("Avg Cycle Days", f"{avg_cycle:.1f}")
metric_cols[4].metric("Scenario Utilization", f"{scenario['utilization']:.0%}")

st.subheader("Manager Summary")
if scenario["utilization"] > 1:
    st.warning(
        "Recommended action: current scenario exceeds estimated capacity. Rebalance priority work, add temporary capacity, or reduce lower-priority intake."
    )
elif scenario["breach_risk"] > 0.25:
    st.info(
        "Recommended action: monitor SLA-sensitive work and review whether P1/P2 demand is crowding out routine backlog closure."
    )
else:
    st.success("Recommended action: staffing and priority mix appear manageable under this scenario.")

st.write(
    f"Scenario estimate: {scenario['adjusted_volume']:.0f} tasks, "
    f"{scenario['demand_hours']:.0f} demand hours, and {scenario['breach_risk']:.1%} projected SLA breach risk."
)

left, right = st.columns(2)
with left:
    weekly = (
        tasks.assign(week=tasks["created_date"].dt.to_period("W").dt.start_time)
        .groupby(["week", "status"])
        .size()
        .reset_index(name="tasks")
    )
    fig = px.bar(weekly, x="week", y="tasks", color="status", title="Weekly Intake and Completion Status")
    st.plotly_chart(fig, use_container_width=True)

with right:
    workload = (
        tasks.groupby(["analyst", "priority"])
        .agg(hours=("estimated_hours", "sum"), tasks=("task_id", "count"))
        .reset_index()
    )
    fig = px.bar(workload, x="analyst", y="hours", color="priority", title="Estimated Workload by Analyst")
    st.plotly_chart(fig, use_container_width=True)

capacity = (
    tasks.groupby(["analyst", "team"])
    .agg(
        assigned_hours=("estimated_hours", "sum"),
        assigned_tasks=("task_id", "count"),
        open_tasks=("status", lambda values: (values == "Open").sum()),
        breach_rate=("sla_breached", "mean"),
        weekly_capacity=("capacity_hours", "max"),
    )
    .reset_index()
)
weeks = max(tasks["created_date"].nunique() / 7, 1)
capacity["utilization"] = capacity["assigned_hours"] / (capacity["weekly_capacity"] * weeks)
capacity["breach_rate"] = capacity["breach_rate"].map(lambda value: f"{value:.1%}")
capacity["utilization"] = capacity["utilization"].map(lambda value: f"{value:.0%}")
capacity["assigned_hours"] = capacity["assigned_hours"].round(1)

st.subheader("Capacity and SLA Risk by Analyst")
st.dataframe(capacity.sort_values("assigned_hours", ascending=False), use_container_width=True, hide_index=True)

priority_summary = (
    tasks.groupby("priority")
    .agg(tasks=("task_id", "count"), open_tasks=("status", lambda values: (values == "Open").sum()), breach_rate=("sla_breached", "mean"))
    .reset_index()
)
priority_summary["breach_rate"] = priority_summary["breach_rate"].map(lambda value: f"{value:.1%}")
st.subheader("Priority Mix and Delivery Risk")
st.dataframe(priority_summary, use_container_width=True, hide_index=True)
