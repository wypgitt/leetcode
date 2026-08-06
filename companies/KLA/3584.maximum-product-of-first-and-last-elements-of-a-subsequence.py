#
# @lc app=leetcode id=3584 lang=python3
#
# [3584] Maximum Product of First and Last Elements of a Subsequence
#
# https://leetcode.com/problems/maximum-product-of-first-and-last-elements-of-a-subsequence/description/
#
# algorithms
# Medium (31.87%)
# Likes:    122
# Dislikes: 1
# Total Accepted:    21K
# Total Submissions: 65.9K
# Testcase Example:  "[-1,-9,2,3,-2,-3,1]\n1"
#
#
# You are given an integer array nums and an integer m.
#
# Return the maximum product of the first and last elements of any
# subsequence of nums of size m.
#
# Example 1:
#
# Input: nums = [-1,-9,2,3,-2,-3,1], m = 1
#
# Output: 81
#
# Explanation:
#
# The subsequence [-9] has the largest product of the first and last
# elements: -9 * -9 = 81. Therefore, the answer is 81.
#
# Example 2:
#
# Input: nums = [1,3,-5,5,6,-4], m = 3
#
# Output: 20
#
# Explanation:
#
# The subsequence [-5, 6, -4] has the largest product of the first and
# last elements.
#
# Example 3:
#
# Input: nums = [2,-1,2,-6,5,2,-5,7], m = 2
#
# Output: 35
#
# Explanation:
#
# The subsequence [5, 7] has the largest product of the first and last
# elements.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#
# 1 <= m <= nums.length
#

# @lc code=start

from math import inf
from typing import List


class Solution:
    def maximumProduct(self, nums: List[int], m: int) -> int:
        """
        Interview explanation:
        For a size-m subsequence ending at i, the first element lies in
        nums[0..i-m+1]. Maximize last * first over min/max of that prefix.

        Algorithm:
        - Sweep i from m-1..n-1; fold nums[i-m+1] into prefix min/max.
        - Track max of nums[i]*mi and nums[i]*mx.

        Complexity: O(n) time, O(1) space.
        """
        ans = -inf
        mi, mx = inf, -inf
        for i in range(m - 1, len(nums)):
            y = nums[i - m + 1]
            mi = min(mi, y)
            mx = max(mx, y)
            x = nums[i]
            ans = max(ans, x * mi, x * mx)
        return int(ans)
# @lc code=end
