#
# @lc app=leetcode id=3395 lang=python3
#
# [3395] Subsequences with a Unique Middle Mode I
#
# https://leetcode.com/problems/subsequences-with-a-unique-middle-mode-i/description/
#
# algorithms
# Hard (21.84%)
# Likes:    25
# Dislikes: 25
# Total Accepted:    2.9K
# Total Submissions: 13.2K
# Testcase Example:  "[1,1,1,1,1,1]"
#
#
# Given an integer array nums, find the number of subsequences of size 5
# of nums with a unique middle mode.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# A mode of a sequence of numbers is defined as the element that appears
# the maximum number of times in the sequence.
#
# A sequence of numbers contains a unique mode if it has only one mode.
#
# A sequence of numbers seq of size 5 contains a unique middle mode if the
# middle element (seq[2]) is a unique mode.
#
# Example 1:
#
# Input: nums = [1,1,1,1,1,1]
#
# Output: 6
#
# Explanation:
#
# [1, 1, 1, 1, 1] is the only subsequence of size 5 that can be formed,
# and it has a unique middle mode of 1. This subsequence can be formed in
# 6 different ways, so the output is 6.
#
# Example 2:
#
# Input: nums = [1,2,2,3,3,4]
#
# Output: 4
#
# Explanation:
#
# [1, 2, 2, 3, 4] and [1, 2, 3, 3, 4] each have a unique middle mode
# because the number at index 2 has the greatest frequency in the
# subsequence. [1, 2, 2, 3, 3] does not have a unique middle mode because
# 2 and 3 appear twice.
#
# Example 3:
#
# Input: nums = [0,1,2,3,4,5,6,7,8]
#
# Output: 0
#
# Explanation:
#
# There is no subsequence of length 5 with a unique middle mode.
#
# Constraints:
#
# 5 <= nums.length <= 1000
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def subsequencesWithMiddleMode(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count length-5 subsequences whose middle element is the unique mode.
        Fix the middle index; total C(L,2)*C(R,2) minus configurations where some
        other value ties/beats the middle's frequency (combinatorial casework).

        Algorithm:
        - Maintain left/right frequency maps while scanning the middle index.
        - Keep aggregate sums (sum left[x]^2, left[x]*right[x], ...) excluding the
          middle value to subtract invalid bb/a/ac, ab/a/bc, ... patterns in O(1).

        Complexity: O(n) time, O(n) space.
        """
        def nC2(x: int) -> int:
            return x * (x - 1) // 2

        MOD = 10**9 + 7
        result = 0
        left = defaultdict(int)
        right = defaultdict(int)
        for x in nums:
            right[x] += 1

        left_x_sq = 0
        right_x_sq = sum(v * v for v in right.values())
        left_x_right_x = 0
        left_x_sq_right_x = 0
        left_x_right_x_sq = 0

        for i, v in enumerate(nums):
            left_x_sq -= left[v] * left[v]
            right_x_sq -= right[v] * right[v]
            left_x_right_x -= left[v] * right[v]
            left_x_sq_right_x -= left[v] * left[v] * right[v]
            left_x_right_x_sq -= left[v] * right[v] * right[v]
            right[v] -= 1

            l, r = i, len(nums) - (i + 1)
            result += nC2(l) * nC2(r)
            result -= nC2(l - left[v]) * nC2(r - right[v])
            result -= (
                (left_x_sq - (l - left[v])) * (r - right[v])
                - (left_x_sq_right_x - left_x_right_x)
            ) * right[v] // 2
            result -= (
                (right_x_sq - (r - right[v])) * (l - left[v])
                - (left_x_right_x_sq - left_x_right_x)
            ) * left[v] // 2
            result -= left[v] * left_x_right_x * (r - right[v]) - left[v] * left_x_right_x_sq
            result -= right[v] * left_x_right_x * (l - left[v]) - right[v] * left_x_sq_right_x
            result -= right[v] * (left_x_sq_right_x - left_x_right_x) // 2
            result -= left[v] * (left_x_right_x_sq - left_x_right_x) // 2

            left[v] += 1
            left_x_sq += left[v] * left[v]
            right_x_sq += right[v] * right[v]
            left_x_right_x += left[v] * right[v]
            left_x_sq_right_x += left[v] * left[v] * right[v]
            left_x_right_x_sq += left[v] * right[v] * right[v]

        return result % MOD
# @lc code=end
