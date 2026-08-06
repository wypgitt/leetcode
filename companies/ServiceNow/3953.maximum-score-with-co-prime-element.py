#
# @lc app=leetcode id=3953 lang=python3
#
# [3953] Maximum Score with Co-Prime Element
#
# https://leetcode.com/problems/maximum-score-with-co-prime-element/description/
#
# algorithms
# Hard (28.70%)
# Likes:    25
# Dislikes: 5
# Total Accepted:    3.8K
# Total Submissions: 13.2K
# Testcase Example:  "[3,4,6]\n5"
#
#
# You are given an integer array nums of length n and an integer maxVal.
#
# You may change any element in nums to any positive integer less than or
# equal to maxVal. Each such change costs 1.
#
# Two integers are co-prime if their greatest common divisor (GCD) is 1.
#
# After all modifications, you must choose an index i such that, nums[i]
# is co-prime with every other element nums[j].
#
# Let:
#
# selectedValue be the final value of nums[i] after modifications.
#
# modificationCost be the total number of elements changed.
#
# The score is defined as score = selectedValue - modificationCost.
#
# Return the maximum possible score.
#
# Example 1:
#
# Input: nums = [3,4,6], maxVal = 5
#
# Output: 4
#
# Explanation:
#
# Change nums[2] from 6 to 5, which costs 1. Choose nums[2] = 5, since it
# is co-prime with 3 and 4.
#
# selectedValue = 5
#
# modificationCost = 1
#
# The score is 5 - 1 = 4
#
# Example 2:
#
# Input: nums = [1,2,3], maxVal = 4
#
# Output: 3
#
# Explanation:
#
# No modifications are required. Choose nums[2] = 3, since it is co-prime
# with 1 and 2.
#
# selectedValue = 3
#
# modificationCost = 0
#
# The score is 3 - 0 = 3
#
# Example 3:
#
# Input: nums = [2,2], maxVal = 1
#
# Output: 1
#
# Explanation:
#
# Change nums[0] from 2 to 1, which costs 1. Choose nums[1] = 2, since it
# is co-prime with 1.
#
# selectedValue = 2
#
# modificationCost = 1
#
# The score is ​​​​​​​2 - 1 = 1
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 1 <= maxVal <= 10^​​​​​​​5
#

# @lc code=start
from typing import List


class Solution:
    def maxScore(self, nums: List[int], maxVal: int) -> int:
        """
        Interview explanation:
        Score = selectedValue − (#changes). The selected value V must be
        coprime with every other final element. Use inclusion-exclusion over
        prime-factor subsets to count non-coprime array elements for each V.

        Algorithm:
        - Sieve unique prime factors up to 1e5.
        - For each array value, add all nonempty prime-subset products into cnt.
        - For each candidate V (≤maxVal or present in nums), cost =
          not_coprime_count, minus 1 if V already occurs (select that slot);
          if V is absent and everything is already coprime, cost = 1 to place V.
        - Maximize V − cost (baseline includes V=1).

        Complexity: O(U log log U + n·2^ω + M·2^ω) with U,M≤1e5, ω≤6.
        """
        U = 10**5 + 1
        pf = [[] for _ in range(U)]
        for i in range(2, U):
            if not pf[i]:
                for j in range(i, U, i):
                    pf[j].append(i)

        cnt = [0] * U
        present = [0] * U
        for x in nums:
            if x < U:
                present[x] += 1
            sz = len(pf[x])
            for mask in range(1, 1 << sz):
                prod = 1
                for b in range(sz):
                    if mask >> b & 1:
                        prod *= pf[x][b]
                if prod < U:
                    cnt[prod] += 1

        def not_coprime(x: int) -> int:
            primes = pf[x]
            sz = len(primes)
            total = 0
            for mask in range(1, 1 << sz):
                prod = 1
                bits = 0
                for b in range(sz):
                    if mask >> b & 1:
                        prod *= primes[b]
                        bits += 1
                if prod < U:
                    total += cnt[prod] if bits & 1 else -cnt[prod]
            return total

        res = 1  # choose value 1
        for v in range(2, maxVal + 1):
            bad = not_coprime(v)
            if present[v] == 0:
                cost = 1 if bad == 0 else bad
            else:
                cost = bad - 1
            res = max(res, v - cost)

        for ele in nums:
            if ele == 1:
                continue
            bad = not_coprime(ele)
            res = max(res, ele - (bad - 1))
        return res
# @lc code=end
