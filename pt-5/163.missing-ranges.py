#
# @lc app=leetcode id=163 lang=python3
#
# [163] Missing Ranges
#
# https://leetcode.com/problems/missing-ranges/description/
#
# algorithms
# Easy (35.68%)
# Likes:    1192
# Dislikes: 3026
# Total Accepted:    312.9K
# Total Submissions: 876.9K
# Testcase Example:  "[0,1,3,50,75]\n0\n99"
#
#
# You are given an inclusive range [lower, upper] and a sorted unique
# integer array nums, where all elements are within the inclusive range.
#
# A number x is considered missing if x is in the range [lower, upper] and
# x is not in nums.
#
# Return the shortest sorted list of ranges that exactly covers all the
# missing numbers. That is, no element of nums is included in any of the
# ranges, and each missing number is covered by one of the ranges.
#
# Example 1:
#
# Input: nums = [0,1,3,50,75], lower = 0, upper = 99
# Output: [[2,2],[4,49],[51,74],[76,99]]
# Explanation: The ranges are:
# [2,2]
# [4,49]
# [51,74]
# [76,99]
#
# Example 2:
#
# Input: nums = [-1], lower = -1, upper = -1
# Output: []
# Explanation: There are no missing ranges since there are no missing
# numbers.
#
# Constraints:
#
# -10^9 <= lower <= upper <= 10^9
#
# 0 <= nums.length <= 100
#
# lower <= nums[i] <= upper
#
# All the values of nums are unique.
#
# @lc code=start
from typing import List


class Solution:
    def findMissingRanges(
        self, nums: List[int], lower: int, upper: int
    ) -> List[List[int]]:
        """
        Interview explanation:
        Walk the sorted unique nums as known covered points and emit inclusive
        gaps between consecutive covered values (also before the first and after
        the last), clipped to [lower, upper].

        Algorithm:
        - prev = lower - 1.
        - For each num in nums + [upper + 1]: if num - prev >= 2, append
          [prev + 1, num - 1]; then prev = num.
        - Return the list of inclusive missing ranges.

        Complexity: O(n) time, O(1) extra space besides output.
        """
        ranges: List[List[int]] = []
        prev = lower - 1
        for num in nums + [upper + 1]:
            if num - prev >= 2:
                ranges.append([prev + 1, num - 1])
            prev = num
        return ranges
# @lc code=end
