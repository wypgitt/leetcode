#
# @lc app=leetcode id=2025 lang=python3
#
# [2025] Maximum Number of Ways to Partition an Array
#
# https://leetcode.com/problems/maximum-number-of-ways-to-partition-an-array/description/
#
# algorithms
# Hard (35.93%)
# Likes:    525
# Dislikes: 59
# Total Accepted:    14.4K
# Total Submissions: 40K
# Testcase Example:  "[2,-1,2]\n3"
#
# You are given a 0-indexed integer array nums of length n. The number of ways
# to partition nums is the number of pivot indices that satisfy both conditions:
#
#
# 1 <= pivot < n
#
#
# nums[0] + nums[1] + ... + nums[pivot - 1] == nums[pivot] + nums[pivot + 1] +
# ... + nums[n - 1]
#
# You are also given an integer k. You can choose to change the value of one
# element of nums to k, or to leave the array unchanged.
#
# Return the maximum possible number of ways to partition nums to satisfy both
# conditions after changing at most one element.
#
#
#
# Example 1:
#
# Input: nums = [2,-1,2], k = 3
# Output: 1
# Explanation: One optimal approach is to change nums[0] to k. The array becomes
# [3,-1,2].
# There is one way to partition the array:
# - For pivot = 2, we have the partition [3,-1 | 2]: 3 + -1 == 2.
#
# Example 2:
#
# Input: nums = [0,0,0], k = 1
# Output: 2
# Explanation: The optimal approach is to leave the array unchanged.
# There are two ways to partition the array:
# - For pivot = 1, we have the partition [0 | 0,0]: 0 == 0 + 0.
# - For pivot = 2, we have the partition [0,0 | 0]: 0 + 0 == 0.
#
# Example 3:
#
# Input: nums = [22,4,-25,-20,-15,15,-16,7,19,-10,0,-13,-14], k = -33
# Output: 4
# Explanation: One optimal approach is to change nums[2] to k. The array becomes
# [22,4,-33,-20,-15,15,-16,7,19,-10,0,-13,-14].
# There are four ways to partition the array.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 2 <= n <= 10^5
#
#
# -10^5 <= k, nums[i] <= 10^5
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def waysToPartition(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count pivots with equal left/right sums. Optionally change one element
        to k (or none); maximize valid pivots.

        Algorithm:
        - Prefix sums; baseline count 2*pref==total.
        - Sweep change index with left/right Counters of prefix values.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * n
        pref[0] = nums[0]
        for i in range(1, n):
            pref[i] = pref[i - 1] + nums[i]
        total = pref[-1]
        ans = sum(1 for i in range(n - 1) if pref[i] * 2 == total)
        left = Counter()
        right = Counter(pref[i] for i in range(n - 1))
        best = ans
        for j in range(n):
            delta = k - nums[j]
            newt = total + delta
            ways = 0
            if newt % 2 == 0:
                ways += left[newt // 2]
            need = total - delta
            if need % 2 == 0:
                ways += right[need // 2]
            best = max(best, ways)
            if j < n - 1:
                left[pref[j]] += 1
                right[pref[j]] -= 1
        return best
# @lc code=end
