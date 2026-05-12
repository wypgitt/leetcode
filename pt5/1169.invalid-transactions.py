from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, List, Tuple


class Solution:
    def invalidTransactions(self, transactions: List[str]) -> List[str]:
        parsed: List[Tuple[str, int, int, str]] = []
        by_name: DefaultDict[str, List[int]] = defaultdict(list)
        invalid = [False] * len(transactions)

        for i, transaction in enumerate(transactions):
            name, time, amount, city = transaction.split(",")
            parsed.append((name, int(time), int(amount), city))
            by_name[name].append(i)
            if int(amount) > 1000:
                invalid[i] = True

        for indices in by_name.values():
            for i in range(len(indices)):
                name_i, time_i, _, city_i = parsed[indices[i]]
                for j in range(i + 1, len(indices)):
                    name_j, time_j, _, city_j = parsed[indices[j]]
                    if name_i == name_j and abs(time_i - time_j) <= 60 and city_i != city_j:
                        invalid[indices[i]] = True
                        invalid[indices[j]] = True

        return [transaction for i, transaction in enumerate(transactions) if invalid[i]]

