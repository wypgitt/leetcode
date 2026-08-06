#
# @lc app=leetcode id=3781 lang=python3
#
# [3781] Maximum Score After Binary Swaps
#
# https://leetcode.com/problems/maximum-score-after-binary-swaps/description/
#
# algorithms
# Medium (35.53%)
# Likes:    84
# Dislikes: 2
# Total Accepted:    15.2K
# Total Submissions: 42.8K
# Testcase Example:  "[2,1,5,2,3]\n\"01010\""
#
#
# You are given an integer array nums of length n and a binary string s of
# the same length.
#
# Initially, your score is 0. Each index i where s[i] = '1' contributes
# nums[i] to the score.
#
# You may perform any number of operations (including zero). In one
# operation, you may choose an index i such that 0 <= i < n - 1, where
# s[i] = '0', and s[i + 1] = '1', and swap these two characters.
#
# Return an integer denoting the maximum possible score you can achieve.
#
# Example 1:
#
# Input: nums = [2,1,5,2,3], s = "01010"
#
# Output: 7
#
# Explanation:
#
# We can perform the following swaps:
#
# Swap at index i = 0: "01010" changes to "10010"
#
# Swap at index i = 2: "10010" changes to "10100"
#
# Positions 0 and 2 contain '1', contributing nums[0] + nums[2] = 2 + 5 =
# 7. This is maximum score achievable.
#
# Example 2:
#
# Input: nums = [4,7,2,9], s = "0000"
#
# Output: 0
#
# Explanation:
#
# There are no '1' characters in s, so no swaps can be performed. The
# score remains 0.
#
# Constraints:
#
# n == nums.length == s.length
#
# 1 <= n <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# s[i] is either '0' or '1'
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def maximumScore(self, nums: List[int], s: str) -> int:
        """
        Interview explanation:
        Swapping 01 -> 10 lets every '1' move left freely past zeros. Each '1'
        can claim one of the best nums among positions it can reach.

        Algorithm:
        - Scan L->R: push nums[i]; when s[i]=='1', add the current max from the heap.

        Complexity: O(n log n) time, O(n) space.
        """
        pq: List[int] = []
        score = 0
        for i, x in enumerate(nums):
            heapq.heappush(pq, -x)
            if s[i] == "1":
                score += -heapq.heappop(pq)
        return score
# @lc code=end
