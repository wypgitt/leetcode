#
# @lc app=leetcode id=673 lang=python3
#
# [673] Number of Longest Increasing Subsequence
#
# https://leetcode.com/problems/number-of-longest-increasing-subsequence/description/
#
# algorithms
# Medium (51.86%)
# Likes:    7323
# Dislikes: 288
# Total Accepted:    339.2K
# Total Submissions: 654.1K
# Testcase Example:  '[1,3,5,4,7]'
#
# Given an integer array nums, return the number of longest increasing
# subsequences.
# 
# Notice that the sequence has to be strictly increasing.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,3,5,4,7]
# Output: 2
# Explanation: The two longest increasing subsequences are [1, 3, 4, 7] and [1,
# 3, 5, 7].
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,2,2,2,2]
# Output: 5
# Explanation: The length of the longest increasing subsequence is 1, and there
# are 5 increasing subsequences of length 1, so output 5.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 2000
# -10^6 <= nums[i] <= 10^6
# The answer is guaranteed to fit inside a 32-bit integer.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def findNumberOfLIS(self, nums: List[int]) -> int:
        n = len(nums)
        lengths = [1] * n
        counts = [1] * n
        for i in range(n):
            for j in range(i):
                if nums[j] < nums[i]:
                    if lengths[j] + 1 > lengths[i]:
                        lengths[i] = lengths[j] + 1
                        counts[i] = counts[j]
                    elif lengths[j] + 1 == lengths[i]:
                        counts[i] += counts[j]
        longest = max(lengths, default=0)
        return sum(c for l, c in zip(lengths, counts) if l == longest)
# @lc code=end

"""
Interview explanation:
For each index i, track the length of the longest increasing subsequence ending at i and how many such subsequences exist. Each earlier j with nums[j] < nums[i] can extend into i. A better length replaces the count; an equal length adds to the count.

Data structure: two parallel DP arrays: lengths and counts.

Edge cases: duplicate values do not extend each other because the condition is strictly <. Empty input would return 0 via the default max.

Complexity: O(n^2) time from all pairs and O(n) space.
"""
