#
# @lc app=leetcode id=1755 lang=python3
#
# [1755] Closest Subsequence Sum
#
# https://leetcode.com/problems/closest-subsequence-sum/description/
#
# algorithms
# Hard (44.58%)
# Likes:    1041
# Dislikes: 74
# Total Accepted:    30.6K
# Total Submissions: 68.7K
# Testcase Example:  "[5,-7,3,5]"
#
# You are given an integer array nums and an integer goal.
#
# You want to choose a subsequence of nums such that the sum of its elements is
# the closest possible to goal. That is, if the sum of the subsequence's
# elements is sum, then you want to minimize the absolute difference abs(sum -
# goal).
#
# Return the minimum possible value of abs(sum - goal).
#
# Note that a subsequence of an array is an array formed by removing some
# elements (possibly all or none) of the original array.
#
# Example 1:
#
# Input: nums = [5,-7,3,5], goal = 6
# Output: 0
# Explanation: Choose the whole array as a subsequence, with a sum of 6.
# This is equal to the goal, so the absolute difference is 0.
#
# Example 2:
#
# Input: nums = [7,-9,15,-2], goal = -5
# Output: 1
# Explanation: Choose the subsequence [7,-9,-2], with a sum of -4.
# The absolute difference is abs(-4 - (-5)) = abs(1) = 1, which is the minimum.
#
# Example 3:
#
# Input: nums = [1,2,3], goal = -7
# Output: 7
#
# Constraints:
#
# 1 <= nums.length <= 40
#
# -10^7 <= nums[i] <= 10^7
#
# -10^9 <= goal <= 10^9
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def minAbsDifference(self, nums: List[int], goal: int) -> int:
        """
        Interview explanation:
        Classic meet-in-the-middle (n≤40): split halves; enumerate all subset
        sums; for each left sum s binary-search right sum closest to goal−s.

        Algorithm:
        - Expand subset sums for each half; sort right; bisect closest for each left.

        Complexity: O(2^{n/2} * n) time, O(2^{n/2}) space.
        """
        def subset_sums(arr: List[int]) -> List[int]:
            sums = [0]
            for x in arr:
                sums += [s + x for s in sums]
            return sums

        mid = len(nums) // 2
        left = subset_sums(nums[:mid])
        right = sorted(subset_sums(nums[mid:]))
        ans = abs(goal)
        for s in left:
            need = goal - s
            i = bisect.bisect_left(right, need)
            if i < len(right):
                ans = min(ans, abs(need - right[i]))
            if i > 0:
                ans = min(ans, abs(need - right[i - 1]))
        return ans

    def minAbsDifference_dfs(self, nums: List[int], goal: int) -> int:
        """
        Interview explanation:
        Alternate meet-in-the-middle with DFS enumeration of subset sums
        (same asymptotics; recursive form).

        Algorithm:
        - DFS fill left/right lists; sort right; binary search closest.

        Complexity: O(2^{n/2} * n) time, O(2^{n/2}) space.
        """
        def dfs(arr, i, cur, out):
            if i == len(arr):
                out.append(cur)
                return
            dfs(arr, i + 1, cur, out)
            dfs(arr, i + 1, cur + arr[i], out)

        mid = len(nums) // 2
        left, right = [], []
        dfs(nums[:mid], 0, 0, left)
        dfs(nums[mid:], 0, 0, right)
        right.sort()
        ans = abs(goal)
        for s in left:
            need = goal - s
            i = bisect.bisect_left(right, need)
            if i < len(right):
                ans = min(ans, abs(right[i] - need))
            if i:
                ans = min(ans, abs(right[i - 1] - need))
        return ans
# @lc code=end
