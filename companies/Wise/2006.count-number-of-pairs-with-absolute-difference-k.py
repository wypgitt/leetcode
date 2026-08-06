#
# @lc app=leetcode id=2006 lang=python3
#
# [2006] Count Number of Pairs With Absolute Difference K
#
# https://leetcode.com/problems/count-number-of-pairs-with-absolute-difference-k/description/
#
# algorithms
# Easy (85.41%)
# Likes:    1820
# Dislikes: 50
# Total Accepted:    246.3K
# Total Submissions: 288.4K
# Testcase Example:  "[1,2,2,1]\n1"
#
# Given an integer array nums and an integer k, return the number of pairs (i,
# j) where i < j such that |nums[i] - nums[j]| == k.
#
# The value of |x| is defined as:
#
#
# x if x >= 0.
#
#
# -x if x < 0.
#
#
#
# Example 1:
#
# Input: nums = [1,2,2,1], k = 1
# Output: 4
# Explanation: The pairs with an absolute difference of 1 are:
# - [1,2,2,1]
# - [1,2,2,1]
# - [1,2,2,1]
# - [1,2,2,1]
#
# Example 2:
#
# Input: nums = [1,3], k = 3
# Output: 0
# Explanation: There are no pairs with an absolute difference of 3.
#
# Example 3:
#
# Input: nums = [3,2,1,5,4], k = 2
# Output: 3
# Explanation: The pairs with an absolute difference of 2 are:
# - [3,2,1,5,4]
# - [3,2,1,5,4]
# - [3,2,1,5,4]
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 200
#
#
# 1 <= nums[i] <= 100
#
#
# 1 <= k <= 99
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def countKDifference(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count unordered pairs (i,j) with |nums[i]-nums[j]| == k.

        Algorithm:
        - One pass with Counter: for each x, add freq[x-k] + freq[x+k], then
          increment freq[x].

        Complexity: O(n) time, O(n) space.
        """
        freq = Counter()
        ans = 0
        for x in nums:
            ans += freq[x - k] + freq[x + k]
            freq[x] += 1
        return ans


# @lc code=end
