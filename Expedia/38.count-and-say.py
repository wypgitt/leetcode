#
# @lc app=leetcode id=38 lang=python3
#
# [38] Count and Say
#
# https://leetcode.com/problems/count-and-say/description/
#
# algorithms
# Medium (62.81%)
# Likes:    5129
# Dislikes: 9088
# Total Accepted:    1.4M
# Total Submissions: 2.3M
# Testcase Example:  '1'
#
# The count-and-say sequence is a sequence of digit strings defined by the
# recursive formula:
# 
# 
# countAndSay(1) = "1"
# countAndSay(n) is the run-length encoding of countAndSay(n - 1).
# 
# 
# Run-length encoding (RLE) is a string compression method that works by
# replacing consecutive identical characters (repeated 2 or more times) with
# the concatenation of the character and the number marking the count of the
# characters (length of the run). For example, to compress the string "3322251"
# we replace "33" with "23", replace "222" with "32", replace "5" with "15" and
# replace "1" with "11". Thus the compressed string becomes "23321511".
# 
# Given a positive integer n, return the n^th element of the count-and-say
# sequence.
# 
# 
# Example 1:
# 
# 
# Input: n = 4
# 
# Output: "1211"
# 
# Explanation:
# 
# 
# countAndSay(1) = "1"
# countAndSay(2) = RLE of "1" = "11"
# countAndSay(3) = RLE of "11" = "21"
# countAndSay(4) = RLE of "21" = "1211"
# 
# 
# 
# Example 2:
# 
# 
# Input: n = 1
# 
# Output: "1"
# 
# Explanation:
# 
# This is the base case.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 30
# 
# 
# 
# Follow up: Could you solve it iteratively?
#

# @lc code=start
from typing import List, Optional
class Solution:
    def countAndSay(self, n: int) -> str:
        """
        Interview explanation:
        Each term is a run-length encoding of the previous term: count adjacent
        equal digits and say "count then digit". Iteration is clearer than
        recursion and avoids repeated stack frames.

        Edge cases and tests:
        - n=1 returns "1".
        - Runs with length greater than 1, e.g. "11" -> "21".
        - Multiple runs in a term, e.g. "1211" -> "111221".

        Complexity: O(total generated length) time and O(current term length)
        space; each iteration scans the previous term once.
        """
        term = '1'
        for _ in range(n - 1):
            parts = []
            i = 0
            while i < len(term):
                j = i
                while j < len(term) and term[j] == term[i]:
                    j += 1
                parts.append(str(j - i))
                parts.append(term[i])
                i = j
            term = ''.join(parts)
        return term
# @lc code=end


