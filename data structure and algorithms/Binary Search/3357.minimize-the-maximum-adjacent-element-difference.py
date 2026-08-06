#
# @lc app=leetcode id=3357 lang=python3
#
# [3357] Minimize the Maximum Adjacent Element Difference
#
# https://leetcode.com/problems/minimize-the-maximum-adjacent-element-difference/description/
#
# algorithms
# Hard (20.09%)
# Likes:    65
# Dislikes: 14
# Total Accepted:    3.8K
# Total Submissions: 19.1K
# Testcase Example:  "[1,2,-1,10,8]"
#
#
# You are given an array of integers nums. Some values in nums are missing
# and are denoted by -1.
#
# You must choose a pair of positive integers (x, y) exactly once and
# replace each missing element with either x or y.
#
# You need to minimize the maximum absolute difference between adjacent
# elements of nums after replacements.
#
# Return the minimum possible difference.
#
# Example 1:
#
# Input: nums = [1,2,-1,10,8]
#
# Output: 4
#
# Explanation:
#
# By choosing the pair as (6, 7), nums can be changed to [1, 2, 6, 10, 8].
#
# The absolute differences between adjacent elements are:
#
# |1 - 2| == 1
#
# |2 - 6| == 4
#
# |6 - 10| == 4
#
# |10 - 8| == 2
#
# Example 2:
#
# Input: nums = [-1,-1,-1]
#
# Output: 0
#
# Explanation:
#
# By choosing the pair as (4, 4), nums can be changed to [4, 4, 4].
#
# Example 3:
#
# Input: nums = [-1,10,-1,8]
#
# Output: 1
#
# Explanation:
#
# By choosing the pair as (11, 9), nums can be changed to [11, 10, 9, 8].
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# nums[i] is either -1 or in the range [1, 10^9].
#

# @lc code=start

from typing import List
import itertools


class Solution:
    def minDifference(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Fill every -1 using one global pair (x,y). Minimize the max adjacent
        |diff|. Fixed adjacent positives give a lower bound; optimal (x,y) are
        near the min/max positives bordering gaps → binary search the max gap m
        with x=mn+m, y=mx-m.

        Algorithm:
        - Compute max fixed gap; mn/mx among positives next to a -1.
        - Binary search m; verify all interior/boundary -1 gaps with (x,y).

        Complexity: O(n log M) time, O(1) extra space.
        """
        max_fixed = 0
        mn, mx = 10**9, 0
        for a, b in itertools.pairwise(nums):
            if (a == -1) != (b == -1):
                positive = max(a, b)
                mn = min(mn, positive)
                mx = max(mx, positive)
            else:
                max_fixed = max(max_fixed, abs(a - b))

        if all(x == -1 for x in nums):
            return 0

        lo, hi = max_fixed, (mx - mn + 1) // 2
        while lo < hi:
            mid = (lo + hi) // 2
            if self._check(nums, mid, mn + mid, mx - mid):
                hi = mid
            else:
                lo = mid + 1
        return lo

    def _check(self, nums: List[int], m: int, x: int, y: int) -> bool:
        gap = 0
        prev = 0
        for num in nums:
            if num == -1:
                gap += 1
                continue
            if prev > 0 and gap > 0:
                if gap == 1 and not self._single(prev, num, m, x, y):
                    return False
                if gap > 1 and not self._multi(prev, num, m, x, y):
                    return False
            prev = num
            gap = 0
        if nums[0] == -1:
            first = next((v for v in nums if v != -1), -1)
            if first != -1 and not self._boundary(first, m, x, y):
                return False
        if nums[-1] == -1:
            last = next((v for v in reversed(nums) if v != -1), -1)
            if last != -1 and not self._boundary(last, m, x, y):
                return False
        return True

    def _single(self, a: int, b: int, m: int, x: int, y: int) -> bool:
        return min(max(abs(a - x), abs(b - x)), max(abs(a - y), abs(b - y))) <= m

    def _multi(self, a: int, b: int, m: int, x: int, y: int) -> bool:
        ax, ay, bx, by, xy = abs(a - x), abs(a - y), abs(b - x), abs(b - y), abs(x - y)
        return min(max(ax, bx), max(ay, by), max(ax, xy, by), max(ay, xy, bx)) <= m

    def _boundary(self, a: int, m: int, x: int, y: int) -> bool:
        return min(abs(a - x), abs(a - y)) <= m
# @lc code=end
