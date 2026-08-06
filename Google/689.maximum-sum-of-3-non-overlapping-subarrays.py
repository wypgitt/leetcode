#
# @lc app=leetcode id=689 lang=python3
#
# [689] Maximum Sum of 3 Non-Overlapping Subarrays
#
# https://leetcode.com/problems/maximum-sum-of-3-non-overlapping-subarrays/description/
#
# algorithms
# Hard (59.95%)
# Likes:    2636
# Dislikes: 159
# Total Accepted:    159K
# Total Submissions: 265K
# Testcase Example:  "[1,2,1,2,6,7,5,1]"
#
# Given an integer array nums and an integer k, find three non-overlapping
# subarrays of length k with maximum sum and return them.
#
# Return the result as a list of indices representing the starting position of
# each interval (0-indexed). If there are multiple answers, return the
# lexicographically smallest one.
#
# Example 1:
#
# Input: nums = [1,2,1,2,6,7,5,1], k = 2
# Output: [0,3,5]
# Explanation: Subarrays [1, 2], [2, 6], [7, 5] correspond to the starting
# indices [0, 3, 5].
# We could have also taken [2, 1], but an answer of [1, 3, 5] would be
# lexicographically larger.
#
# Example 2:
#
# Input: nums = [1,2,1,2,1,2,1,2,1], k = 2
# Output: [0,2,4]
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# 1 <= nums[i] < 2^16
#
# 1 <= k <= floor(nums.length / 3)
#

# @lc code=start
from typing import List


class Solution:
    def maxSumOfThreeSubarrays(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Three non-overlapping length-k subarrays with maximum total sum; return
        lexicographically smallest start indices. Precompute window sums; track
        best single window on the left and best pair, then best triple.

        Algorithm:
        - wins[i] = sum(nums[i:i+k]).
        - left[i] = best start index in [0..i]; right[i] = best in [i..].
        - For mid m, maximize wins[left[m-k]] + wins[m] + wins[right[m+k]].

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        wins = [0] * (n - k + 1)
        s = sum(nums[:k])
        wins[0] = s
        for i in range(1, len(wins)):
            s += nums[i + k - 1] - nums[i - 1]
            wins[i] = s

        m = len(wins)
        left = [0] * m
        best = 0
        for i in range(m):
            if wins[i] > wins[best]:
                best = i
            left[i] = best

        right = [0] * m
        best = m - 1
        for i in range(m - 1, -1, -1):
            if wins[i] >= wins[best]:
                best = i
            right[i] = best

        ans = [-1, -1, -1]
        max_total = -1
        for mid in range(k, m - k):
            l, r = left[mid - k], right[mid + k]
            total = wins[l] + wins[mid] + wins[r]
            if total > max_total:
                max_total = total
                ans = [l, mid, r]
        return ans
# @lc code=end
