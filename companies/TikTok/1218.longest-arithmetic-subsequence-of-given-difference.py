#
# @lc app=leetcode id=1218 lang=python3
#
# [1218] Longest Arithmetic Subsequence of Given Difference
#
# https://leetcode.com/problems/longest-arithmetic-subsequence-of-given-difference/description/
#
# algorithms
# Medium (54.35%)
# Likes:    3397
# Dislikes: 92
# Total Accepted:    176K
# Total Submissions: 324K
# Testcase Example:  "[1,2,3,4]"
#
# Given an integer array arr and an integer difference, return the length of
# the longest subsequence in arr which is an arithmetic sequence such that the
# difference between adjacent elements in the subsequence equals difference.
#
# A subsequence is a sequence that can be derived from arr by deleting some or
# no elements without changing the order of the remaining elements.
#
# Example 1:
#
# Input: arr = [1,2,3,4], difference = 1
# Output: 4
# Explanation: The longest arithmetic subsequence is [1,2,3,4].
#
# Example 2:
#
# Input: arr = [1,3,5,7], difference = 1
# Output: 1
# Explanation: The longest arithmetic subsequence is any single element.
#
# Example 3:
#
# Input: arr = [1,5,7,8,5,3,4,2,1], difference = -2
# Output: 4
# Explanation: The longest arithmetic subsequence is [7,5,3,1].
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# -10^4 <= arr[i], difference <= 10^4
#


# @lc code=start
from typing import List

class Solution:
    def longestSubsequence(self, arr: List[int], difference: int) -> int:
        """
        Interview explanation:
        Longest arithmetic subsequence with fixed difference. DP: for each
        value x, dp[x] = dp[x-diff] + 1 (hash map of best ending at value).

        Algorithm:
        - mp empty; for x in arr: mp[x] = mp.get(x-difference,0)+1; track max

        Complexity: O(n) time, O(n) space.
        """
        mp = {}
        ans = 0
        for x in arr:
            mp[x] = mp.get(x - difference, 0) + 1
            ans = max(ans, mp[x])
        return ans
# @lc code=end
