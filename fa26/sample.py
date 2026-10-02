"""Sample helpers for the FA26 MuckRock slot-machine revenue work."""


def average_revenue_per_base(records):
    """Return average slot revenue per base.

    Each record is a dict with ``revenue`` and ``bases``.
    """
    if not records:
        return 0.0
    total_revenue = sum(row["revenue"] for row in records)
    total_bases = sum(row["bases"] for row in records)
    if total_bases == 0:
        return 0.0
    return total_revenue / total_bases


def main():
    sample = [
        {"branch": "Army", "region": "Korea", "bases": 5, "revenue": 100_568_956},
        {"branch": "Army", "region": "Europe", "bases": 12, "revenue": 56_722_390},
        {"branch": "Navy", "region": "Japan", "bases": 6, "revenue": 41_435_211},
    ]
    average = average_revenue_per_base(sample)
    print(f"Sample rows: {len(sample)}")
    print(f"Average revenue per base: ${average:,.0f}")


if __name__ == "__main__":
    main()
