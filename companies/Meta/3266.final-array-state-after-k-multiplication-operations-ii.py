#
# @lc app=leetcode id=3266 lang=python3
#
# [3266] Final Array State After K Multiplication Operations II
#
# https://leetcode.com/problems/final-array-state-after-k-multiplication-operations-ii/description/
#
# algorithms
# Hard (13.80%)
# Likes:    181
# Dislikes: 24
# Total Accepted:    12.2K
# Total Submissions: 88.5K
# Testcase Example:  "[2,1,3,5,6]\n5\n2"
#
#
# You are given an integer array nums, an integer k, and an integer
# multiplier.
#
# You need to perform k operations on nums. In each operation:
#
# Find the minimum value x in nums. If there are multiple occurrences of
# the minimum value, select the one that appears first.
#
# Replace the selected minimum value x with x * multiplier.
#
# After the k operations, apply modulo 10^9 + 7 to every value in nums.
#
# Return an integer array denoting the final state of nums after
# performing all k operations and then applying the modulo.
#
# Example 1:
#
# Input: nums = [2,1,3,5,6], k = 5, multiplier = 2
#
# Output: [8,4,6,5,6]
#
# Explanation:
#
#                         Operation
#                         Result
#
#                         After operation 1
#                         [2, 2, 3, 5, 6]
#
#                         After operation 2
#                         [4, 2, 3, 5, 6]
#
#                         After operation 3
#                         [4, 4, 3, 5, 6]
#
#                         After operation 4
#                         [4, 4, 6, 5, 6]
#
#                         After operation 5
#                         [8, 4, 6, 5, 6]
#
#                         After applying modulo
#                         [8, 4, 6, 5, 6]
#
# Example 2:
#
# Input: nums = [100000,2000], k = 2, multiplier = 1000000
#
# Output: [999999307,999999993]
#
# Explanation:
#
#                         Operation
#                         Result
#
#                         After operation 1
#                         [100000, 2000000000]
#
#                         After operation 2
#                         [100000000000, 2000000000]
#
#                         After applying modulo
#                         [999999307, 999999993]
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= 10^9
#
# 1 <= multiplier <= 10^6
#

# @lc code=start

from typing import List
import heapq


class Solution:
    def getFinalState(self, nums: List[int], k: int, multiplier: int) -> List[int]:
        """
        Interview explanation:
        Same min-multiply process as I, but k ≤ 1e9 so simulate only until every
        value is in a tight band, then distribute remaining multiplies evenly with
        modular exponentiation.

        Algorithm:
        - If multiplier == 1: return nums mod 1e9+7.
        - Heap-simulate while min * multiplier <= current global max and k > 0.
        - Sort remaining heap; each of the smallest (k % n) gets one extra multiply
          beyond k // n; ans[i] = val * mult^times mod MOD.

        Complexity: O(n log n * log A + n log k) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        if multiplier == 1:
            return [x % MOD for x in nums]

        h = [(x, i) for i, x in enumerate(nums)]
        heapq.heapify(h)
        mx = max(nums)
        while k and h[0][0] * multiplier <= mx:
            v, i = heapq.heappop(h)
            v *= multiplier
            mx = max(mx, v)
            heapq.heappush(h, (v, i))
            k -= 1

        arr = sorted(h)
        q, r = divmod(k, n)
        ans = [0] * n
        for j, (v, i) in enumerate(arr):
            times = q + (1 if j < r else 0)
            ans[i] = (v % MOD) * pow(multiplier, times, MOD) % MOD
        return ans
# @lc code=end
