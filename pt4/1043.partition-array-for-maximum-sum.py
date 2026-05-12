#
# @lc app=leetcode id=1043 lang=python3
#
# [1043] Partition Array for Maximum Sum
#
# https://leetcode.com/problems/partition-array-for-maximum-sum/description/
#
# algorithms
# Medium (77.34%)
# Likes:    5076
# Dislikes: 439
# Total Accepted:    267.7K
# Total Submissions: 346.2K
# Testcase Example:  '[1,15,7,9,2,5,10]\n3'
#
# Given an integer array arr, partition the array into (contiguous) subarrays
# of length at most k. After partitioning, each subarray has their values
# changed to become the maximum value of that subarray.
# 
# Return the largest sum of the given array after partitioning. Test cases are
# generated so that the answer fits in a 32-bit integer.
# 
# 
# Example 1:
# 
# 
# Input: arr = [1,15,7,9,2,5,10], k = 3
# Output: 84
# Explanation: arr becomes [15,15,15,9,10,10,10]
# 
# 
# Example 2:
# 
# 
# Input: arr = [1,4,1,5,7,3,6,1,9,9,3], k = 4
# Output: 83
# 
# 
# Example 3:
# 
# 
# Input: arr = [1], k = 1
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 500
# 0 <= arr[i] <= 10^9
# 1 <= k <= arr.length
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def maxSumAfterPartitioning(self, arr: List[int], k: int) -> int:
        dp = [0] * (len(arr) + 1)

        for end in range(1, len(arr) + 1):
            current_max = 0
            for length in range(1, min(k, end) + 1):
                current_max = max(current_max, arr[end - length])
                dp[end] = max(dp[end], dp[end - length] + current_max * length)

        return dp[-1]
# @lc code=end

"""
Interview Explanation

Core idea:
The last partition determines the recurrence. If the last block has length L,
its contribution is L times the maximum value in that block, plus the best
answer for everything before it.

Algorithm:
Let dp[end] be the best score for arr[:end].
For each end position:
1. Try every possible last block length from 1 to k.
2. Maintain the maximum value inside that last block while expanding backward.
3. Update dp[end] with dp[end - length] + max_value * length.

Data structure choice:
A one-dimensional DP array is sufficient because the state only depends on a
prefix length. The current block maximum can be maintained incrementally,
avoiding repeated scans.

Correctness:
Every valid partition of arr[:end] has some final block length L <= k. The
score before that block is optimally dp[end - L], and the block's score is
max(block) * L. Trying all valid L therefore considers every possible final
partition and takes the best one.

Complexity:
There are n end positions and up to k lengths per position, so time is O(nk).
Space is O(n).

Tests and edge cases:
- k = 1: no grouping; answer is sum(arr).
- k = n: one large block may be optimal but DP still compares all choices.
- Single element array returns that element.
- Large values are safe in Python; LeetCode guarantees 32-bit answer.
"""
