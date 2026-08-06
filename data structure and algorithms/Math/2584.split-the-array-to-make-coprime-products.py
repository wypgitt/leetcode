#
# @lc app=leetcode id=2584 lang=python3
#
# [2584] Split the Array to Make Coprime Products
#
# --- Notes (problem, math, algorithm, DS, complexity, tests, edges, improvements, interview) ---
#
# Problem restatement
# Given nums (length n), find the smallest index i with 0 <= i <= n - 2 such that
#   gcd( nums[0] * ... * nums[i],  nums[i+1] * ... * nums[n-1] ) == 1.
# If none exists, return -1.
# Equivalently: split into two non-empty contiguous parts whose PRODUCTS are coprime.
#
# Number theory reduction
# gcd(A, B) > 1 iff some prime p divides both A and B.
# The product of a subarray is divisible by p iff at least one element in that subarray is
# divisible by p. So the split after i is VALID iff no prime p divides an element on BOTH sides
# of the split — i.e. there is no prime whose occurrences straddle the boundary between i and i+1.
#
# Why not multiply huge products?
# nums can be large; products overflow and are unnecessary. Only prime presence matters.
#
# Algorithm (two-pointer / sweep with frequency counts)
# Pre-count, for each prime p, how many ARRAY POSITIONS (elements) to the RIGHT of the scan will
# still contain p after we remove indices — implemented as a multiset counter over positions:
#   - Build rightPrimeFactors: for each nums[k], for each distinct prime p | nums[k], increment
#     rightPrimeFactors[p] (number of not-yet-processed indices on the right that still owe p).
# Actually the editorial counts: total occurrences-weighted by elements — each index contributes
# once per distinct prime dividing nums[i].
#
# Sweep i = 0 .. n-2:
#   Move nums[i] from "right side" to "left side" conceptually:
#   For each distinct prime p in nums[i]:
#     Decrement rightPrimeFactors[p].
#     If it becomes 0: p no longer appears strictly to the right of i — remove p from both counters
#       (nothing left on right; no "spanning" concern for p).
#     Else: p still appears somewhere to the right of i, AND already appears in nums[0..i], so p
#       spans the split after i — record that by incrementing leftPrimeFactors[p] (or equivalent).
#   After updating, if leftPrimeFactors is empty, NO prime spans both sides -> split after i works.
# Return the first such i (scan order is increasing i -> smallest valid split).
#
# Correctness sketch
# After processing index i, leftPrimeFactors[p] > 0 iff p divides some element in nums[0..i] AND
# some element in nums[i+1..n-1]. That is exactly "p bridges the boundary". Empty map <=> no such p.
#
# Data structures
# - collections.Counter (or two dicts) for right-side multiplicities and "bridging" primes.
# - Unique prime factors per nums[i] from trial division / sieve — list of ints per element.
# - When right[p] hits 0, use left_bridge.pop(p, None): p may only exist on the left now and never
#   entered left_bridge (safe across Python versions).
#
# Prime factorization helper
# For nums[i] <= 10^6 (typical constraint), trial divide up to min(1000, num): any composite <= 10^6
# has a factor <= 1000. After stripping small factors, what remains is 1 or a prime > 1000 (append).
# Edge: nums[i] == 1 has no prime factors — contributes nothing to counters.
#
# Time complexity
# - Building right counts: O(n * F) where F is number of trial divisions per value (~sqrt(V) worst,
#   bounded ~1000 iterations with the min(1000, num) trick for V <= 10^6).
# - Sweep: O(n * F) updates.
# Overall O(n * sqrt(V)) worst-case editorial bound, O(n * constant) for fixed V cap.
#
# Space complexity
# - O(P) for distinct primes in the whole array (P <= total prime factors across nums), plus O(n)
#   only implicitly through recursion stack none — O(P) counters.
#
# Edge cases
# - n == 2: only i = 0 is candidate.
# - Value 1: no primes; does not create spanning by itself.
# - All numbers share a prime (e.g. all even): no valid split -> -1.
# - Pairwise coprime consecutive groups: early split often at smallest i.
#
# Tests (mental / small)
# - [3, 5]: split after 0 -> gcd(3,5)=1 -> answer 0.
# - [2, 4]: share factor 2 -> -1.
#
# Improvements
# - Precompute smallest-prime-factor (SPF) sieve up to max(nums) for O(log n) factorization per value.
# - Interval-merge variant: record first/last index per prime, sweep mx last index — same goal,
#   alternative implementation (good for interviews).
#
# LeetCode submission
# Place imports (`collections`, `typing.List`) inside the marked code region.

# @lc code=start
import collections
from typing import List


class Solution:
    def findValidSplit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Find the smallest split index i so the product of nums[0..i] is coprime with
        the product of nums[i+1..]. Equivalent to: no prime appears on both sides.

        Algorithm:
        - Factor each value; count prime occurrences on the right.
        - Sweep i left-to-right, moving primes to the left; track primes that still
          bridge both sides. First i with an empty bridge set is the answer.

        Complexity: O(n * sqrt(V)) time, O(P) space for distinct primes.
        """
        def prime_factors(num: int) -> List[int]:
            if num <= 1:
                return []
            factors: List[int] = []
            x = num
            for d in range(2, min(1000, x) + 1):
                if x % d == 0:
                    factors.append(d)
                    while x % d == 0:
                        x //= d
            if x > 1:
                factors.append(x)
            return factors

        right = collections.Counter()
        for v in nums:
            for p in prime_factors(v):
                right[p] += 1

        left_bridge = collections.Counter()
        for i in range(len(nums) - 1):
            for p in prime_factors(nums[i]):
                right[p] -= 1
                if right[p] == 0:
                    right.pop(p)
                    left_bridge.pop(p, None)
                else:
                    left_bridge[p] += 1
            if not left_bridge:
                return i
        return -1

    def findValidSplit_interval(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate classic: for each prime, record first/last index where it appears;
        a valid split must be after every prime's last occurrence that started on the left.

        Algorithm:
        - Factor each nums[i]; track first/last index per prime.
        - Sweep i, maintain max last-index among primes whose first index <= i.
        - If max_last == i, split after i is valid (no prime crosses i+1).

        Complexity: O(n * sqrt(V)) time, O(P) space.
        """
        def prime_factors(num: int) -> List[int]:
            if num <= 1:
                return []
            factors: List[int] = []
            x = num
            for d in range(2, min(1000, x) + 1):
                if x % d == 0:
                    factors.append(d)
                    while x % d == 0:
                        x //= d
            if x > 1:
                factors.append(x)
            return factors

        first = {}
        last = {}
        for i, v in enumerate(nums):
            for p in prime_factors(v):
                if p not in first:
                    first[p] = i
                last[p] = i

        # For each index, the farthest end among primes starting at this index
        far = [0] * len(nums)
        for p, f in first.items():
            far[f] = max(far[f], last[p])

        mx = 0
        for i in range(len(nums) - 1):
            mx = max(mx, far[i])
            if mx == i:
                return i
        return -1
# @lc code=end
