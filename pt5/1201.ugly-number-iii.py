from __future__ import annotations

from math import gcd


class Solution:
    def nthUglyNumber(self, n: int, a: int, b: int, c: int) -> int:
        def lcm(x: int, y: int) -> int:
            return x // gcd(x, y) * y

        ab = lcm(a, b)
        ac = lcm(a, c)
        bc = lcm(b, c)
        abc = lcm(ab, c)

        def count_ugly(limit: int) -> int:
            return (
                limit // a
                + limit // b
                + limit // c
                - limit // ab
                - limit // ac
                - limit // bc
                + limit // abc
            )

        left, right = 1, 2_000_000_000
        while left < right:
            mid = (left + right) // 2
            if count_ugly(mid) >= n:
                right = mid
            else:
                left = mid + 1

        return left

