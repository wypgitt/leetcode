#
# @lc app=leetcode id=1027 lang=python3
#
# [1027] Longest Arithmetic Subsequence
#
# https://leetcode.com/problems/longest-arithmetic-subsequence/description/
#
# algorithms
# Medium (49.95%)
# Likes:    4921
# Dislikes: 220
# Total Accepted:    213.1K
# Total Submissions: 426.6K
# Testcase Example:  '[3,6,9,12]'
#
# Given an array nums of integers, return the length of the longest arithmetic
# subsequence in nums.
# 
# Note that:
# 
# 
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
# A sequence seq is arithmetic if seq[i + 1] - seq[i] are all the same value
# (for 0 <= i < seq.length - 1).
# 
# 
# 
# Example 1:
# 
# 
# Input: nums = [3,6,9,12]
# Output: 4
# Explanation:  The whole array is an arithmetic sequence with steps of length
# = 3.
# 
# 
# Example 2:
# 
# 
# Input: nums = [9,4,7,2,10]
# Output: 3
# Explanation:  The longest arithmetic subsequence is [4,7,10].
# 
# 
# Example 3:
# 
# 
# Input: nums = [20,1,15,3,10,5,8]
# Output: 4
# Explanation:  The longest arithmetic subsequence is [20,15,10,5].
# 
# 
# 
# Constraints:
# 
# 
# 2 <= nums.length <= 1000
# 0 <= nums[i] <= 500
# 
# 
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def longestArithSeqLength(self, nums: List[int]) -> int:
        dp = [defaultdict(lambda: 1) for _ in nums]
        best = 2

        for right in range(len(nums)):
            for left in range(right):
                diff = nums[right] - nums[left]
                dp[right][diff] = max(dp[right][diff], dp[left][diff] + 1)
                best = max(best, dp[right][diff])

        return best
# @lc code=end

"""
Interview Explanation

Core idea:
An arithmetic subsequence is determined by its last index and common
difference. If nums[left] can end a sequence with difference d, then
nums[right] can extend it when nums[right] - nums[left] == d.

Algorithm:
Let dp[i][d] be the length of the longest arithmetic subsequence ending at
index i with common difference d.
For every pair left < right:
1. Compute d = nums[right] - nums[left].
2. Extend the best sequence ending at left with difference d.
3. Store the improved length at dp[right][d].

Data structure choice:
Each index uses a hash map from difference to length. Differences can be
negative and vary across pairs, so a dictionary is cleaner than a fixed array.

Correctness:
Every arithmetic subsequence of length at least 2 has a final pair
(left, right) and a fixed difference d. The transition extends the optimal
subsequence ending at left with that d, so it builds the optimal subsequence
ending at right. Considering all pairs covers every possible final pair, and
the maximum recorded length is the global optimum.

Complexity:
There are O(n^2) pairs. Dictionary operations are O(1) average, so time is
O(n^2), and space is O(n^2) in the worst case.

Tests and edge cases:
- All numbers equal: diff 0 grows to length n.
- Strictly increasing arithmetic array: answer n.
- Negative differences are handled because dictionary keys can be negative.
- Minimum n = 2 returns 2.
"""
