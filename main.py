import sys
import importlib

PROBLEMS = {"warehouse_shipments", "carrier_earned_discount"}


def print_banner():
    """Print the main banner."""
    print("\n" + "=" * 80)
    print("OPTIMIZATION TOOLKIT".center(80))
    print("=" * 80)
    print()


def list_all_problems():
    """Display available optimization problems."""
    print("Available Optimization Problems:")
    print("-" * 80)
    for i, problem in enumerate(PROBLEMS):
        print(f"\n  {i}. {problem}")
    print("\n" + "-" * 80)


def select_problem() -> str:
    """Prompt user to select a problem."""
    while True:
        choice = input("\nEnter problem (or 'q' to quit): ").strip().lower()

        if choice == "q":
            print("\nExiting...")
            sys.exit(0)

        if choice in PROBLEMS:
            return choice

        print(f"  Error: '{choice}' is not a valid problem code.")
        print(f"  Valid codes: {', '.join(PROBLEMS)}")


def build_module_path(module: str) -> str:
    """Return the module path of a selected module"""
    return f"problems.{module}.main"


def main():
    print_banner()
    list_all_problems()
    selected = select_problem()
    module = importlib.import_module(build_module_path(selected))
    module.main()


if __name__ == "__main__":
    main()
