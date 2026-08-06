#
# @lc app=leetcode id=2902 lang=python3
#
# [2902] Count of Sub-Multisets With Bounded Sum
#
# https://leetcode.com/problems/count-of-sub-multisets-with-bounded-sum/description/
#
# algorithms
# Hard (22.81%)
# Likes:    164
# Dislikes: 27
# Total Accepted:    6.4K
# Total Submissions: 27.9K
# Testcase Example:  "[1,2,2,3]\n6\n6"
#
#
# You are given a 0-indexed array nums of non-negative integers, and two
# integers l and r.
#
# Return the count of sub-multisets within nums where the sum of elements
# in each subset falls within the inclusive range of [l, r].
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# A sub-multiset is an unordered collection of elements of the array in
# which a given value x can occur 0, 1, ..., occ[x] times, where occ[x] is
# the number of occurrences of x in the array.
#
# Note that:
#
# Two sub-multisets are the same if sorting both sub-multisets results in
# identical multisets.
#
# The sum of an empty multiset is 0.
#
# Example 1:
#
# Input: nums = [1,2,2,3], l = 6, r = 6
# Output: 1
# Explanation: The only subset of nums that has a sum of 6 is {1, 2, 3}.
#
# Example 2:
#
# Input: nums = [2,1,4,2,7], l = 1, r = 5
# Output: 7
# Explanation: The subsets of nums that have a sum within the range [1, 5]
# are {1}, {2}, {4}, {2, 2}, {1, 2}, {1, 4}, and {1, 2, 2}.
#
# Example 3:
#
# Input: nums = [1,2,1,3,5,2], l = 3, r = 5
# Output: 9
# Explanation: The subsets of nums that have a sum within the range [3, 5]
# are {3}, {5}, {1, 2}, {1, 3}, {2, 2}, {2, 3}, {1, 1, 2}, {1, 1, 3}, and
# {1, 2, 2}.
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# 0 <= nums[i] <= 2 * 10^4
#
# Sum of nums does not exceed 2 * 10^4.
#
# 0 <= l <= r <= 2 * 10^4
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def countSubMultisets(self, nums: List[int], l: int, r: int) -> int:
        """
        Interview explanation:
        Count distinct sub-multisets whose element sum lies in [l, r]
        (empty sum 0). Answer mod 10^9+7. Zeros only multiply the count.

        Algorithm:
        - Frequency map; knapsack over positive values with at most c copies.
        - For value x with freq c: on each residue mod x, sliding-window sum
          of the last (c+1) prior dp entries (0..c copies).
        - Multiply by (zeros+1); sum dp[l..r].

        Complexity: O(r * distinct) time, O(r) space.
        """
        MOD = 10**9 + 7
        cnt = Counter(nums)
        zeros = cnt.pop(0, 0)
        dp = [1] + [0] * r
        for x, c in cnt.items():
            ndp = [0] * (r + 1)
            for rem in range(x):
                window = 0
                vals = []
                pos = rem
                while pos <= r:
                    window = (window + dp[pos]) % MOD
                    vals.append(dp[pos])
                    if len(vals) > c + 1:
                        window = (window - vals[-(c + 2)]) % MOD
                    ndp[pos] = window
                    pos += x
            dp = ndp
        return (zeros + 1) * sum(dp[l : r + 1]) % MOD
# @lc code=end
