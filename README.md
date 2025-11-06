# Warehouse & Carrier Optimization Toolkit

A Python-based linear programming toolkit for optimizing warehouse shipment routing and multi-year carrier earned discount strategies.

This project now includes **two complementary optimization modules**:

- **`warehouse_shipments.py`** – Optimizes warehouse-to-destination shipment routing to minimize total shipping costs while meeting delivery constraints.
- **`carrier_earned_discount.py`** – Optimizes multi-year carrier shipment allocations to achieve earned discount tiers while satisfying shipment targets.

Both scripts use the [PuLP](https://coin-or.github.io/pulp/) linear programming library and feature interactive CLI input, detailed solution reports, and robust feasibility diagnostics.

---

## Features

### Warehouse Shipment Optimization (`warehouse_shipments.py`)
- **Cost Minimization**: Reduces total shipping cost, including fixed warehouse overhead and per-shipment costs.
- **Target Fulfillment**: Guarantees exact shipment quantities to each destination.
- **Delivery Constraints**: Enforces maximum delivery days with configurable tolerance for late deliveries.
- **Capacity Handling**: Respects per-route shipment capacity limits.
- **Interactive CLI Input**: Collects all parameters directly from the user — no code editing required.
- **Feasibility Diagnostics**: Identifies and explains infeasible, unbounded, or unsolved optimization scenarios.
- **Detailed Report**: Provides breakdowns by warehouse, destination, and delivery statistics.

---

### Carrier Earned Discount Optimization (`carrier_earned_discount.py`)
- **Multi-Year Planning**: Optimizes shipment allocation across multiple years.
- **Tiered Discounts**: Models carrier-specific earned discount tiers based on shipment volume.
- **Automatic Tier 0 Handling**: Tier 0 (minimum = 0, discount = 1.0) is automatically included for all carriers.
- **Comprehensive Diagnostics**: Detects infeasibility, unbounded objectives, and solver issues with explanatory feedback.
- **Interactive CLI Input**: Users specify carriers, destinations, targets, costs, tiers, and discounts through prompts.
- **Detailed Report**: Displays active tiers, shipment allocation per carrier, destination summaries, and total cost analysis.

---

## Requirements

- **Python 3.12 or higher**
- [**PuLP**](https://coin-or.github.io/pulp/)
- [**uv**](https://docs.astral.sh/uv/) package manager (recommended) or pip

---

## Installation

### Using uv (Recommended)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
````

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install pulp
```

---

## Usage

### 1. Warehouse Shipment Optimization

Run interactively:

```bash
uv run warehouse_shipments.py
# or
python warehouse_shipments.py
```

You will be prompted for:

1. Warehouse names
2. Destination names
3. Shipment targets per destination
4. Fixed warehouse costs
5. Capacity per warehouse-destination pair
6. Shipment cost per route
7. Delivery day targets and tolerance
8. Estimated delivery days per route

If the solver detects infeasibility or unboundedness, detailed diagnostics and suggestions are displayed.

---

### 2. Carrier Earned Discount Optimization

Run interactively:

```bash
uv run carrier_earned_discount.py
# or
python carrier_earned_discount.py
```

You will be prompted for:

1. Number of years to optimize
2. Carrier names
3. Destination names
4. Annual shipment targets per destination
5. Shipment cost per carrier-destination pair
6. Minimum shipment quantities per discount tier *(Tier 0 = 0 is always included)*
7. Discount multipliers for each carrier *(Tier 0 multiplier = 1.0 added automatically)*

---

## Output

Both optimization models generate detailed terminal reports including:

* **Solver Status** (Optimal, Infeasible, Unbounded, etc.)
* **Feasibility Diagnostics** with probable causes and suggestions
* **Total Cost Breakdown**
* **Shipment Routing and Allocation Tables**
* **Destination and Warehouse Summaries**
* **Performance Metrics** (delivery days, on-time %)
* **Discount Tier Summaries** (for carrier optimization)

---

## Problem Formulation

Each model solves a **mixed-integer linear programming (MILP)** problem using PuLP’s CBC solver:

* **Objective**: Minimize total cost
* **Subject to**:

  * Capacity constraints
  * Delivery or tier requirements
  * Exact shipment target fulfillment
  * Binary warehouse/carrier activation constraints

See `equations.txt` for the complete mathematical formulation.

---

## License

This project uses the [PuLP](https://coin-or.github.io/pulp/) library for linear programming optimization.
