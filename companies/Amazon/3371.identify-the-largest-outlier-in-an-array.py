#
# @lc app=leetcode id=3371 lang=python3
#
# [3371] Identify the Largest Outlier in an Array
#
# https://leetcode.com/problems/identify-the-largest-outlier-in-an-array/description/
#
# algorithms
# Medium (36.46%)
# Likes:    229
# Dislikes: 30
# Total Accepted:    53.8K
# Total Submissions: 147.5K
# Testcase Example:  "[2,3,5,10]"
#
#
# You are given an integer array nums. This array contains n elements,
# where exactly n - 2 elements are special numbers. One of the remaining
# two elements is the sum of these special numbers, and the other is an
# outlier.
#
# An outlier is defined as a number that is neither one of the original
# special numbers nor the element representing the sum of those numbers.
#
# Note that special numbers, the sum element, and the outlier must have
# distinct indices, but may share the same value.
#
# Return the largest potential outlier in nums.
#
# Example 1:
#
# Input: nums = [2,3,5,10]
#
# Output: 10
#
# Explanation:
#
# The special numbers could be 2 and 3, thus making their sum 5 and the
# outlier 10.
#
# Example 2:
#
# Input: nums = [-2,-1,-3,-6,4]
#
# Output: 4
#
# Explanation:
#
# The special numbers could be -2, -1, and -3, thus making their sum -6
# and the outlier 4.
#
# Example 3:
#
# Input: nums = [1,1,1,1,1,5,5]
#
# Output: 5
#
# Explanation:
#
# The special numbers could be 1, 1, 1, 1, and 1, thus making their sum 5
# and the other 5 as the outlier.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# -1000 <= nums[i] <= 1000
#
# The input is generated such that at least one potential outlier exists
# in nums.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def getLargestOutlier(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Exactly n-2 specials, one sum-of-specials, one outlier.
        If outlier is x and sum element is y, then total - x = 2y.

        Algorithm:
        - For each candidate outlier x, check y = (S - x) / 2 exists at another index.
        - Take the maximum valid x.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter(nums)
        S = sum(nums)
        ans = -(10**18)
        for x in cnt:
            if (S - x) % 2:
                continue
            y = (S - x) // 2
            if y in cnt and (y != x or cnt[x] >= 2):
                ans = max(ans, x)
        return ans
# @lc code=end
