#
# @lc app=leetcode id=3202 lang=python3
#
# [3202] Find the Maximum Length of Valid Subsequence II
#
# https://leetcode.com/problems/find-the-maximum-length-of-valid-subsequence-ii/description/
#
# algorithms
# Medium (57.11%)
# Likes:    662
# Dislikes: 56
# Total Accepted:    102.7K
# Total Submissions: 179.9K
# Testcase Example:  "[1,2,3,4,5]\n2"
#
#
# You are given an integer array nums and a positive integer k.
#
# A subsequence sub of nums with length x is called valid if it satisfies:
#
# (sub[0] + sub[1]) % k == (sub[1] + sub[2]) % k == ... == (sub[x - 2] +
# sub[x - 1]) % k.
#
# Return the length of the longest valid subsequence of nums.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5], k = 2
#
# Output: 5
#
# Explanation:
#
# The longest valid subsequence is [1, 2, 3, 4, 5].
#
# Example 2:
#
# Input: nums = [1,4,2,3,1,4], k = 3
#
# Output: 4
#
# Explanation:
#
# The longest valid subsequence is [1, 4, 1, 4].
#
# Constraints:
#
# 2 <= nums.length <= 10^3
#
# 1 <= nums[i] <= 10^7
#
# 1 <= k <= 10^3
#

# @lc code=start
from typing import List


class Solution:
    def maximumLength(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Valid means every adjacent pair has the same (sum % k). Residues then
        alternate between two values a,b with (a+b)%k fixed (including a==b).

        Algorithm:
        - dp[j][x]: longest valid subsequence ending with residue x whose
          adjacent-sum mod involves partner residue j (transition
          dp[j][x] = dp[x][j] + 1 when appending x after a chain ending in j).
        - Scan nums; for each residue x and each j update and track the max.

        Complexity: O(n * k) time, O(k^2) space.
        """
        dp = [[0] * k for _ in range(k)]
        ans = 0
        for num in nums:
            x = num % k
            for j in range(k):
                dp[j][x] = dp[x][j] + 1
                if dp[j][x] > ans:
                    ans = dp[j][x]
        return ans
# @lc code=end
