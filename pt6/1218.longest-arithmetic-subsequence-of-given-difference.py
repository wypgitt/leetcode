#
# @lc app=leetcode id=1218 lang=python3
#
# [1218] Longest Arithmetic Subsequence of Given Difference
#
# https://leetcode.com/problems/longest-arithmetic-subsequence-of-given-difference/description/
#
# algorithms
# Medium (54.33%)
# Likes:    3386
# Dislikes: 92
# Total Accepted:    172.6K
# Total Submissions: 317.6K
# Testcase Example:  '[1,2,3,4]\n1'
#
# Given an integer array arr and an integer difference, return the length of
# the longest subsequence in arr which is an arithmetic sequence such that the
# difference between adjacent elements in the subsequence equals difference.
# 
# A subsequence is a sequence that can be derived from arr by deleting some or
# no elements without changing the order of the remaining elements.
# 
# 
# Example 1:
# 
# 
# Input: arr = [1,2,3,4], difference = 1
# Output: 4
# Explanation: The longest arithmetic subsequence is [1,2,3,4].
# 
# Example 2:
# 
# 
# Input: arr = [1,3,5,7], difference = 1
# Output: 1
# Explanation: The longest arithmetic subsequence is any single element.
# 
# 
# Example 3:
# 
# 
# Input: arr = [1,5,7,8,5,3,4,2,1], difference = -2
# Output: 4
# Explanation: The longest arithmetic subsequence is [7,5,3,1].
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 10^5
# -10^4 <= arr[i], difference <= 10^4
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def longestSubsequence(self, arr: List[int], difference: int) -> int:
        best_ending_at = {}
        best = 0

        for num in arr:
            best_ending_at[num] = best_ending_at.get(num - difference, 0) + 1
            best = max(best, best_ending_at[num])

        return best
# @lc code=end

# Explanation
# -----------
# Let dp[x] be the longest valid subsequence ending with value x after scanning
# the processed prefix. For a new number num, the previous value must be
# num - difference, so the best chain ending at num is
# dp[num - difference] + 1.
#
# A hash map is the key data structure because values can be large or negative;
# indexing an array by value would be wasteful or impossible.
#
# The order of the array is respected because we update dp while scanning from
# left to right. We never reuse a future number.
#
# Edge cases: difference can be 0, in which case dp[num] simply counts repeated
# occurrences; negative differences are handled by the same formula.
#
# Time complexity: O(n) average.
# Space complexity: O(u), where u is the number of distinct values.
