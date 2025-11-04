# Warehouse Shipment Optimization

A Python-based linear programming tool that optimizes warehouse shipment routing to minimize costs while meeting distribution targets and delivery time constraints.

## Features

- **Cost Optimization**: Minimizes total shipping costs including fixed warehouse costs and per-shipment costs
- **Distribution Targets**: Ensures shipments meet target distribution percentages across destinations (with configurable tolerance)
- **Delivery Constraints**: Respects delivery time targets with configurable tolerance for late shipments
- **Capacity Management**: Handles warehouse-to-destination capacity limits
- **Interactive CLI**: User-friendly command-line interface for inputting parameters
- **Detailed Output**: Comprehensive solution summary with cost breakdowns, routing tables, and delivery statistics

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
3. **Total Shipments**: Total number of shipments to distribute
4. **Target Distribution**: Desired percentage of shipments to each destination (must sum to 1.0)
5. **Distribution Tolerance**: Allowable deviation from target distribution (0.0-1.0)
6. **Warehouse Fixed Costs**: Fixed cost for using each warehouse
7. **Shipment Capacity**: Maximum shipments from each warehouse to each destination
8. **Shipment Costs**: Cost per shipment for each warehouse-destination pair
9. **Target Delivery Days**: Maximum acceptable delivery time
10. **Delivery Tolerance**: Fraction of shipments allowed to miss delivery target (0.0-1.0)
11. **Delivery Estimates**: Expected delivery days for each warehouse-destination pair

### Example Input

```
Warehouses: a,b
Destinations: x,y,z
Total shipments: 1000
Target distribution for 'x': 0.4
Target distribution for 'y': 0.3
Target distribution for 'z': 0.3
Distribution tolerance: 0.05
Fixed cost for warehouse 'a': $500
Fixed cost for warehouse 'b': $300
...
```

## Output

The program provides a detailed optimization report including:

- **Warehouse Usage**: Which warehouses are active and their fixed costs
- **Shipment Routing**: Complete routing table with shipment counts and costs
- **Destination Distribution**: Actual vs. target distribution percentages
- **Delivery Statistics**: Average delivery times, on-time rates, and late shipment statistics

## Problem Formulation

The optimizer solves a mixed-integer linear programming problem that:

- **Minimizes**: Total cost (fixed warehouse costs + variable shipment costs)
- **Subject to**: 
  - Total shipment constraint
  - Capacity constraints
  - Distribution target constraints (with tolerance)
  - Delivery time constraints (with tolerance)

See `equations.txt` for the complete mathematical formulation.

## License

This project uses the PuLP library for linear programming optimization.
