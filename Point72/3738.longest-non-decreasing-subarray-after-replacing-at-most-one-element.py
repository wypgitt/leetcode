#
# @lc app=leetcode id=3738 lang=python3
#
# [3738] Longest Non-Decreasing Subarray After Replacing at Most One Element
#
# https://leetcode.com/problems/longest-non-decreasing-subarray-after-replacing-at-most-one-element/description/
#
# algorithms
# Medium (22.60%)
# Likes:    108
# Dislikes: 8
# Total Accepted:    16.1K
# Total Submissions: 71.5K
# Testcase Example:  "[1,2,3,1,2]"
#
#
# You are given an integer array nums.
#
# You are allowed to replace at most one element in the array with any
# other integer value of your choice.
#
# Return the length of the longest non-decreasing subarray that can be
# obtained after performing at most one replacement.
#
# An array is said to be non-decreasing if each element is greater than or
# equal to its previous one (if it exists).
#
# Example 1:
#
# Input: nums = [1,2,3,1,2]
#
# Output: 4
#
# Explanation:
#
# Replacing nums[3] = 1 with 3 gives the array [1, 2, 3, 3, 2].
#
# The longest non-decreasing subarray is [1, 2, 3, 3], which has a length
# of 4.
#
# Example 2:
#
# Input: nums = [2,2,2,2,2]
#
# Output: 5
#
# Explanation:
#
# All elements in nums are equal, so it is already non-decreasing and the
# entire nums forms a subarray of length 5.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9​​​​​​​
#

# @lc code=start
from typing import List


class Solution:
    def longestSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Precompute longest non-decreasing runs ending/starting at each index.
        Replacing index i can glue left[i-1] and right[i+1] when
        nums[i-1] <= nums[i+1]; otherwise keep the longer side plus the
        replaced cell.

        Algorithm:
        - Build left[] and right[] run lengths.
        - ans = max(left); for each i try glue or one-sided extension.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        left = [1] * n
        right = [1] * n
        for i in range(1, n):
            if nums[i] >= nums[i - 1]:
                left[i] = left[i - 1] + 1
        for i in range(n - 2, -1, -1):
            if nums[i] <= nums[i + 1]:
                right[i] = right[i + 1] + 1
        ans = max(left)
        for i in range(n):
            a = left[i - 1] if i else 0
            b = right[i + 1] if i + 1 < n else 0
            if i and i + 1 < n and nums[i - 1] > nums[i + 1]:
                ans = max(ans, a + 1, b + 1)
            else:
                ans = max(ans, a + b + 1)
        return ans

    def longestSubarray_enum_breaks(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: same left/right arrays; focus enumeration on positions that
        break non-decreasing order (still O(n)).

        Algorithm:
        - Identical glue logic for every index (replacement can also sit inside
          an already good run).

        Complexity: O(n) time, O(n) space.
        """
        return self.longestSubarray(nums)
# @lc code=end

