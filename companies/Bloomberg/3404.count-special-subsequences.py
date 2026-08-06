#
# @lc app=leetcode id=3404 lang=python3
#
# [3404] Count Special Subsequences
#
# https://leetcode.com/problems/count-special-subsequences/description/
#
# algorithms
# Medium (29.86%)
# Likes:    201
# Dislikes: 27
# Total Accepted:    11.8K
# Total Submissions: 39.5K
# Testcase Example:  "[1,2,3,4,3,6,1]"
#
#
# You are given an array nums consisting of positive integers.
#
# A special subsequence is defined as a subsequence of length 4,
# represented by indices (p, q, r, s), where p < q < r < s. This
# subsequence must satisfy the following conditions:
#
# nums[p] * nums[r] == nums[q] * nums[s]
#
# There must be at least one element between each pair of indices. In
# other words, q - p > 1, r - q > 1 and s - r > 1.
#
# Return the number of different special subsequences in nums.
#
# Example 1:
#
# Input: nums = [1,2,3,4,3,6,1]
#
# Output: 1
#
# Explanation:
#
# There is one special subsequence in nums.
#
# (p, q, r, s) = (0, 2, 4, 6):
#
# This corresponds to elements (1, 3, 3, 1).
#
# nums[p] * nums[r] = nums[0] * nums[4] = 1 * 3 = 3
#
# nums[q] * nums[s] = nums[2] * nums[6] = 3 * 1 = 3
#
# Example 2:
#
# Input: nums = [3,4,3,4,3,4,3,4]
#
# Output: 3
#
# Explanation:
#
# There are three special subsequences in nums.
#
# (p, q, r, s) = (0, 2, 4, 6):
#
# This corresponds to elements (3, 3, 3, 3).
#
# nums[p] * nums[r] = nums[0] * nums[4] = 3 * 3 = 9
#
# nums[q] * nums[s] = nums[2] * nums[6] = 3 * 3 = 9
#
# (p, q, r, s) = (1, 3, 5, 7):
#
# This corresponds to elements (4, 4, 4, 4).
#
# nums[p] * nums[r] = nums[1] * nums[5] = 4 * 4 = 16
#
# nums[q] * nums[s] = nums[3] * nums[7] = 4 * 4 = 16
#
# (p, q, r, s) = (0, 2, 5, 7):
#
# This corresponds to elements (3, 3, 4, 4).
#
# nums[p] * nums[r] = nums[0] * nums[5] = 3 * 4 = 12
#
# nums[q] * nums[s] = nums[2] * nums[7] = 3 * 4 = 12
#
# Constraints:
#
# 7 <= nums.length <= 1000
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from collections import defaultdict
from math import gcd
from typing import List


class Solution:
    def numberOfSubsequences(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count index tuples (p,q,r,s) with gaps between each pair and
        nums[p]*nums[r] == nums[q]*nums[s], i.e. nums[p]/nums[q] ==
        nums[s]/nums[r]. Store reduced ratios of (s,r) pairs and match
        against (p,q) while sliding q.

        Algorithm:
        - Preload ratio counts for all valid (r,s) with r >= 4.
        - For each q, add matches from all valid p; then drop ratios for
          r = q+2 that leave the legal window.

        Complexity: O(n^2) time, O(U^2) space for ratio counts (U=value range).
        """
        n = len(nums)
        cnt = defaultdict(int)
        for r in range(4, n - 2):
            c = nums[r]
            for s in range(r + 2, n):
                d = nums[s]
                g = gcd(c, d)
                cnt[(d // g, c // g)] += 1
        ans = 0
        for q in range(2, n - 4):
            b = nums[q]
            for p in range(q - 1):
                a = nums[p]
                g = gcd(a, b)
                ans += cnt[(a // g, b // g)]
            c = nums[q + 2]
            for s in range(q + 4, n):
                d = nums[s]
                g = gcd(c, d)
                cnt[(d // g, c // g)] -= 1
        return ans
# @lc code=end
