#
# @lc app=leetcode id=3046 lang=python3
#
# [3046] Split the Array
#
# https://leetcode.com/problems/split-the-array/description/
#
# algorithms
# Easy (61.78%)
# Likes:    181
# Dislikes: 16
# Total Accepted:    88.1K
# Total Submissions: 142.6K
# Testcase Example:  "[1,1,2,2,3,4]"
#
#
# You are given an integer array nums of even length. You have to split
# the array into two parts nums1 and nums2 such that:
#
# nums1.length == nums2.length == nums.length / 2.
#
# nums1 should contain distinct elements.
#
# nums2 should also contain distinct elements.
#
# Return true if it is possible to split the array, and false otherwise.
#
# Example 1:
#
# Input: nums = [1,1,2,2,3,4]
# Output: true
# Explanation: One of the possible ways to split nums is nums1 = [1,2,3]
# and nums2 = [1,2,4].
#
# Example 2:
#
# Input: nums = [1,1,1,1]
# Output: false
# Explanation: The only possible way to split nums is nums1 = [1,1] and
# nums2 = [1,1]. Both nums1 and nums2 do not contain distinct elements.
# Therefore, we return false.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# nums.length % 2 == 0
#
# 1 <= nums[i] <= 100
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def isPossibleToSplit(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Split into two equal-length halves, each with distinct elements. A value
        appearing 3+ times cannot fit (each half may take it at most once).

        Algorithm:
        - Return whether every frequency is <= 2.

        Complexity: O(n) time, O(n) space.
        """
        return max(Counter(nums).values()) <= 2

    def isPossibleToSplit_array(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Values are in [1,100]; fixed-size frequency table.

        Algorithm:
        - Count in size-101 array; reject if any count > 2.

        Complexity: O(n) time, O(1) space.
        """
        freq = [0] * 101
        for x in nums:
            freq[x] += 1
            if freq[x] > 2:
                return False
        return True
# @lc code=end

