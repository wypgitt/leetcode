#
# @lc app=leetcode id=1027 lang=python3
#
# [1027] Longest Arithmetic Subsequence
#
# https://leetcode.com/problems/longest-arithmetic-subsequence/description/
#
# algorithms
# Medium (50.12%)
# Likes:    4942
# Dislikes: 221
# Total Accepted:    217K
# Total Submissions: 434K
# Testcase Example:  "[3,6,9,12]"
#
# Given an array nums of integers, return the length of the longest arithmetic
# subsequence in nums.
#
# Note that:
#
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
#
# A sequence seq is arithmetic if seq[i + 1] - seq[i] are all the same value
# (for 0 <= i < seq.length - 1).
#
# Example 1:
#
# Input: nums = [3,6,9,12]
# Output: 4
# Explanation: The whole array is an arithmetic sequence with steps of length =
# 3.
#
# Example 2:
#
# Input: nums = [9,4,7,2,10]
# Output: 3
# Explanation: The longest arithmetic subsequence is [4,7,10].
#
# Example 3:
#
# Input: nums = [20,1,15,3,10,5,8]
# Output: 4
# Explanation: The longest arithmetic subsequence is [20,15,10,5].
#
# Constraints:
#
# 2 <= nums.length <= 1000
#
# 0 <= nums[i] <= 500
#

# @lc code=start
from typing import List


class Solution:
    def longestArithSeqLength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        DP where dp[i][d] = longest arithmetic subsequence ending at i with
        difference d. For each pair (j,i) j<i, d=nums[i]-nums[j],
        dp[i][d]=dp[j][d]+1 (or 2).

        Algorithm:
        - dp = [dict() for _ in nums]; best=2
        - For i: for j<i: d=nums[i]-nums[j]; dp[i][d]=dp[j].get(d,1)+1; best=max

        Complexity: O(n^2) time, O(n^2) space worst case.
        """
        n = len(nums)
        if n <= 2:
            return n
        dp = [{} for _ in range(n)]
        best = 2
        for i in range(n):
            for j in range(i):
                d = nums[i] - nums[j]
                dp[i][d] = dp[j].get(d, 1) + 1
                best = max(best, dp[i][d])
        return best
# @lc code=end
