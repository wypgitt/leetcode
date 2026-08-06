#
# @lc app=leetcode id=3850 lang=python3
#
# [3850] Count Sequences to K
#
# https://leetcode.com/problems/count-sequences-to-k/description/
#
# algorithms
# Hard (36.21%)
# Likes:    95
# Dislikes: 7
# Total Accepted:    16.3K
# Total Submissions: 45K
# Testcase Example:  "[2,3,2]\n6"
#
#
# You are given an integer array nums, and an integer k.
#
# Start with an initial value val = 1 and process nums from left to right.
# At each index i, you must choose exactly one of the following actions:
#
# Multiply val by nums[i].
#
# Divide val by nums[i].
#
# Leave val unchanged.
#
# After processing all elements, val is considered equal to k only if its
# final rational value exactly equals k.
#
# Return the count of distinct sequences of choices that result in val ==
# k.
#
# Note: Division is rational (exact), not integer division. For example, 2
# / 4 = 1 / 2.
#
# Example 1:
#
# Input: nums = [2,3,2], k = 6
#
# Output: 2
#
# Explanation:
#
# The following 2 distinct sequences of choices result in val == k:
#
#                         Sequence
#                         Operation on nums[0]
#                         Operation on nums[1]
#                         Operation on nums[2]
#                         Final val
#
#                         1
#                         Multiply: val = 1 * 2 = 2
#                         Multiply: val = 2 * 3 = 6
#                         Leave val unchanged
#                         6
#
#                         2
#                         Leave val unchanged
#                         Multiply: val = 1 * 3 = 3
#                         Multiply: val = 3 * 2 = 6
#                         6
#
# Example 2:
#
# Input: nums = [4,6,3], k = 2
#
# Output: 2
#
# Explanation:
#
# The following 2 distinct sequences of choices result in val == k:
#
#                         Sequence
#                         Operation on nums[0]
#                         Operation on nums[1]
#                         Operation on nums[2]
#                         Final val
#
#                         1
#                         Multiply: val = 1 * 4 = 4
#                         Divide: val = 4 / 6 = 2 / 3
#                         Multiply: val = (2 / 3) * 3 = 2
#                         2
#
#                         2
#                         Leave val unchanged
#                         Multiply: val = 1 * 6 = 6
#                         Divide: val = 6 / 3 = 2
#                         2
#
# Example 3:
#
# Input: nums = [1,5], k = 1
#
# Output: 3
#
# Explanation:
#
# The following 3 distinct sequences of choices result in val == k:
#
#                         Sequence
#                         Operation on nums[0]
#                         Operation on nums[1]
#                         Final val
#
#                         1
#                         Multiply: val = 1 * 1 = 1
#                         Leave val unchanged
#                         1
#
#                         2
#                         Divide: val = 1 / 1 = 1
#                         Leave val unchanged
#                         1
#
#                         3
#                         Leave val unchanged
#                         Leave val unchanged
#                         1
#
# Constraints:
#
# 1 <= nums.length <= 19
#
# 1 <= nums[i] <= 6
#
# 1 <= k <= 10^15
#

# @lc code=start
from collections import Counter
from typing import List, Tuple


class Solution:
    def countSequences(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Starting from 1, for each nums[i] multiply, divide, or skip. Count
        sequences whose final rational value equals k.

        Algorithm:
        - Factor everything into primes {2,3,5}; if k has another prime, answer 0.
        - DP over exponent triples (a,b,c) for 2^a 3^b 5^c; each step branches
          to same, +factors, or -factors.
        - Return ways to reach k's exponent triple.

        Complexity: O(n * S) time where S is #reachable states, O(S) space.
        """
        target, reachable = self._factor_target(k)
        if not reachable:
            return 0

        dp = Counter({(0, 0, 0): 1})

        for num in nums:
            da, db, dc = self._factor_small(num)
            nxt = Counter()

            for (a, b, c), ways in dp.items():
                nxt[(a, b, c)] += ways
                nxt[(a + da, b + db, c + dc)] += ways
                nxt[(a - da, b - db, c - dc)] += ways

            dp = nxt

        return dp[target]

    def _factor_target(self, value: int) -> Tuple[Tuple[int, int, int], bool]:
        exponents = []
        for prime in (2, 3, 5):
            count = 0
            while value % prime == 0:
                value //= prime
                count += 1
            exponents.append(count)
        return (exponents[0], exponents[1], exponents[2]), value == 1

    def _factor_small(self, value: int) -> Tuple[int, int, int]:
        exponents = []
        for prime in (2, 3, 5):
            count = 0
            while value % prime == 0:
                value //= prime
                count += 1
            exponents.append(count)
        return exponents[0], exponents[1], exponents[2]
# @lc code=end
