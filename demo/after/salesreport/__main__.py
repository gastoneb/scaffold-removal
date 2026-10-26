import csv
import json
import sys


def read_rows(path):
    with open(path, newline="") as handle:
        for number, record in enumerate(csv.DictReader(handle), start=2):
            region = (record.get("region") or "").strip()
            if not region:
                raise ValueError(f"line {number}: missing region")
            try:
                amount = float(record.get("amount"))
            except (TypeError, ValueError):
                raise ValueError(f"line {number}: invalid amount {record.get('amount')!r}")
            yield region, amount


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python -m salesreport FILE", file=sys.stderr)
        return 2
    try:
        totals = {}
        for region, amount in read_rows(argv[0]):
            totals[region] = totals.get(region, 0.0) + amount
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps({r: round(t, 2) for r, t in sorted(totals.items())}, indent=2))
    return 0


sys.exit(main())
