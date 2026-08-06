#
# @lc app=leetcode id=1848 lang=python3
#
# [1848] Minimum Distance to the Target Element
#
# https://leetcode.com/problems/minimum-distance-to-the-target-element/description/
#
# algorithms
# Easy (64.35%)
# Likes:    633
# Dislikes: 86
# Total Accepted:    180K
# Total Submissions: 279K
# Testcase Example:  "[1,2,3,4,5]"
#
# Given an integer array nums (0-indexed) and two integers target and start,
# find an index i such that nums[i] == target and abs(i - start) is minimized.
# Note that abs(x) is the absolute value of x.
#
# Return abs(i - start).
#
# It is guaranteed that target exists in nums.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5], target = 5, start = 3
# Output: 1
# Explanation: nums[4] = 5 is the only value equal to target, so the answer is
# abs(4 - 3) = 1.
#
# Example 2:
#
# Input: nums = [1], target = 1, start = 0
# Output: 0
# Explanation: nums[0] = 1 is the only value equal to target, so the answer is
# abs(0 - 0) = 0.
#
# Example 3:
#
# Input: nums = [1,1,1,1,1,1,1,1,1,1], target = 1, start = 0
# Output: 0
# Explanation: Every value of nums is 1, but nums[0] minimizes abs(i - start),
# which is abs(0 - 0) = 0.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^4
#
# 0 <= start < nums.length
#
# target is in nums.
#

# @lc code=start
from typing import List


class Solution:
    def getMinDistance(self, nums: List[int], target: int, start: int) -> int:
        """
        Interview explanation:
        Min |i-start| over i with nums[i]==target (guaranteed exists).

        Algorithm (linear scan):
        - Track min abs distance among matching indices.

        Complexity: O(n) time, O(1) space.
        """
        ans = len(nums)
        for i, x in enumerate(nums):
            if x == target:
                ans = min(ans, abs(i - start))
        return ans

    def getMinDistance_expand(self, nums: List[int], target: int, start: int) -> int:
        """
        Interview explanation:
        Alternate: expand outward from start until hitting target.

        Algorithm (two pointers expand):
        - For d=0..n check start±d.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        for d in range(n):
            for i in (start - d, start + d):
                if 0 <= i < n and nums[i] == target:
                    return d
        return 0
# @lc code=end
