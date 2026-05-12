#
# @lc app=leetcode id=1055 lang=python3
#
# [1055] Shortest Way to Form String
#
# https://leetcode.com/problems/shortest-way-to-form-string/description/
#
# algorithms
# Medium (61.62%)
# Likes:    1339
# Dislikes: 77
# Total Accepted:    111.6K
# Total Submissions: 181.1K
# Testcase Example:  '"abc"\n"abcbc"'
#
# A subsequence of a string is a new string that is formed from the original
# string by deleting some (can be none) of the characters without disturbing
# the relative positions of the remaining characters. (i.e., "ace" is a
# subsequence of "abcde" while "aec" is not).
# 
# Given two strings source and target, return the minimum number of
# subsequences of source such that their concatenation equals target. If the
# task is impossible, return -1.
# 
# 
# Example 1:
# 
# 
# Input: source = "abc", target = "abcbc"
# Output: 2
# Explanation: The target "abcbc" can be formed by "abc" and "bc", which are
# subsequences of source "abc".
# 
# 
# Example 2:
# 
# 
# Input: source = "abc", target = "acdbc"
# Output: -1
# Explanation: The target string cannot be constructed from the subsequences of
# source string due to the character "d" in target string.
# 
# 
# Example 3:
# 
# 
# Input: source = "xyz", target = "xzyxz"
# Output: 3
# Explanation: The target string can be constructed as follows "xz" + "y" +
# "xz".
# 
# 
# 
# Constraints:
# 
# 
# 1 <= source.length, target.length <= 1000
# source and target consist of lowercase English letters.
# 
# 
#

# @lc code=start
from bisect import bisect_right
from collections import defaultdict


class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        positions = defaultdict(list)
        for index, char in enumerate(source):
            positions[char].append(index)

        subsequences = 1
        current_index = -1

        for char in target:
            if char not in positions:
                return -1

            indexes = positions[char]
            next_position = bisect_right(indexes, current_index)

            if next_position == len(indexes):
                subsequences += 1
                current_index = indexes[0]
            else:
                current_index = indexes[next_position]

        return subsequences
# @lc code=end

"""
Interview Explanation

Core idea:
Build each subsequence greedily by taking as many target characters as possible
from left to right in source. When the next target character cannot appear
after the current source index, start a new subsequence.

Algorithm:
1. Precompute sorted source indices for each character.
2. Track current_index, the last source index used in the current subsequence.
3. For each target character, binary search for its first source occurrence
   greater than current_index.
4. If found, use it.
5. If not found, start a new subsequence and use that character's first source
   occurrence.
6. If a target character never appears in source, return -1.

Data structure choice:
The character-to-indices map plus binary search avoids repeatedly rescanning
source. It is also easy to explain: every lookup asks for the next usable
occurrence of a character.

Correctness:
For a fixed subsequence, using the earliest possible source occurrence for each
target character leaves the most room for future characters, so it can never be
worse than choosing a later occurrence. A new subsequence is necessary exactly
when no occurrence exists after current_index. Therefore the greedy process
starts a new subsequence only when forced and produces the minimum count.

Complexity:
Preprocessing is O(|source|). Each target character performs a binary search
among occurrences, so time is O(|target| log |source|). Space is O(|source|).

Tests and edge cases:
- Missing character in target returns -1.
- target already a subsequence of source returns 1.
- Repeated wraparounds, such as source "xyz", target "xzyxz", return 3.
- Repeated source characters are handled by the occurrence lists.
"""
