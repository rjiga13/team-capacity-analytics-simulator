# Team Capacity Analytics Simulator

A manager-facing analytics simulator for understanding team capacity, delivery risk, workload imbalance, SLA exposure, and operational bottlenecks using synthetic workflow data.

## Problem

Managers often need to make staffing and prioritization decisions before they have perfect data. Backlog, volume shifts, priority mix, and individual capacity can create delivery risk that is hard to see from raw task lists.

## Solution

This Streamlit app generates a synthetic task workflow across analysts, priorities, SLAs, and completion times. It provides KPI views and scenario controls so leaders can test how volume growth, staffing changes, and priority mix shifts affect throughput and SLA breach risk.

## Core Features

- Synthetic dataset for tasks, analysts, priorities, completion times, backlog, and SLA status
- Throughput, utilization, workload balance, bottleneck, and SLA risk views
- Scenario simulator for volume growth, staffing changes, and priority mix shifts
- Manager-facing recommendations tied to staffing and prioritization decisions
- Clean business documentation for hiring managers and portfolio reviewers

## Business Value

- Helps leaders spot delivery risk before missed SLAs accumulate
- Makes workload imbalance visible across analysts and priority levels
- Supports staffing and prioritization conversations with data-backed scenarios
- Demonstrates analytics leadership, product thinking, and practical dashboard delivery

## Tech Stack

Python, Streamlit, pandas, NumPy, Plotly

## How To Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- data/
|   `-- README.md
`-- screenshots/
    `-- README.md
```

## Notes

All data is synthetic and fictional. The simulator is intended for portfolio demonstration and management decision-support design.
