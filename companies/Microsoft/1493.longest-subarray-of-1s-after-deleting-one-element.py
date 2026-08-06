#
# @lc app=leetcode id=1493 lang=python3
#
# [1493] Longest Subarray of 1's After Deleting One Element
#
# https://leetcode.com/problems/longest-subarray-of-1s-after-deleting-one-element/description/
#
# algorithms
# Medium (71.43%)
# Likes:    4877
# Dislikes: 112
# Total Accepted:    677K
# Total Submissions: 948K
# Testcase Example:  "[1,1,0,1]"
#
# Given a binary array nums, you should delete one element from it.
#
# Return the size of the longest non-empty subarray containing only 1's in the
# resulting array. Return 0 if there is no such subarray.
#
# Example 1:
#
# Input: nums = [1,1,0,1]
# Output: 3
# Explanation: After deleting the number in position 2, [1,1,1] contains 3
# numbers with value of 1's.
#
# Example 2:
#
# Input: nums = [0,1,1,1,0,1,1,0,1]
# Output: 5
# Explanation: After deleting the number in position 4, [0,1,1,1,1,1,0,1]
# longest subarray with value of 1's is [1,1,1,1,1].
#
# Example 3:
#
# Input: nums = [1,1,1]
# Output: 2
# Explanation: You must delete one element.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# nums[i] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def longestSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Longest subarray of 1s after deleting exactly one element — sliding
        window with at most one 0 inside; answer is window length - 1.

        Algorithm:
        - Expand right; while zeros>1 shrink left; track max (right-left+1)-1.

        Complexity: O(n) time, O(1) space.
        """
        left = zeros = best = 0
        for right, x in enumerate(nums):
            zeros += x == 0
            while zeros > 1:
                zeros -= nums[left] == 0
                left += 1
            best = max(best, right - left)  # delete one
        return best

    def longestSubarray_groups(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: for each zero, sum lengths of 1-runs on both sides; also
        handle all-ones (must delete one → n-1).

        Algorithm:
        - Scan runs; at each 0, left_run+right_run; max.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        if all(nums):
            return n - 1
        best = prev = cur = 0
        for x in nums:
            if x == 1:
                cur += 1
            else:
                best = max(best, prev + cur)
                prev, cur = cur, 0
        best = max(best, prev + cur)
        return best
# @lc code=end
