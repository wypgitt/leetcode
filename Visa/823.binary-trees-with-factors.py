#
# @lc app=leetcode id=823 lang=python3
#
# [823] Binary Trees With Factors
#
# https://leetcode.com/problems/binary-trees-with-factors/description/
#
# algorithms
# Medium (53.09%)
# Likes:    3376
# Dislikes: 262
# Total Accepted:    160K
# Total Submissions: 301.5K
# Testcase Example:  '[2,4]'
#
# Given an array of unique integers, arr, where each integer arr[i] is strictly
# greater than 1.
# 
# We make a binary tree using these integers, and each number may be used for
# any number of times. Each non-leaf node's value should be equal to the
# product of the values of its children.
# 
# Return the number of binary trees we can make. The answer may be too large so
# return the answer modulo 10^9 + 7.
# 
# 
# Example 1:
# 
# 
# Input: arr = [2,4]
# Output: 3
# Explanation: We can make these trees: [2], [4], [4, 2, 2]
# 
# Example 2:
# 
# 
# Input: arr = [2,4,5,10]
# Output: 7
# Explanation: We can make these trees: [2], [4], [5], [10], [4, 2, 2], [10, 2,
# 5], [10, 5, 2].
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 1000
# 2 <= arr[i] <= 10^9
# All the values of arr are unique.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def numFactoredBinaryTrees(self, arr: List[int]) -> int:
        MOD = 10 ** 9 + 7
        arr.sort()
        dp = {}
        values = set(arr)
        for x in arr:
            total = 1
            for a in arr:
                if a * a > x:
                    break
                if x % a == 0:
                    b = x // a
                    if b in values:
                        ways = dp[a] * dp[b]
                        total += ways if a == b else 2 * ways
            dp[x] = total % MOD
        return sum(dp.values()) % MOD
# @lc code=end

"""
Interview explanation:
Sort values so factor subtrees are computed before their product. For each root value x, start with the single-node tree. For every factor pair a*b=x present in arr, combine any tree rooted at a with any tree rooted at b. If a and b differ, left/right order doubles the count.

Data structure: dp[value] stores the number of trees rooted at value; a set gives O(1) factor existence checks.

Edge cases: every value contributes at least one single-node tree. Equal factor pairs are not doubled.

Complexity: the implementation checks factors up to sqrt by iterating sorted arr, worst-case O(n^2) time and O(n) space.
"""
