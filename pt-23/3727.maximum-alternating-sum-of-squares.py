#
# @lc app=leetcode id=3727 lang=python3
#
# [3727] Maximum Alternating Sum of Squares
#
# https://leetcode.com/problems/maximum-alternating-sum-of-squares/description/
#
# algorithms
# Medium (61.80%)
# Likes:    73
# Dislikes: 1
# Total Accepted:    35K
# Total Submissions: 56.7K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums. You may rearrange the elements in
# any order.
#
# The alternating score of an array arr is defined as:
#
# score = arr[0]^2 - arr[1]^2 + arr[2]^2 - arr[3]^2 + ...
#
# Return an integer denoting the maximum possible alternating score of
# nums after rearranging its elements.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 12
#
# Explanation:
#
# A possible rearrangement for nums is [2,1,3], which gives the maximum
# alternating score among all possible rearrangements.
#
# The alternating score is calculated as:
#
# score = 2^2 - 1^2 + 3^2 = 4 - 1 + 9 = 12
#
# Example 2:
#
# Input: nums = [1,-1,2,-2,3,-3]
#
# Output: 16
#
# Explanation:
#
# A possible rearrangement for nums is [-3,-1,-2,1,3,2], which gives the
# maximum alternating score among all possible rearrangements.
#
# The alternating score is calculated as:
#
# score = (-3)^2 - (-1)^2 + (-2)^2 - (1)^2 + (3)^2 - (2)^2 = 9 - 1 + 4 - 1
# + 9 - 4 = 16
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -4 * 10^4 <= nums[i] <= 4 * 10^4
#

# @lc code=start
from typing import List


class Solution:
    def maxAlternatingSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Squares erase sign. Alternating score puts ceil(n/2) terms positive and
        floor(n/2) negative, so assign the largest squares to '+' slots.

        Algorithm:
        - Sort squares; sum of the larger half minus sum of the smaller half.

        Complexity: O(n log n) time, O(n) space.
        """
        sq = sorted(x * x for x in nums)
        mid = len(sq) // 2
        return sum(sq[mid:]) - sum(sq[:mid])

    def maxAlternatingSum_two_pointer(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: after sorting squares, accumulate from both ends.

        Algorithm:
        - Positive contribution from the right half, negative from the left.

        Complexity: O(n log n) time, O(n) space.
        """
        sq = sorted(x * x for x in nums)
        ans = 0
        l, r = 0, len(sq) - 1
        while l < r:
            ans += sq[r] - sq[l]
            l += 1
            r -= 1
        if l == r:
            ans += sq[l]
        return ans
# @lc code=end

