#
# @lc app=leetcode id=3023 lang=python3
#
# [3023] Find Pattern in Infinite Stream I
#
# https://leetcode.com/problems/find-pattern-in-infinite-stream-i/description/
#
# algorithms
# Medium (57.67%)
# Likes:    15
# Dislikes: 2
# Total Accepted:    2.1K
# Total Submissions: 3.6K
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
# 1 <= pattern.length <= 100
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
        Find the first index where pattern occurs in a one-pass bit stream.
        Pattern length <= 100, so classic KMP streaming match is enough.

        Algorithm:
        - Build LPS for pattern. Read bits one-by-one; advance KMP state j.
        - On full match (j == m), return current_index - m + 1.

        Complexity: O(L + m) time for stream prefix length L, O(m) space.
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
