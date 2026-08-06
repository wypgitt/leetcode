#
# @lc app=leetcode id=3745 lang=python3
#
# [3745] Maximize Expression of Three Elements
#
# https://leetcode.com/problems/maximize-expression-of-three-elements/description/
#
# algorithms
# Easy (73.04%)
# Likes:    53
# Dislikes: 1
# Total Accepted:    49.2K
# Total Submissions: 67.4K
# Testcase Example:  "[1,4,2,5]"
#
#
# You are given an integer array nums.
#
# Choose three elements a, b, and c from nums at distinct indices such
# that the value of the expression a + b - c is maximized.
#
# Return an integer denoting the maximum possible value of this
# expression.
#
# Example 1:
#
# Input: nums = [1,4,2,5]
#
# Output: 8
#
# Explanation:
#
# We can choose a = 4, b = 5, and c = 1. The expression value is 4 + 5 - 1
# = 8, which is the maximum possible.
#
# Example 2:
#
# Input: nums = [-2,0,5,-2,4]
#
# Output: 11
#
# Explanation:
#
# We can choose a = 5, b = 4, and c = -2. The expression value is 5 + 4 -
# (-2) = 11, which is the maximum possible.
#
# Constraints:
#
# 3 <= nums.length <= 100
#
# -100 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def maximizeExpressionOfThree(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Maximize a + b - c over distinct indices = two largest values minus the
        smallest value.

        Algorithm:
        - Sort; return nums[-1] + nums[-2] - nums[0].

        Complexity: O(n log n) time, O(1) extra space.
        """
        nums = sorted(nums)
        return nums[-1] + nums[-2] - nums[0]

    def maximizeExpressionOfThree_scan(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: one pass for the minimum and two maxima.

        Algorithm:
        - Track min and two largest; return max1 + max2 - min.

        Complexity: O(n) time, O(1) space.
        """
        import heapq

        return sum(heapq.nlargest(2, nums)) - min(nums)
# @lc code=end
