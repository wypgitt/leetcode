#
# @lc app=leetcode id=2419 lang=python3
#
# [2419] Longest Subarray With Maximum Bitwise AND
#
# https://leetcode.com/problems/longest-subarray-with-maximum-bitwise-and/description/
#
# algorithms
# Medium (65.35%)
# Likes:    1323
# Dislikes: 111
# Total Accepted:    255.3K
# Total Submissions: 390.6K
# Testcase Example:  "[1,2,3,3,2,2]"
#
# You are given an integer array nums of size n.
#
# Consider a non-empty subarray from nums that has the maximum possible bitwise
# AND.
#
#
# In other words, let k be the maximum value of the bitwise AND of any subarray
# of nums. Then, only subarrays with a bitwise AND equal to k should be
# considered.
#
# Return the length of the longest such subarray.
#
# The bitwise AND of an array is the bitwise AND of all the numbers in it.
#
# A subarray is a contiguous sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [1,2,3,3,2,2]
# Output: 2
# Explanation:
# The maximum possible bitwise AND of a subarray is 3.
# The longest subarray with that value is [3,3], so we return 2.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: 1
# Explanation:
# The maximum possible bitwise AND of a subarray is 4.
# The longest subarray with that value is [4], so we return 1.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def longestSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Bitwise AND of a subarray is maximized by the global max element; longest
        subarray with that AND is the longest run of the max value.

        Algorithm:
        - Find M = max(nums); scan longest consecutive streak of M.

        Complexity: O(n) time, O(1) space.
        """
        m = max(nums)
        ans = cur = 0
        for x in nums:
            if x == m:
                cur += 1
                ans = max(ans, cur)
            else:
                cur = 0
        return ans
# @lc code=end
