from typing import Dict
import pulp


def optimize_shipments(
    warehouses: list[str],
    destinations: list[str],
    target_distribution: Dict[str, int],
    shipment_capacity: Dict[str, Dict[str, int]],
    warehouse_cost: Dict[str, float],
    shipment_cost: Dict[str, Dict[str, float]],
    target_delivery_days: int,
    delivery_tolerance: float,
    delivery_estimate: Dict[str, Dict[str, int]],
) -> pulp.LpProblem:
    problem = pulp.LpProblem("Shipment_Optimization", pulp.LpMinimize)

    # DECISION VARIABLES
    shipment_count = {
        (i, j): pulp.LpVariable(
            f"shipment_count_{i}_{j}",
            lowBound=0,
            upBound=shipment_capacity[i][j],
            cat="Integer",
        )
        for i in warehouses
        for j in destinations
    }

    # warehouse_usage[i] = binary variable indicating if warehouse i is used
    warehouse_usage = pulp.LpVariable.dicts("warehouse_usage", warehouses, cat="Binary")

    # CALCULATED PARAMETERS
    delivery_target_failure = {
        (i, j): 1 if delivery_estimate[i][j] > target_delivery_days else 0
        for i in warehouses
        for j in destinations
    }

    # OBJECTIVE FUNCTION
    total_cost = pulp.lpSum(
        [
            shipment_count[(i, j)] * shipment_cost[i][j]
            for i in warehouses
            for j in destinations
        ]
    ) + pulp.lpSum([warehouse_usage[i] * warehouse_cost[i] for i in warehouses])
    problem += total_cost, "Total_Cost"

    # CONSTRAINTS
    # Warehouse usage constraints
    for i in warehouses:
        for j in destinations:
            problem += (
                shipment_count[(i, j)] <= shipment_capacity[i][j] * warehouse_usage[i],
                f"Warehouse_Usage_{i}_{j}",
            )

    # Distribution constraints
    for j in destinations:
        problem += (
            pulp.lpSum([shipment_count[(i, j)] for i in warehouses])
            == target_distribution[j],
            f"Distribution_{j}",
        )

    # Delivery target constraints
    for j in destinations:
        failed_shipments = pulp.lpSum(
            [
                delivery_target_failure[(i, j)] * shipment_count[(i, j)]
                for i in warehouses
            ]
        )

        total_to_dest = pulp.lpSum([shipment_count[(i, j)] for i in warehouses])

        problem += (
            failed_shipments <= delivery_tolerance * total_to_dest,
            f"Delivery_Target_{j}",
        )

    return problem


def print_solution(
    problem: pulp.LpProblem,
    warehouses: list[str],
    destinations: list[str],
    target_distribution: Dict[str, int],
    warehouse_cost: Dict[str, float],
    shipment_cost: Dict[str, Dict[str, float]],
    target_delivery_days: int,
    delivery_estimate: Dict[str, Dict[str, int]],
) -> None:
    """
    Pretty print the solution of the shipment optimization problem.
    """
    if problem.status != pulp.LpStatusOptimal:
        print(f"Solution Status: {pulp.LpStatus[problem.status]}")
        print("No optimal solution found.")
        return

    print("=" * 80)
    print("SHIPMENT OPTIMIZATION SOLUTION")
    print("=" * 80)
    print(f"Status: {pulp.LpStatus[problem.status]}")
    print(f"Total Cost: ${problem.objective.value():,.2f}\n")

    # Extract solution values
    shipment_counts = {}
    warehouse_usage = {}

    for v in problem.variables():
        if v.name.startswith("shipment_count_"):
            # Parse warehouse and destination from variable name
            parts = v.name.replace("shipment_count_", "").split("_")
            i, j = parts[0], parts[1]
            shipment_counts[(i, j)] = int(v.varValue)
        elif v.name.startswith("warehouse_usage_"):
            i = v.name.replace("warehouse_usage_", "")
            warehouse_usage[i] = int(v.varValue)

    # Calculate total shipments across all destination targets
    total_shipments = sum(target_distribution.values())

    # Print warehouse usage and costs
    print("WAREHOUSE USAGE:")
    print("-" * 80)
    fixed_cost_total = 0
    for i in warehouses:
        status = "ACTIVE" if warehouse_usage.get(i, 0) == 1 else "INACTIVE"
        cost = warehouse_cost[i] * warehouse_usage.get(i, 0)
        fixed_cost_total += cost
        print(f"  Warehouse {i}: {status:8s}  Fixed Cost: ${cost:,.2f}")
    print(f"  Total Fixed Costs: ${fixed_cost_total:,.2f}\n")

    # Print shipment routing table
    print("SHIPMENT ROUTING:")
    print("-" * 80)

    # Header
    header = f"  {'From':8s} -> {'To':8s} | {'Shipments':>10s} | {'Unit Cost':>10s} | {'Total Cost':>12s}"
    print(header)
    print("  " + "-" * 76)

    variable_cost_total = 0
    for i in warehouses:
        for j in destinations:
            count = shipment_counts.get((i, j), 0)
            if count > 0:
                unit_cost = shipment_cost[i][j]
                total_cost = count * unit_cost
                variable_cost_total += total_cost
                print(
                    f"  {i:8s} -> {j:8s} | {count:10d} | ${unit_cost:9.2f} | ${total_cost:11.2f}"
                )

    print("  " + "-" * 76)
    print(f"  {'Total Variable Costs:':32s} ${variable_cost_total:11,.2f}\n")

    # Print destination distribution
    print("DESTINATION DISTRIBUTION:")
    print("-" * 80)
    print(
        f"  {'Destination':12s} | {'Actual':>10s} | {'Target':>10s} | {'% of Total':>11s}"
    )
    print("  " + "-" * 76)

    for j in destinations:
        dest_actual = sum(shipment_counts.get((i, j), 0) for i in warehouses)
        dest_target = target_distribution.get(j, 0)
        pct_of_total = (
            (dest_actual / total_shipments) * 100 if total_shipments > 0 else 0
        )
        print(
            f"  {j:12s} | {dest_actual:10d} | {dest_target:10d} | {pct_of_total:10.2f}%"
        )

    print("  " + "-" * 76)
    print(
        f"  {'TOTAL':12s} | {total_shipments:10d} | {total_shipments:10d} | {100.0:10.2f}%\n"
    )

    # Print warehouse distribution
    print("WAREHOUSE DISTRIBUTION:")
    print("-" * 80)
    print(f"  {'Warehouse':12s} | {'Shipments':>10s} | {'% of Total':>11s}")
    print("  " + "-" * 76)

    for i in warehouses:
        warehouse_total = sum(shipment_counts.get((i, j), 0) for j in destinations)
        pct_of_total = (
            (warehouse_total / total_shipments) * 100 if total_shipments > 0 else 0
        )
        print(f"  {i:12s} | {warehouse_total:10d} | {pct_of_total:10.2f}%")

    print("  " + "-" * 76)
    print(f"  {'TOTAL':12s} | {total_shipments:10d} | {100.0:10.2f}%\n")

    # Print delivery time statistics
    print("DELIVERY TIME STATISTICS:")
    print("-" * 80)
    print(f"  Target Delivery Days: {target_delivery_days}\n")

    # Overall statistics
    total_delivery_days = 0
    on_time_shipments = 0
    late_shipments = 0

    for i in warehouses:
        for j in destinations:
            count = shipment_counts.get((i, j), 0)
            if count > 0:
                days = delivery_estimate[i][j]
                total_delivery_days += days * count
                if days <= target_delivery_days:
                    on_time_shipments += count
                else:
                    late_shipments += count

    avg_delivery_days = (
        total_delivery_days / total_shipments if total_shipments > 0 else 0
    )
    on_time_pct = (
        (on_time_shipments / total_shipments * 100) if total_shipments > 0 else 0
    )
    late_pct = (late_shipments / total_shipments * 100) if total_shipments > 0 else 0

    print("  Overall:")
    print(f"    Average Delivery Time: {avg_delivery_days:.2f} days")
    print(f"    On-Time Shipments:     {on_time_shipments:,} ({on_time_pct:.2f}%)")
    print(f"    Late Shipments:        {late_shipments:,} ({late_pct:.2f}%)\n")

    # Per-destination statistics
    print(
        f"  {'Destination':12s} | {'Avg Days':>9s} | {'On-Time':>10s} | {'Late':>10s} | {'Late %':>9s}"
    )
    print("  " + "-" * 76)

    for j in destinations:
        dest_total = sum(shipment_counts.get((i, j), 0) for i in warehouses)
        if dest_total > 0:
            dest_delivery_days = sum(
                shipment_counts.get((i, j), 0) * delivery_estimate[i][j]
                for i in warehouses
            )
            dest_avg = dest_delivery_days / dest_total

            dest_on_time = sum(
                shipment_counts.get((i, j), 0)
                for i in warehouses
                if delivery_estimate[i][j] <= target_delivery_days
            )
            dest_late = dest_total - dest_on_time
            dest_late_pct = (dest_late / dest_total * 100) if dest_total > 0 else 0

            print(
                f"  {j:12s} | {dest_avg:9.2f} | {dest_on_time:10,} | {dest_late:10,} | {dest_late_pct:8.2f}%"
            )

    print("=" * 80)


def get_user_input() -> dict:
    """
    Prompt user via CLI to input all fixed parameters for the optimization problem.
    Returns a dictionary containing all the parameters.
    """
    print("=" * 80)
    print("SHIPMENT OPTIMIZATION - INPUT PARAMETERS")
    print("=" * 80)
    print()

    # Get warehouses
    print("WAREHOUSES:")
    warehouse_input = input(
        "Enter warehouse names (comma-separated, e.g., 'a,b,c'): "
    ).strip()
    warehouses = [w.strip() for w in warehouse_input.split(",")]
    print(f"  Warehouses: {warehouses}\n")

    # Get destinations
    print("DESTINATIONS:")
    destination_input = input(
        "Enter destination names (comma-separated, e.g., 'x,y,z'): "
    ).strip()
    destinations = [d.strip() for d in destination_input.split(",")]
    print(f"  Destinations: {destinations}\n")

    # Get target distribution
    print("TARGET DISTRIBUTION:")
    target_distribution = {}
    for j in destinations:
        while True:
            try:
                val = int(input(f"  Shipment count for destination '{j}': ").strip())
                if 0 <= val:
                    target_distribution[j] = val
                    break
                else:
                    print("    Error: Value must be non-negative")
            except ValueError:
                print("    Error: Please enter a valid number")

    # Get warehouse costs
    print("WAREHOUSE FIXED COSTS:")
    warehouse_cost = {}
    for i in warehouses:
        while True:
            try:
                val = float(input(f"  Fixed cost for warehouse '{i}': $").strip())
                if val >= 0:
                    warehouse_cost[i] = val
                    break
                else:
                    print("    Error: Cost must be non-negative")
            except ValueError:
                print("    Error: Please enter a valid number")
    print()

    # Get shipment capacity
    print("SHIPMENT CAPACITY:")
    print("  (Maximum shipments from each warehouse to each destination)")
    shipment_capacity = {}
    for i in warehouses:
        shipment_capacity[i] = {}
        for j in destinations:
            while True:
                try:
                    val = int(input(f"  Capacity from '{i}' to '{j}': ").strip())
                    if val >= 0:
                        shipment_capacity[i][j] = val
                        break
                    else:
                        print("    Error: Capacity must be non-negative")
                except ValueError:
                    print("    Error: Please enter a valid integer")
    print()

    # Get shipment costs
    print("SHIPMENT COSTS:")
    print("  (Cost per shipment from warehouse to destination)")
    shipment_cost = {}
    for i in warehouses:
        shipment_cost[i] = {}
        for j in destinations:
            while True:
                try:
                    val = float(
                        input(f"  Cost per shipment from '{i}' to '{j}': $").strip()
                    )
                    if val > 0:
                        shipment_cost[i][j] = val
                        break
                    else:
                        print("    Error: Cost must be positive")
                except ValueError:
                    print("    Error: Please enter a valid number")
    print()

    # Get target delivery days
    print("DELIVERY TARGETS:")
    while True:
        try:
            target_delivery_days = int(
                input("Enter target maximum delivery days: ").strip()
            )
            if target_delivery_days > 0:
                break
            else:
                print("  Error: Must be a positive integer")
        except ValueError:
            print("  Error: Please enter a valid integer")
    print(f"  Target delivery days: {target_delivery_days}\n")

    # Get delivery tolerance
    print("DELIVERY TOLERANCE:")
    while True:
        try:
            delivery_tolerance = float(
                input(
                    "Enter delivery tolerance (0.0-1.0, fraction that may miss target): "
                ).strip()
            )
            if 0 <= delivery_tolerance <= 1:
                break
            else:
                print("  Error: Value must be between 0 and 1")
        except ValueError:
            print("  Error: Please enter a valid number")
    print(f"  Delivery tolerance: {delivery_tolerance}\n")

    # Get delivery estimates
    print("DELIVERY ESTIMATES:")
    print("  (Estimated delivery days from each warehouse to each destination)")
    delivery_estimate = {}
    for i in warehouses:
        delivery_estimate[i] = {}
        for j in destinations:
            while True:
                try:
                    val = int(
                        input(
                            f"  Estimated delivery days from '{i}' to '{j}': "
                        ).strip()
                    )
                    if val >= 1:
                        delivery_estimate[i][j] = val
                        break
                    else:
                        print("    Error: Must be at least 1 day")
                except ValueError:
                    print("    Error: Please enter a valid integer")
    print()

    print("=" * 80)
    print("INPUT COMPLETE")
    print("=" * 80)
    print()

    return {
        "warehouses": warehouses,
        "destinations": destinations,
        "target_distribution": target_distribution,
        "shipment_capacity": shipment_capacity,
        "warehouse_cost": warehouse_cost,
        "shipment_cost": shipment_cost,
        "target_delivery_days": target_delivery_days,
        "delivery_tolerance": delivery_tolerance,
        "delivery_estimate": delivery_estimate,
    }


def main():
    params = get_user_input()

    problem = optimize_shipments(**params)
    problem.solve()

    print_solution(
        problem,
        params["warehouses"],
        params["destinations"],
        params["target_distribution"],
        params["warehouse_cost"],
        params["shipment_cost"],
        params["target_delivery_days"],
        params["delivery_estimate"],
    )


if __name__ == "__main__":
    main()
