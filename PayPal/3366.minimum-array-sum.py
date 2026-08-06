#
# @lc app=leetcode id=3366 lang=python3
#
# [3366] Minimum Array Sum
#
# https://leetcode.com/problems/minimum-array-sum/description/
#
# algorithms
# Medium (31.95%)
# Likes:    178
# Dislikes: 17
# Total Accepted:    17.9K
# Total Submissions: 55.9K
# Testcase Example:  "[2,8,3,19,3]\n3\n1\n1"
#
#
# You are given an integer array nums and three integers k, op1, and op2.
#
# You can perform the following operations on nums:
#
# Operation 1: Choose an index i and divide nums[i] by 2, rounding up to
# the nearest whole number. You can perform this operation at most op1
# times, and not more than once per index.
#
# Operation 2: Choose an index i and subtract k from nums[i], but only if
# nums[i] is greater than or equal to k. You can perform this operation at
# most op2 times, and not more than once per index.
#
# Note: Both operations can be applied to the same index, but at most once
# each.
#
# Return the minimum possible sum of all elements in nums after performing
# any number of operations.
#
# Example 1:
#
# Input: nums = [2,8,3,19,3], k = 3, op1 = 1, op2 = 1
#
# Output: 23
#
# Explanation:
#
# Apply Operation 2 to nums[1] = 8, making nums[1] = 5.
#
# Apply Operation 1 to nums[3] = 19, making nums[3] = 10.
#
# The resulting array becomes [2, 5, 3, 10, 3], which has the minimum
# possible sum of 23 after applying the operations.
#
# Example 2:
#
# Input: nums = [2,4,3], k = 3, op1 = 2, op2 = 1
#
# Output: 3
#
# Explanation:
#
# Apply Operation 1 to nums[0] = 2, making nums[0] = 1.
#
# Apply Operation 1 to nums[1] = 4, making nums[1] = 2.
#
# Apply Operation 2 to nums[2] = 3, making nums[2] = 0.
#
# The resulting array becomes [1, 2, 0], which has the minimum possible
# sum of 3 after applying the operations.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 0 <= nums[i] <= 10^5
#
# 0 <= k <= 10^5
#
# 0 <= op1, op2 <= nums.length
#

# @lc code=start
from typing import List


class Solution:
    def minArraySum(self, nums: List[int], k: int, op1: int, op2: int) -> int:
        """
        Interview explanation:
        Each index may take ceil(/2) at most once and subtract-k at most once;
        order of both ops matters. DP over used op1/op2 counts.

        Algorithm:
        - f[i][j][p] = min sum using first i nums with j op1 and p op2.
        - Transitions: none / only op1 / only op2 / both orders.

        Complexity: O(n * op1 * op2) time and space.
        """
        n = len(nums)
        inf = 10**18
        f = [[[inf] * (op2 + 1) for _ in range(op1 + 1)] for _ in range(n + 1)]
        f[0][0][0] = 0
        for i, x in enumerate(nums, 1):
            for j in range(op1 + 1):
                for p in range(op2 + 1):
                    f[i][j][p] = f[i - 1][j][p] + x
                    if j > 0:
                        f[i][j][p] = min(f[i][j][p], f[i - 1][j - 1][p] + (x + 1) // 2)
                    if p > 0 and x >= k:
                        f[i][j][p] = min(f[i][j][p], f[i - 1][j][p - 1] + (x - k))
                    if j > 0 and p > 0:
                        y = (x + 1) // 2
                        if y >= k:
                            f[i][j][p] = min(f[i][j][p], f[i - 1][j - 1][p - 1] + y - k)
                        if x >= k:
                            f[i][j][p] = min(
                                f[i][j][p], f[i - 1][j - 1][p - 1] + (x - k + 1) // 2
                            )
        ans = inf
        for j in range(op1 + 1):
            for p in range(op2 + 1):
                ans = min(ans, f[n][j][p])
        return ans
# @lc code=end
