"""
Approach: Sieve of Eratosthenes.
Data structure: a boolean array marks whether each number below n is still considered prime.
Interview logic: when p is prime, every multiple of p starting at p*p has a smaller factor p and is composite. Numbers below p*p were already marked by smaller primes.
Complexity: O(n log log n) time, O(n) space.
Tests and edge cases: n <= 2 returns 0; small n like 3 returns 1; square boundaries are handled by starting at p*p.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def countPrimes(self, n: int) -> int:
        if n <= 2:
            return 0
        prime = [True] * n
        prime[0] = prime[1] = False
        p = 2
        while p * p < n:
            if prime[p]:
                for multiple in range(p * p, n, p):
                    prime[multiple] = False
            p += 1
        return sum(prime)
# @lc code=end
