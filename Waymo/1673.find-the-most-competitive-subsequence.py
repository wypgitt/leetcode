#
# @lc app=leetcode id=1673 lang=python3
#
# [1673] Find the Most Competitive Subsequence
#
# https://leetcode.com/problems/find-the-most-competitive-subsequence/description/
#
# algorithms
# Medium (53.37%)
# Likes:    2208
# Dislikes: 106
# Total Accepted:    88.7K
# Total Submissions: 166K
# Testcase Example:  "[3,5,2,6]"
#
# Given an integer array nums and a positive integer k, return the most
# competitive subsequence of nums of size k.
#
# An array's subsequence is a resulting sequence obtained by erasing some
# (possibly zero) elements from the array.
#
# We define that a subsequence a is more competitive than a subsequence b (of
# the same length) if in the first position where a and b differ, subsequence a
# has a number less than the corresponding number in b. For example, [1,3,4] is
# more competitive than [1,3,5] because the first position they differ is at
# the final number, and 4 is less than 5.
#
# Example 1:
#
# Input: nums = [3,5,2,6], k = 2
# Output: [2,6]
# Explanation: Among the set of every possible subsequence: {[3,5], [3,2],
# [3,6], [5,2], [5,6], [2,6]}, [2,6] is the most competitive.
#
# Example 2:
#
# Input: nums = [2,4,3,3,5,4,9,6], k = 4
# Output: [2,3,3,4]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#
# 1 <= k <= nums.length
#

# @lc code=start
from typing import List


class Solution:
    def mostCompetitive(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Lexicographically smallest subsequence of length k (most competitive).
        Monotonic increasing stack: pop larger previous while enough elements remain.

        Algorithm (mono stack):
        - For each v: while stack and stack[-1]>v and len(stack)+remaining>k: pop
          if len(stack)<k: push v.

        Complexity: O(n) time, O(k) space.
        """
        n = len(nums)
        stack = []
        for i, v in enumerate(nums):
            while stack and stack[-1] > v and len(stack) + (n - i) > k:
                stack.pop()
            if len(stack) < k:
                stack.append(v)
        return stack
# @lc code=end
