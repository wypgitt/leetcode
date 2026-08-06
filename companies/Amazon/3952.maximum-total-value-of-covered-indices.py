#
# @lc app=leetcode id=3952 lang=python3
#
# [3952] Maximum Total Value of Covered Indices
#
# https://leetcode.com/problems/maximum-total-value-of-covered-indices/description/
#
# algorithms
# Medium (28.60%)
# Likes:    70
# Dislikes: 6
# Total Accepted:    18.4K
# Total Submissions: 64.2K
# Testcase Example:  "[9,2,6,1]\n\"0101\""
#
#
# You are given an integer array nums of length n and a binary string s of
# length n, where s[i] == '1' means index i initially contains a token and
# s[i] == '0' means it does not.
#
# You may perform the following operation any number of times:
#
# Choose a token currently located at index i, where i > 0, such that this
# token has not been moved before.
#
# Move this token from index i to index i - 1.
#
# An index is considered covered if it contains a token after all moves.
#
# Return an integer denoting the maximum total value of nums at the
# covered indices after optimally performing the operations.
#
# Example 1:
#
# Input: nums = [9,2,6,1], s = "0101"
#
# Output: 15
#
# Explanation:
#
# Initially, indices 1 and 3 contain tokens.
#
# Move the token from index 3 to index 2.
#
# Move the token from index 1 to index 0.
#
# The covered indices are [0, 2], so the total value is nums[0] + nums[2]
# = 9 + 6 = 15.
#
# Example 2:
#
# Input: nums = [5,1,4], s = "001"
#
# Output: 4
#
# Explanation:
#
# Initially, only index 2 contains a token.
#
# It is optimal to leave the token at index 2.
#
# The covered index is [2], so the total value is nums[2] = 4.
#
# Example 3:
#
# Input: nums = [9,3,5], s = "011"
#
# Output: 14
#
# Explanation:
#
# Initially, indices 1 and 2 contain tokens.
#
# Move the token from index 1 to index 0.
#
# The covered indices are [0, 2], so the total value is nums[0] + nums[2]
# = 9 + 5 = 14.
#
# Constraints:
#
# 1 <= n == nums.length == s.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# ​​​​​​​s[i] is either '0' or '1'
#

# @lc code=start
from typing import List


class Solution:
    def maxTotal(self, nums: List[int], s: str) -> int:
        """
        Interview explanation:
        Each token may stay or move one step left once. Assign tokens left to
        right, preferring a free left neighbor when it has larger value.

        Algorithm:
        - Scan tokens left→right; if i-1 is free and nums[i-1] > nums[i], cover
          i-1; else cover i.
        - Sum nums at covered indices.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        covered = -1
        for i, ch in enumerate(s):
            if ch != '1':
                continue
            if i > 0 and covered != i - 1 and nums[i - 1] > nums[i]:
                ans += nums[i - 1]
                covered = i - 1
            else:
                ans += nums[i]
                covered = i
        return ans
# @lc code=end
