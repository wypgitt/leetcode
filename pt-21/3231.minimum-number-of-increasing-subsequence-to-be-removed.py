#
# @lc app=leetcode id=3231 lang=python3
#
# [3231] Minimum Number of Increasing Subsequence to Be Removed
#
# https://leetcode.com/problems/minimum-number-of-increasing-subsequence-to-be-removed/description/
#
# algorithms
# Hard (47.38%)
# Likes:    8
# Dislikes: 1
# Total Accepted:    652
# Total Submissions: 1.4K
# Testcase Example:  "[5,3,1,4,2]"
#
#
# Given an array of integers nums, you are allowed to perform the
# following operation any number of times:
#
# Remove a strictly increasing subsequence from the array.
#
# Your task is to find the minimum number of operations required to make
# the array empty.
#
# Example 1:
#
# Input: nums = [5,3,1,4,2]
#
# Output: 3
#
# Explanation:
#
# We remove subsequences [1, 2], [3, 4], [5].
#
# Example 2:
#
# Input: nums = [1,2,3,4,5]
#
# Output: 1
#
# Example 3:
#
# Input: nums = [5,4,3,2,1]
#
# Output: 5
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from bisect import bisect_right
from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Each op removes one strictly increasing subsequence. By Dilworth, the
        minimum cover size equals the length of the longest non-increasing
        subsequence.

        Algorithm:
        - Patience sorting / LIS on negated values with non-strict insertion
          (bisect_right): length of longest non-increasing subsequence.

        Complexity: O(n log n) time, O(n) space.
        Alternate: DP O(n^2) longest non-increasing ending at each index.
        """
        piles: List[int] = []
        for x in nums:
            y = -x
            i = bisect_right(piles, y)
            if i == len(piles):
                piles.append(y)
            else:
                piles[i] = y
        return len(piles)

# @lc code=end
