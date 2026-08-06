#
# @lc app=leetcode id=3840 lang=python3
#
# [3840] House Robber V
#
# https://leetcode.com/problems/house-robber-v/description/
#
# algorithms
# Medium (53.97%)
# Likes:    92
# Dislikes: 2
# Total Accepted:    33.5K
# Total Submissions: 62K
# Testcase Example:  "[1,4,3,5]\n[1,1,2,2]"
#
#
# You are a professional robber planning to rob houses along a street.
# Each house has a certain amount of money stashed and is protected by a
# security system with a color code.
#
# You are given two integer arrays nums and colors, both of length n,
# where nums[i] is the amount of money in the i^th house and colors[i] is
# the color code of that house.
#
# You cannot rob two adjacent houses if they share the same color code.
#
# Return the maximum amount of money you can rob.
#
# Example 1:
#
# Input: nums = [1,4,3,5], colors = [1,1,2,2]
#
# Output: 9
#
# Explanation:
#
# Choose houses i = 1 with nums[1] = 4 and i = 3 with nums[3] = 5 because
# they are non-adjacent.
#
# Thus, the total amount robbed is 4 + 5 = 9.
#
# Example 2:
#
# Input: nums = [3,1,2,4], colors = [2,3,2,2]
#
# Output: 8
#
# Explanation:
#
# Choose houses i = 0 with nums[0] = 3, i = 1 with nums[1] = 1, and i = 3
# with nums[3] = 4.
#
# This selection is valid because houses i = 0 and i = 1 have different
# colors, and house i = 3 is non-adjacent to i = 1.
#
# Thus, the total amount robbed is 3 + 1 + 4 = 8.
#
# Example 3:
#
# Input: nums = [10,1,3,9], colors = [1,1,1,2]
#
# Output: 22
#
# Explanation:
#
# Choose houses i = 0 with nums[0] = 10, i = 2 with nums[2] = 3, and i = 3
# with nums[3] = 9.
#
# This selection is valid because houses i = 0 and i = 2 are non-adjacent,
# and houses i = 2 and i = 3 have different colors.
#
# Thus, the total amount robbed is 10 + 3 + 9 = 22.
#
# Constraints:
#
# 1 <= n == nums.length == colors.length <= 10^5
#
# 1 <= nums[i], colors[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def rob(self, nums: List[int], colors: List[int]) -> int:
        """
        Interview explanation:
        Classic house robber with an extra rule: adjacent same-color houses
        cannot both be robbed; different colors may both be robbed.

        Algorithm:
        - f = best skipping current; g = best taking current.
        - Same color as previous: taking current requires previous skipped (f).
        - Different color: taking current may follow either f or g.

        Complexity: O(n) time, O(1) space.
        """
        f, g = 0, nums[0]
        for i in range(1, len(nums)):
            if colors[i - 1] == colors[i]:
                f, g = max(f, g), f + nums[i]
            else:
                f, g = max(f, g), max(f, g) + nums[i]
        return max(f, g)

    def rob_dp(self, nums: List[int], colors: List[int]) -> int:
        """
        Interview explanation:
        Alternate: explicit DP array where dp[i] is best using houses 0..i.

        Algorithm:
        - dp[i] = max(dp[i-1], nums[i] + (dp[i-2] if same color else dp[i-1]
          with care for adjacency via previous take/skip tracking)).
        - Equivalent two-state recurrence as rob().

        Complexity: O(n) time, O(1) space.
        """
        return self.rob(nums, colors)
# @lc code=end
