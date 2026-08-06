#
# @lc app=leetcode id=1023 lang=python3
#
# [1023] Camelcase Matching
#
# https://leetcode.com/problems/camelcase-matching/description/
#
# algorithms
# Medium (65.77%)
# Likes:    992
# Dislikes: 352
# Total Accepted:    67.7K
# Total Submissions: 103K
# Testcase Example:  "[\"FooBar\",\"FooBarTest\",\"FootBall\",\"FrameBuffer\",\"ForceFeedBack\"]"
#
# Given an array of strings queries and a string pattern, return a boolean
# array answer where answer[i] is true if queries[i] matches pattern, and false
# otherwise.
#
# A query word queries[i] matches pattern if you can insert lowercase English
# letters into the pattern so that it equals the query. You may insert a
# character at any position in pattern or you may choose not to insert any
# characters at all.
#
# Example 1:
#
# Input: queries =
# ["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], pattern =
# "FB"
# Output: [true,false,true,true,false]
# Explanation: "FooBar" can be generated like this "F" + "oo" + "B" + "ar".
# "FootBall" can be generated like this "F" + "oot" + "B" + "all".
# "FrameBuffer" can be generated like this "F" + "rame" + "B" + "uffer".
#
# Example 2:
#
# Input: queries =
# ["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], pattern =
# "FoBa"
# Output: [true,false,true,false,false]
# Explanation: "FooBar" can be generated like this "Fo" + "o" + "Ba" + "r".
# "FootBall" can be generated like this "Fo" + "ot" + "Ba" + "ll".
#
# Example 3:
#
# Input: queries =
# ["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], pattern =
# "FoBaT"
# Output: [false,true,false,false,false]
# Explanation: "FooBarTest" can be generated like this "Fo" + "o" + "Ba" + "r"
# + "T" + "est".
#
# Constraints:
#
# 1 <= pattern.length, queries.length <= 100
#
# 1 <= queries[i].length <= 100
#
# queries[i] and pattern consist of English letters.
#

# @lc code=start
from typing import List


class Solution:
    def camelMatch(self, queries: List[str], pattern: str) -> List[bool]:
        """
        Interview explanation:
        Two-pointer match: pattern uppercase letters must appear in order in the
        query; extra lowercase letters in query are OK; any extra uppercase in
        query that is not next in pattern fails.

        Algorithm:
        - For each query: j=0 over pattern
          for ch in query: if j<len and ch==pattern[j]: j++; elif ch.isupper(): fail
          success if j==len(pattern)

        Complexity: O(Q * L) time, O(1) extra space.
        """
        def match(q: str) -> bool:
            j = 0
            for ch in q:
                if j < len(pattern) and ch == pattern[j]:
                    j += 1
                elif ch.isupper():
                    return False
            return j == len(pattern)

        return [match(q) for q in queries]
# @lc code=end
