#
# @lc app=leetcode id=484 lang=python3
#
# [484] Find Permutation
#
# https://leetcode.com/problems/find-permutation/description/
#
# algorithms
# Medium (66.74%)
# Likes:    731
# Dislikes: 151
# Total Accepted:    43.7K
# Total Submissions: 65.6K
# Testcase Example:  "\"I\""
#
#
# A permutation perm of n integers of all the integers in the range [1, n]
# can be represented as a string s of length n - 1 where:
#
# s[i] == 'I' if perm[i] < perm[i + 1], and
#
# s[i] == 'D' if perm[i] > perm[i + 1].
#
# Given a string s, reconstruct the lexicographically smallest permutation
# perm and return it.
#
# Example 1:
#
# Input: s = "I"
# Output: [1,2]
# Explanation: [1,2] is the only legal permutation that can represented by
# s, where the number 1 and 2 construct an increasing relationship.
#
# Example 2:
#
# Input: s = "DI"
# Output: [2,1,3]
# Explanation: Both [2,1,3] and [3,1,2] can be represented as "DI", but
# since we want to find the smallest lexicographical permutation, you
# should return [2,1,3]
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either 'I' or 'D'.
#
# @lc code=start
from typing import List


class Solution:
    def findPermutation(self, s: str) -> List[int]:
        """
        Interview explanation:
        Premium. Find the lexicographically smallest permutation of 1..n
        (n = len(s)+1) whose consecutive comparisons match s ('D'/'I').
        Greedy: write 1..n, then reverse each contiguous 'D' segment.

        Algorithm:
        - ans = [1,2,...,n]
        - For each run of D's from i..j, reverse ans[i:j+1].
        - Or: stack-based — push next number; on 'I' (or end) flush stack.

        Complexity: O(n) time and space.
        """
        n = len(s) + 1
        ans = list(range(1, n + 1))
        i = 0
        while i < len(s):
            if s[i] == "D":
                j = i
                while j < len(s) and s[j] == "D":
                    j += 1
                ans[i : j + 1] = reversed(ans[i : j + 1])
                i = j
            else:
                i += 1
        return ans
# @lc code=end
