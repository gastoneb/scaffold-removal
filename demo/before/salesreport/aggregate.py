from collections import OrderedDict


def aggregate(rows, sort_by="region", decimals=2):
    totals = OrderedDict()
    for row in rows:
        totals[row["region"]] = totals.get(row["region"], 0.0) + row["amount"]
    items = list(totals.items())
    if sort_by == "region":
        items.sort(key=lambda item: item[0])
    elif sort_by == "total":
        items.sort(key=lambda item: item[1], reverse=True)
    else:
        raise ValueError(f"unknown sort key: {sort_by}")
    return OrderedDict((region, round(total, decimals)) for region, total in items)
