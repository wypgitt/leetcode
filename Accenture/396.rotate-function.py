#
# @lc app=leetcode id=396 lang=python3
#
# [396] Rotate Function
#
# https://leetcode.com/problems/rotate-function/description/
#
# algorithms
# Medium (53.99%)
# Likes:    1969
# Dislikes: 290
# Total Accepted:    196.3K
# Total Submissions: 363.5K
# Testcase Example:  '[4,3,2,6]'
#
# You are given an integer array nums of length n.
# 
# Assume arrk to be an array obtained by rotating nums by k positions
# clock-wise. We define the rotation function F on nums as follow:
# 
# 
# F(k) = 0 * arrk[0] + 1 * arrk[1] + ... + (n - 1) * arrk[n - 1].
# 
# 
# Return the maximum value of F(0), F(1), ..., F(n-1).
# 
# The test cases are generated so that the answer fits in a 32-bit integer.
# 
# 
# Example 1:
# 
# 
# Input: nums = [4,3,2,6]
# Output: 26
# Explanation:
# F(0) = (0 * 4) + (1 * 3) + (2 * 2) + (3 * 6) = 0 + 3 + 4 + 18 = 25
# F(1) = (0 * 6) + (1 * 4) + (2 * 3) + (3 * 2) = 0 + 4 + 6 + 6 = 16
# F(2) = (0 * 2) + (1 * 6) + (2 * 4) + (3 * 3) = 0 + 6 + 8 + 9 = 23
# F(3) = (0 * 3) + (1 * 2) + (2 * 6) + (3 * 4) = 0 + 2 + 12 + 12 = 26
# So the maximum value of F(0), F(1), F(2), F(3) is F(3) = 26.
# 
# 
# Example 2:
# 
# 
# Input: nums = [100]
# Output: 0
# 
# 
# 
# Constraints:
# 
# 
# n == nums.length
# 1 <= n <= 10^5
# -100 <= nums[i] <= 100
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def maxRotateFunction(self, nums: List[int]) -> int:
        total = sum(nums)
        n = len(nums)
        cur = sum(i * x for i, x in enumerate(nums))
        best = cur
        for k in range(1, n):
            cur = cur + total - n * nums[-k]
            best = max(best, cur)
        return best
# @lc code=end

"""
Interview explanation:
Compute F(0) directly, then update rotations in O(1). When rotating right by one, every existing element's index increases by 1, contributing +sum(nums), except the element moved from the end to index 0 loses n * value. Therefore F(k) = F(k-1) + total - n * nums[n-k].

Data structure: plain scalar accumulators are enough; no rotated arrays are built.

Edge cases: length 1 naturally returns 0. Negative values still work because the recurrence is algebraic.

Complexity: O(n) time for one pass and O(1) extra space.
"""
