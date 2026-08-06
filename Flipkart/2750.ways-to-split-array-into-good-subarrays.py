#
# @lc app=leetcode id=2750 lang=python3
#
# [2750] Ways to Split Array Into Good Subarrays
#
# https://leetcode.com/problems/ways-to-split-array-into-good-subarrays/description/
#
# algorithms
# Medium (35.13%)
# Likes:    481
# Dislikes: 14
# Total Accepted:    29K
# Total Submissions: 82.7K
# Testcase Example:  "[0,1,0,0,1]"
#
# You are given a binary array nums.
#
# A subarray of an array is good if it contains exactly one element with the
# value 1.
#
# Return an integer denoting the number of ways to split the array nums into
# good subarrays. As the number may be too large, return it modulo 10^9 + 7.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [0,1,0,0,1]
# Output: 3
# Explanation: There are 3 ways to split nums into good subarrays:
# - [0,1] [0,0,1]
# - [0,1,0] [0,1]
# - [0,1,0,0] [1]
#
# Example 2:
#
# Input: nums = [0,1,0]
# Output: 1
# Explanation: There is 1 way to split nums into good subarrays:
# - [0,1,0]
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 0 <= nums[i] <= 1
#

# @lc code=start
from typing import List


class Solution:
    def numberOfGoodSubarraySplits(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Split binary array into contiguous good subarrays each containing exactly one 1.

        Algorithm:
        - Record positions of 1s; if none return 0; answer is product of gaps between
          consecutive 1s (gap = pos[i]-pos[i-1]).

        Complexity: O(n) time, O(n) space (or O(1) streaming).
        """
        mod = 10**9 + 7
        ones = [i for i, v in enumerate(nums) if v == 1]
        if not ones:
            return 0
        ans = 1
        for i in range(1, len(ones)):
            ans = ans * (ones[i] - ones[i - 1]) % mod
        return ans
# @lc code=end
