#
# @lc app=leetcode id=3577 lang=python3
#
# [3577] Count the Number of Computer Unlocking Permutations
#
# https://leetcode.com/problems/count-the-number-of-computer-unlocking-permutations/description/
#
# algorithms
# Medium (58.95%)
# Likes:    360
# Dislikes: 133
# Total Accepted:    95.2K
# Total Submissions: 161.4K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an array complexity of length n.
#
# There are n locked computers in a room with labels from 0 to n - 1, each
# with its own unique password. The password of the computer i has a
# complexity complexity[i].
#
# The password for the computer labeled 0 is already decrypted and serves
# as the root. All other computers must be unlocked using it or another
# previously unlocked computer, following this information:
#
# You can decrypt the password for the computer i using the password for
# computer j, where j is any integer less than i with a lower complexity.
# (i.e. j < i and complexity[j] < complexity[i])
#
# To decrypt the password for computer i, you must have already unlocked a
# computer j such that j < i and complexity[j] < complexity[i].
#
# Find the number of permutations of [0, 1, 2, ..., (n - 1)] that
# represent a valid order in which the computers can be unlocked, starting
# from computer 0 as the only initially unlocked one.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# Note that the password for the computer with label 0 is decrypted, and
# not the computer with the first position in the permutation.
#
# Example 1:
#
# Input: complexity = [1,2,3]
#
# Output: 2
#
# Explanation:
#
# The valid permutations are:
#
# [0, 1, 2]
#
# Unlock computer 0 first with root password.
#
# Unlock computer 1 with password of computer 0 since complexity[0] <
# complexity[1].
#
# Unlock computer 2 with password of computer 1 since complexity[1] <
# complexity[2].
#
# [0, 2, 1]
#
# Unlock computer 0 first with root password.
#
# Unlock computer 2 with password of computer 0 since complexity[0] <
# complexity[2].
#
# Unlock computer 1 with password of computer 0 since complexity[0] <
# complexity[1].
#
# Example 2:
#
# Input: complexity = [3,3,3,4,4,4]
#
# Output: 0
#
# Explanation:
#
# There are no possible permutations which can unlock all computers.
#
# Constraints:
#
# 2 <= complexity.length <= 10^5
#
# 1 <= complexity[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def countPermutations(self, complexity: List[int]) -> int:
        """
        Interview explanation:
        Computer 0 starts unlocked. Unlocking i requires some already-unlocked
        j < i with complexity[j] < complexity[i]. If complexity[0] is not
        strictly smaller than every other value, some computer is unreachable.
        If it is the unique minimum, 0 can unlock every other computer, so every
        order with 0 first is valid → (n-1)!.

        Algorithm:
        - If any complexity[i] <= complexity[0] for i > 0, return 0.
        - Else return (n-1)! mod 10^9+7.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        n = len(complexity)
        c0 = complexity[0]
        for i in range(1, n):
            if complexity[i] <= c0:
                return 0
        ans = 1
        for i in range(1, n):
            ans = ans * i % MOD
        return ans
# @lc code=end
