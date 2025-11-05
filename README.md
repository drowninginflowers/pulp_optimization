# Warehouse Shipment Optimization

A Python-based linear programming tool that optimizes warehouse shipment routing to minimize costs while meeting distribution targets and delivery time constraints.

## Features

- **Cost Optimization**: Minimizes total shipping costs including fixed warehouse costs and per-shipment costs
- **Distribution Targets**: Ensures shipments meet exact target quantities for each destination
- **Delivery Constraints**: Respects delivery time targets with configurable tolerance for late shipments
- **Capacity Management**: Handles warehouse-to-destination capacity limits
- **Interactive CLI**: User-friendly command-line interface for inputting parameters
- **Detailed Output**: Comprehensive solution summary with cost breakdowns, routing tables, distribution statistics, and delivery analytics

## Requirements

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

## Installation

### Using uv (Recommended)

1. Install uv if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone or download this repository

3. Install dependencies:
   ```bash
   uv sync
   ```

### Using pip

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install pulp
   ```

## Usage

Run the program with:

```bash
uv run main.py
```

Or if using pip:

```bash
python main.py
```

The program will prompt you to enter:

1. **Warehouses**: Comma-separated list of warehouse names
2. **Destinations**: Comma-separated list of destination names
3. **Target Distribution**: Exact number of shipments required for each destination
4. **Warehouse Fixed Costs**: Fixed cost for using each warehouse
5. **Shipment Capacity**: Maximum shipments from each warehouse to each destination
6. **Shipment Costs**: Cost per shipment for each warehouse-destination pair
7. **Target Delivery Days**: Maximum acceptable delivery time
8. **Delivery Tolerance**: Fraction of shipments allowed to miss delivery target (0.0-1.0)
9. **Delivery Estimates**: Expected delivery days for each warehouse-destination pair

### Example Input

```
Warehouses: a,b
Destinations: x,y,z
Shipment count for destination 'x': 400
Shipment count for destination 'y': 300
Shipment count for destination 'z': 300
Fixed cost for warehouse 'a': $500
Fixed cost for warehouse 'b': $300
...
```

## Output

The program provides a detailed optimization report including:

- **Warehouse Usage**: Which warehouses are active and their fixed costs
- **Shipment Routing**: Complete routing table with shipment counts and costs
- **Destination Distribution**: Actual vs. target shipment counts with percentage breakdowns
- **Warehouse Distribution**: Total shipments from each warehouse with percentage breakdowns
- **Delivery Statistics**: Average delivery times, on-time rates, and late shipment statistics by destination and overall

## Problem Formulation

The optimizer solves a mixed-integer linear programming problem that:

- **Minimizes**: Total cost (fixed warehouse costs + variable shipment costs)
- **Subject to**: 
  - Exact shipment count requirements for each destination
  - Capacity constraints for each warehouse-destination pair
  - Warehouse usage binary constraints
  - Delivery time constraints (with tolerance for late shipments)

See `equations.txt` for the complete mathematical formulation.

## License

This project uses the PuLP library for linear programming optimization.
