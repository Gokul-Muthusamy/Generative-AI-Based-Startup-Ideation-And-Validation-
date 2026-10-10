import json
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

matplotlib.use("Agg")


def build_market_projection(
    base_value=1200.0, annual_growth=0.224, years=None
):
    """
    Builds a series of market projection data dictionary records.
    Safely coerces base_value and annual_growth inputs to float.
    """
    try:
        base_val = float(base_value)
    except (TypeError, ValueError):
        base_val = 1200.0

    try:
        growth = float(annual_growth)
    except (TypeError, ValueError):
        growth = 0.224

    if not years or not isinstance(years, (list, tuple)):
        years = list(range(2023, 2029))

    values = np.array([
        round(base_val * ((1 + growth) ** index), 2)
        for index, _ in enumerate(years)
    ])
    frame = pd.DataFrame({"year": years, "market_value_billion": values})
    return frame.to_dict(orient="records")


def build_plotly_market_projection(projection):
    """
    Generates a Plotly market projection chart dict structure.
    Validates input projection data format.
    """
    if not projection or not isinstance(projection, list):
        projection = build_market_projection()

    frame = pd.DataFrame(projection)
    has_yr = "year" in frame.columns
    has_val = "market_value_billion" in frame.columns
    if not has_yr or not has_val:
        frame = pd.DataFrame(build_market_projection())

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=frame["year"],
        y=frame["market_value_billion"],
        mode="lines+markers",
        name="Market Value (₹ Cr)",
        line={"color": "#2563EB", "width": 3},
    ))
    fig.update_layout(
        template="plotly_white",
        margin={"l": 32, "r": 16, "t": 24, "b": 32},
        xaxis_title="Year",
        yaxis_title="Market Value (₹ Crores)",
        height=320,
    )
    return json.loads(fig.to_json())


def generate_matplotlib_projection_chart(projection, output_filepath):
    """
    Generates and saves a Matplotlib market projection PNG file.
    Ensures plt figure is closed safely in a try-finally block.
    """
    if not projection or not isinstance(projection, list):
        projection = build_market_projection()

    frame = pd.DataFrame(projection)
    has_yr = "year" in frame.columns
    has_val = "market_value_billion" in frame.columns
    if not has_yr or not has_val:
        frame = pd.DataFrame(build_market_projection())

    path = Path(output_filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(7, 3.4))
    try:
        plt.plot(
            frame["year"],
            frame["market_value_billion"],
            marker="o",
            color="#2563EB"
        )
        plt.fill_between(
            frame["year"],
            frame["market_value_billion"],
            alpha=0.15,
            color="#2563EB"
        )
        plt.title("Market Growth Projection (India/TN)")
        plt.xlabel("Year")
        plt.ylabel("Market Value (₹ Crores)")
        plt.tight_layout()
        plt.savefig(path, dpi=140)
    finally:
        plt.close(fig)

    return str(path)
