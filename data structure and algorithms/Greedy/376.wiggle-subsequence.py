#
# @lc app=leetcode id=376 lang=python3
#
# [376] Wiggle Subsequence
#
# https://leetcode.com/problems/wiggle-subsequence/description/
#
# algorithms
# Medium (49.65%)
# Likes:    5340
# Dislikes: 169
# Total Accepted:    301K
# Total Submissions: 607K
# Testcase Example:  "[1,7,4,9,2,5]"
#
# A wiggle sequence is a sequence where the differences between successive
# numbers strictly alternate between positive and negative. The first
# difference (if one exists) may be either positive or negative. A sequence
# with one element and a sequence with two non-equal elements are trivially
# wiggle sequences.
#
# For example, [1, 7, 4, 9, 2, 5] is a wiggle sequence because the differences
# (6, -3, 5, -7, 3) alternate between positive and negative.
#
# In contrast, [1, 4, 7, 2, 5] and [1, 7, 4, 5, 5] are not wiggle sequences.
# The first is not because its first two differences are positive, and the
# second is not because its last difference is zero.
#
# A subsequence is obtained by deleting some elements (possibly zero) from the
# original sequence, leaving the remaining elements in their original order.
#
# Given an integer array nums, return the length of the longest wiggle
# subsequence of nums.
#
# Example 1:
#
# Input: nums = [1,7,4,9,2,5]
# Output: 6
# Explanation: The entire sequence is a wiggle sequence with differences (6,
# -3, 5, -7, 3).
#
# Example 2:
#
# Input: nums = [1,17,5,10,13,15,10,5,16,8]
# Output: 7
# Explanation: There are several subsequences that achieve this length.
# One is [1, 17, 10, 13, 10, 16, 8] with differences (16, -7, 3, -3, 6, -8).
#
# Example 3:
#
# Input: nums = [1,2,3,4,5,6,7,8,9]
# Output: 2
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 0 <= nums[i] <= 1000
#
# Follow up: Could you solve this in O(n) time?
#

# @lc code=start
from typing import List


class Solution:
    def wiggleMaxLength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A wiggle alternates up/down differences. Greedy: keep only peaks and
        valleys — whenever the difference direction flips (or starts), count
        a new element. Plateaus (diff 0) are skipped.

        Algorithm:
        - If len <= 1 return len.
        - Track prev_diff; for each consecutive pair, if diff != 0 and
          (prev_diff == 0 or sign flips), length++ and update prev_diff.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        if n < 2:
            return n
        length = 1
        prev_diff = 0
        for i in range(1, n):
            diff = nums[i] - nums[i - 1]
            if diff != 0 and (prev_diff == 0 or (diff > 0) != (prev_diff > 0)):
                length += 1
                prev_diff = diff
        return length

    def wiggleMaxLengthDP(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate DP: up[i]/down[i] = longest wiggle ending at i with last
        difference up/down. up = down+1 when nums[i] > nums[i-1], etc.

        Complexity: O(n) time, O(1) space with rolling vars.
        """
        if not nums:
            return 0
        up = down = 1
        for i in range(1, len(nums)):
            if nums[i] > nums[i - 1]:
                up = down + 1
            elif nums[i] < nums[i - 1]:
                down = up + 1
        return max(up, down)
# @lc code=end
