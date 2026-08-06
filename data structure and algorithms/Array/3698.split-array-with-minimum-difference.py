#
# @lc app=leetcode id=3698 lang=python3
#
# [3698] Split Array With Minimum Difference
#
# https://leetcode.com/problems/split-array-with-minimum-difference/description/
#
# algorithms
# Medium (33.59%)
# Likes:    103
# Dislikes: 16
# Total Accepted:    41.6K
# Total Submissions: 123.9K
# Testcase Example:  "[1,3,2]"
#
#
# You are given an integer array nums.
#
# Split the array into exactly two subarrays, left and right, such that
# left is strictly increasing  and right is strictly decreasing.
#
# Return the minimum possible absolute difference between the sums of left
# and right. If no valid split exists, return -1.
#
# Example 1:
#
# Input: nums = [1,3,2]
#
# Output: 2
#
# Explanation:
#
#                         i
#                         left
#                         right
#                         Validity
#                         left sum
#                         right sum
#                         Absolute difference
#
#                         0
#                         [1]
#                         [3, 2]
#                         Yes
#                         1
#                         5
#                         |1 - 5| = 4
#
#                         1
#                         [1, 3]
#                         [2]
#                         Yes
#                         4
#                         2
#                         |4 - 2| = 2
#
# Thus, the minimum absolute difference is 2.
#
# Example 2:
#
# Input: nums = [1,2,4,3]
#
# Output: 4
#
# Explanation:
#
#                         i
#                         left
#                         right
#                         Validity
#                         left sum
#                         right sum
#                         Absolute difference
#
#                         0
#                         [1]
#                         [2, 4, 3]
#                         No
#                         1
#                         9
#                         -
#
#                         1
#                         [1, 2]
#                         [4, 3]
#                         Yes
#                         3
#                         7
#                         |3 - 7| = 4
#
#                         2
#                         [1, 2, 4]
#                         [3]
#                         Yes
#                         7
#                         3
#                         |7 - 3| = 4
#
# Thus, the minimum absolute difference is 4.
#
# Example 3:
#
# Input: nums = [3,1,2]
#
# Output: -1
#
# Explanation:
#
# No valid split exists, so the answer is -1.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def splitArray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Valid splits need a strict-increasing prefix and a strict-decreasing
        suffix that cover the array without overlap. Minimize |left_sum - right_sum|.

        Algorithm:
        - Precompute whether nums[0..i] is strict-increasing and nums[i..n-1]
          is strict-decreasing.
        - For each split i | i+1, if both sides valid, track min abs sum diff.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        inc = [False] * n
        dec = [False] * n
        inc[0] = True
        for i in range(1, n):
            inc[i] = inc[i - 1] and nums[i] > nums[i - 1]
        dec[n - 1] = True
        for i in range(n - 2, -1, -1):
            dec[i] = dec[i + 1] and nums[i] > nums[i + 1]
        total = sum(nums)
        left = 0
        ans = float('inf')
        for i in range(n - 1):
            left += nums[i]
            if inc[i] and dec[i + 1]:
                ans = min(ans, abs(left - (total - left)))
        return -1 if ans == float('inf') else ans
# @lc code=end
