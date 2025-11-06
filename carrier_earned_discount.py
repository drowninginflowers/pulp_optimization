from pulp import (
    LpProblem,
    LpMinimize,
    LpVariable,
    lpSum,
    value,
    LpStatus,
    LpStatusOptimal,
    LpStatusInfeasible,
    LpStatusUnbounded,
    LpStatusNotSolved,
)


def optimize_shipments(
    num_years: int,
    carriers: list[str],
    destinations: list[str],
    # shipment_target[year][dest] == target shipments to dest in year
    shipment_target: list[dict[str, float]],
    # shipment_cost[carrier][dest] == cost per shipment to dest via carrier
    shipment_cost: dict[str, dict[str, float]],
    tier_min_quantity: list[int],
    # discount_rate[carrier][tier] == discount multiplier for carrier at tier
    discount_rate: dict[str, list[float]],
) -> LpProblem:
    problem = LpProblem("Carrier_Optimization", LpMinimize)

    # DECISION VARIABLES: shipments in year at tier from carrier to destination
    # Ordered as: year -> carrier -> tier -> destination
    shipment_at_tier = {}
    for year in range(num_years):
        shipment_at_tier[year] = {}
        for carrier in carriers:
            shipment_at_tier[year][carrier] = {}
            for tier in range(len(tier_min_quantity)):
                shipment_at_tier[year][carrier][tier] = {}
                for dest in destinations:
                    shipment_at_tier[year][carrier][tier][dest] = LpVariable(
                        f"ship_y{year}_{carrier}_t{tier}_{dest}",
                        lowBound=0,
                        upBound=shipment_target[year][dest],
                        cat="Integer",
                    )

    # Binary variables for tier selection
    # Ordered as: year -> carrier -> tier
    tier_flag = []
    for year in range(num_years):
        tier_flag.append({})
        for carrier in carriers:
            tier_flag[year][carrier] = [
                LpVariable(f"tier_y{year}_{carrier}_t{tier}", cat="Binary")
                for tier in range(len(tier_min_quantity))
            ]

    # OBJECTIVE FUNCTION
    total_cost = lpSum(
        [
            shipment_at_tier[year][carrier][tier][dest]
            * shipment_cost[carrier][dest]
            * discount_rate[carrier][tier]
            for year in range(num_years)
            for carrier in carriers
            for tier in range(len(tier_min_quantity))
            for dest in destinations
        ]
    )

    problem += total_cost, "Total_Cost"

    # CONSTRAINTS
    for year in range(num_years):
        for carrier in carriers:
            # only 1 earned discount tier may be active per year
            problem += lpSum(tier_flag[year][carrier]) == 1

            for tier in range(len(tier_min_quantity)):
                for dest in destinations:
                    # shipments can only occur when tier is active
                    problem += (
                        shipment_at_tier[year][carrier][tier][dest]
                        <= shipment_target[year][dest] * tier_flag[year][carrier][tier]
                    )

                # total shipments at a discount tier across all destinations
                tier_total = lpSum(
                    [
                        shipment_at_tier[year][carrier][tier][dest]
                        for dest in destinations
                    ]
                )

                # must meet minimum shipments for an active discount tier
                problem += (
                    tier_total
                    >= tier_min_quantity[tier] * tier_flag[year][carrier][tier]
                )

    # must hit shipment targets each year
    for year in range(num_years):
        for dest in destinations:
            destination_total = lpSum(
                [
                    shipment_at_tier[year][carrier][tier][dest]
                    for carrier in carriers
                    for tier in range(len(tier_min_quantity))
                ]
            )
            problem += destination_total == shipment_target[year][dest]

    return problem


def print_solution(
    problem: LpProblem,
    num_years: int,
    carriers: list[str],
    destinations: list[str],
    shipment_target: list[dict[str, float]],
    tier_min_quantity: list[int],
    discount_rate: dict[str, list[float]],
) -> None:
    """
    Pretty print the solution of the shipment optimization problem.
    """

    print("\n" + "=" * 80)
    print("SHIPMENT OPTIMIZATION RESULTS")
    print("=" * 80)

    status_code = problem.status
    status_name = LpStatus[status_code]

    print(f"\nSolver Status: {status_name} (code: {status_code})")

    # Handle different solution statuses
    if status_code == LpStatusOptimal:
        print(f"Optimal Total Cost: ${value(problem.objective):,.2f}")

    elif status_code == LpStatusInfeasible:
        print("\n⚠ PROBLEM IS INFEASIBLE ⚠")
        print("\nThe constraints cannot be satisfied simultaneously.")
        print("\nPossible reasons:")
        print("  1. Shipment targets exceed combined carrier capacity at any tier")
        print(
            "  2. Individual destination targets exceed any single carrier's capacity"
        )
        print("  3. Minimum tier quantities are too high to achieve with given targets")
        print(
            "  4. Conflicting constraints between tier requirements and shipment bounds"
        )

        print("\nDiagnostic Information:")
        print(
            f"  Total shipments needed (all years): {sum(sum(shipment_target[y].values()) for y in range(num_years)):,.0f}"
        )
        print(f"  Number of carriers: {len(carriers)}")
        print(f"  Number of destinations: {len(destinations)}")
        print(f"  Number of years: {num_years}")

        print("\n  Tier minimum quantities:")
        for i, min_qty in enumerate(tier_min_quantity):
            print(f"    Tier {i}: {min_qty:,} shipments")

        print("\n  Yearly shipment targets:")
        for year in range(num_years):
            year_total = sum(shipment_target[year].values())
            print(f"    Year {year}: {year_total:,.0f} total")
            for dest in destinations:
                print(f"      {dest}: {shipment_target[year][dest]:,.0f}")

        print("\nSuggestions:")
        print("  • Check if any single destination target exceeds maximum shipments")
        print("  • Verify tier minimums are achievable with your shipment volumes")
        print("  • Consider adding more carriers or relaxing constraints")
        print("  • Review if shipment bounds are too restrictive")
        return

    elif status_code == LpStatusUnbounded:  # -2 = Unbounded
        print("\n⚠ PROBLEM IS UNBOUNDED ⚠")
        print("\nThe objective function can be improved indefinitely.")
        print("This suggests an error in the model formulation:")
        print("  • Missing constraints that should limit the solution")
        print("  • Incorrect objective function (possibly wrong sign)")
        print("  • Variables without proper bounds")
        return

    elif status_code == LpStatusNotSolved:  # 0 = Not Solved
        print("\n⚠ PROBLEM NOT SOLVED ⚠")
        print("\nThe solver did not attempt to solve or did not complete.")
        print("Possible reasons:")
        print("  • Solver not found or not properly installed")
        print("  • Problem too large for available memory")
        print("  • Timeout reached before solution found")
        print("  • Solver configuration error")
        return

    elif status_code == -3:  # Undefined (solver-specific)
        print("\n⚠ SOLVER RETURNED UNDEFINED STATUS ⚠")
        print("\nThe solver encountered an issue:")
        print("  • Numerical difficulties")
        print("  • Model formulation issues")
        print("  • Solver-specific error")
        return

    else:
        print(f"\n⚠ UNKNOWN STATUS: {status_code} ⚠")
        print(
            f"Optimal Total Cost: ${value(problem.objective):,.2f}"
            if value(problem.objective)
            else "Cost unavailable"
        )
        return

    # OPTIMAL SOLUTION DISPLAY
    # Extract variable values
    print("\n" + "-" * 80)
    print("SHIPMENT ALLOCATION BY YEAR")
    print("-" * 80)

    for year in range(num_years):
        print(f"\n{'Year ' + str(year):=^80}")

        # Calculate yearly totals
        year_total_cost = 0
        year_total_shipments = 0

        for carrier in carriers:
            print(f"\n  {carrier}:")

            # Find active tier for this carrier in this year
            active_tier = None
            for tier in range(len(tier_min_quantity)):
                tier_var_name = f"tier_y{year}_{carrier}_t{tier}"
                for var in problem.variables():
                    if var.name == tier_var_name and value(var) > 0.5:
                        active_tier = tier
                        break
                if active_tier is not None:
                    break

            if active_tier is not None:
                discount_pct = (1 - discount_rate[carrier][active_tier]) * 100
                print(
                    f"    Active Tier: {active_tier} (Discount: {discount_pct:.1f}%, Multiplier: {discount_rate[carrier][active_tier]:.3f})"
                )
                print(f"    Min Required: {tier_min_quantity[active_tier]:,} shipments")

            # Calculate carrier totals for this year
            carrier_shipments = 0
            carrier_cost = 0

            print(
                f"\n    {'Destination':<15} {'Shipments':>12} {'Target':>12} {'Cost':>15}"
            )
            print(f"    {'-' * 15} {'-' * 12} {'-' * 12} {'-' * 15}")

            for dest in destinations:
                dest_shipments = 0
                dest_cost = 0

                # Sum across all tiers (though only one should be non-zero)
                for tier in range(len(tier_min_quantity)):
                    var_name = f"ship_y{year}_{carrier}_t{tier}_{dest}"
                    for var in problem.variables():
                        if var.name == var_name:
                            shipments = value(var)
                            if shipments is not None and shipments > 0:
                                dest_shipments += shipments
                                dest_cost += shipments * discount_rate[carrier][tier]
                            break

                carrier_shipments += dest_shipments
                carrier_cost += dest_cost

                if dest_shipments > 0:
                    print(
                        f"    {dest:<15} {dest_shipments:>12,.0f} {shipment_target[year][dest]:>12,.0f} ${dest_cost:>14,.2f}"
                    )

            print(f"    {'-' * 15} {'-' * 12} {'-' * 12} {'-' * 15}")
            print(
                f"    {'CARRIER TOTAL':<15} {carrier_shipments:>12,.0f} {'':>12} ${carrier_cost:>14,.2f}"
            )

            year_total_shipments += carrier_shipments
            year_total_cost += carrier_cost

        print(
            f"\n  {'YEAR TOTAL':<17} {year_total_shipments:>12,.0f} {'':>12} ${year_total_cost:>14,.2f}"
        )

    # Summary by destination
    print("\n" + "-" * 80)
    print("DESTINATION SUMMARY (All Years)")
    print("-" * 80)
    print(
        f"\n{'Destination':<15} {'Total Shipments':>18} {'Total Target':>18} {'Status':>10}"
    )
    print(f"{'-' * 15} {'-' * 18} {'-' * 18} {'-' * 10}")

    for dest in destinations:
        total_shipments = 0
        total_target = sum(shipment_target[year][dest] for year in range(num_years))

        for year in range(num_years):
            for carrier in carriers:
                for tier in range(len(tier_min_quantity)):
                    var_name = f"ship_y{year}_{carrier}_t{tier}_{dest}"
                    for var in problem.variables():
                        if var.name == var_name:
                            shipments = value(var)
                            if shipments is not None:
                                total_shipments += shipments
                            break

        status = "✓" if abs(total_shipments - total_target) < 0.01 else "✗"
        print(
            f"{dest:<15} {total_shipments:>18,.0f} {total_target:>18,.0f} {status:>10}"
        )

    # Carrier performance summary
    print("\n" + "-" * 80)
    print("CARRIER PERFORMANCE SUMMARY")
    print("-" * 80)
    print(
        f"\n{'Carrier':<15} {'Year':<8} {'Tier':<8} {'Shipments':>15} {'Discount':>12}"
    )
    print(f"{'-' * 15} {'-' * 8} {'-' * 8} {'-' * 15} {'-' * 12}")

    for carrier in carriers:
        for year in range(num_years):
            # Find active tier
            active_tier = None
            for tier in range(len(tier_min_quantity)):
                tier_var_name = f"tier_y{year}_{carrier}_t{tier}"
                for var in problem.variables():
                    if var.name == tier_var_name and value(var) > 0.5:
                        active_tier = tier
                        break
                if active_tier is not None:
                    break

            # Calculate total shipments for this carrier/year
            carrier_year_shipments = 0
            for dest in destinations:
                for tier in range(len(tier_min_quantity)):
                    var_name = f"ship_y{year}_{carrier}_t{tier}_{dest}"
                    for var in problem.variables():
                        if var.name == var_name:
                            shipments = value(var)
                            if shipments is not None:
                                carrier_year_shipments += shipments
                            break

            if active_tier is not None:
                discount_pct = (1 - discount_rate[carrier][active_tier]) * 100
                print(
                    f"{carrier:<15} {year:<8} {active_tier:<8} {carrier_year_shipments:>15,.0f} {discount_pct:>11.1f}%"
                )

    print("\n" + "=" * 80 + "\n")


def get_user_input() -> dict:
    """
    Prompt user via CLI to input all fixed parameters for the optimization problem.
    Returns a dictionary containing all the parameters.
    """
    base_shipments = 40000
    num_years = 2
    carriers = ["UPS", "FedEx"]
    destinations = ["A", "B", "C"]
    distribution_target = {"A": 0.5, "B": 0.35, "C": 0.15}
    shipment_target = [
        {
            dest: int((base_shipments * 1.3**i) * distribution_target[dest])
            for dest in destinations
        }
        for i in range(num_years)
    ]
    return {
        "num_years": num_years,
        "carriers": carriers,
        "destinations": destinations,
        "shipment_target": shipment_target,
        "shipment_cost": {
            "UPS": {"A": 5.0, "B": 8.0, "C": 10.0},
            "FedEx": {"A": 6.0, "B": 9.0, "C": 8.0},
        },
        "tier_min_quantity": [0, 5000, 50000, 100000],
        "discount_rate": {
            "UPS": [1.0, 0.97, 0.96, 0.95],
            "FedEx": [1.0, 0.96, 0.94, 0.93],
        },
    }


def main():
    params = get_user_input()

    problem = optimize_shipments(**params)
    problem.solve()

    print_solution(
        problem,
        params["num_years"],
        params["carriers"],
        params["destinations"],
        params["shipment_target"],
        params["tier_min_quantity"],
        params["discount_rate"],
    )


if __name__ == "__main__":
    main()
