#
# @lc app=leetcode id=3037 lang=python3
#
# [3037] Find Pattern in Infinite Stream II
#
# https://leetcode.com/problems/find-pattern-in-infinite-stream-ii/description/
#
# algorithms
# Hard (67.81%)
# Likes:    7
# Dislikes: 3
# Total Accepted:    1.5K
# Total Submissions: 2.2K
# Testcase Example:  "[1,1,1,0,1]\n[0,1]"
#
#
# You are given a binary array pattern and an object stream of class
# InfiniteStream representing a 0-indexed infinite stream of bits.
#
# The class InfiniteStream contains the following function:
#
# int next(): Reads a single bit (which is either 0 or 1) from the stream
# and returns it.
#
# Return the first starting index where the pattern matches the bits read
# from the stream. For example, if the pattern is [1, 0], the first match
# is the highlighted part in the stream [0, 1, 0, 1, ...].
#
# Example 1:
#
# Input: stream = [1,1,1,0,1,1,1,...], pattern = [0,1]
# Output: 3
# Explanation: The first occurrence of the pattern [0,1] is highlighted in
# the stream [1,1,1,0,1,...], which starts at index 3.
#
# Example 2:
#
# Input: stream = [0,0,0,0,...], pattern = [0]
# Output: 0
# Explanation: The first occurrence of the pattern [0] is highlighted in
# the stream [0,...], which starts at index 0.
#
# Example 3:
#
# Input: stream = [1,0,1,1,0,1,1,0,1,...], pattern = [1,1,0,1]
# Output: 2
# Explanation: The first occurrence of the pattern [1,1,0,1] is
# highlighted in the stream [1,0,1,1,0,1,...], which starts at index 2.
#
# Constraints:
#
# 1 <= pattern.length <= 10^4
#
# pattern consists only of 0 and 1.
#
# stream consists only of 0 and 1.
#
# The input is generated such that the pattern's start index exists in the
# first 10^5 bits of the stream.
#

# @lc code=start

from typing import List, Optional


# Definition for an infinite stream.
# class InfiniteStream:
#     def next(self) -> int:
#         pass
class Solution:
    def findPattern(self, stream: Optional["InfiniteStream"], pattern: List[int]) -> int:
        """
        Interview explanation:
        Same streaming pattern search as part I, but pattern length up to 1e4.
        KMP still reads each stream bit once.

        Algorithm:
        - LPS on pattern; stream bits through the KMP automaton until match.
        - Return start index idx - m + 1.

        Complexity: O(L + m) time, O(m) space (L = match end index).
        """
        m = len(pattern)
        lps = [0] * m
        length = 0
        i = 1
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            elif length:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

        idx = 0
        j = 0
        while True:
            bit = stream.next()
            while j and bit != pattern[j]:
                j = lps[j - 1]
            if bit == pattern[j]:
                j += 1
                if j == m:
                    return idx - m + 1
            idx += 1
# @lc code=end
