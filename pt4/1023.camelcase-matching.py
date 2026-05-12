#
# @lc app=leetcode id=1023 lang=python3
#
# [1023] Camelcase Matching
#
# https://leetcode.com/problems/camelcase-matching/description/
#
# algorithms
# Medium (65.29%)
# Likes:    986
# Dislikes: 350
# Total Accepted:    65.5K
# Total Submissions: 100.2K
# Testcase Example:  '["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"]\n"FB"'
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
# 
# Example 1:
# 
# 
# Input: queries =
# ["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], pattern =
# "FB"
# Output: [true,false,true,true,false]
# Explanation: "FooBar" can be generated like this "F" + "oo" + "B" + "ar".
# "FootBall" can be generated like this "F" + "oot" + "B" + "all".
# "FrameBuffer" can be generated like this "F" + "rame" + "B" + "uffer".
# 
# 
# Example 2:
# 
# 
# Input: queries =
# ["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], pattern =
# "FoBa"
# Output: [true,false,true,false,false]
# Explanation: "FooBar" can be generated like this "Fo" + "o" + "Ba" + "r".
# "FootBall" can be generated like this "Fo" + "ot" + "Ba" + "ll".
# 
# 
# Example 3:
# 
# 
# Input: queries =
# ["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], pattern =
# "FoBaT"
# Output: [false,true,false,false,false]
# Explanation: "FooBarTest" can be generated like this "Fo" + "o" + "Ba" + "r"
# + "T" + "est".
# 
# 
# 
# Constraints:
# 
# 
# 1 <= pattern.length, queries.length <= 100
# 1 <= queries[i].length <= 100
# queries[i] and pattern consist of English letters.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def camelMatch(self, queries: List[str], pattern: str) -> List[bool]:
        def matches(query: str) -> bool:
            pattern_index = 0

            for char in query:
                if pattern_index < len(pattern) and char == pattern[pattern_index]:
                    pattern_index += 1
                elif char.isupper():
                    return False

            return pattern_index == len(pattern)

        return [matches(query) for query in queries]
# @lc code=end

"""
Interview Explanation

Core idea:
A matching query is the pattern with extra lowercase letters inserted anywhere.
So while scanning the query, uppercase letters are strict: every uppercase
letter must be consumed by the pattern at that position in the pattern order.
Extra lowercase letters can be ignored.

Algorithm:
For each query, keep a pointer into pattern.
- If the current query character equals pattern[p], consume it.
- Otherwise, if the query character is uppercase, the query cannot match.
- Otherwise it is an inserted lowercase character, so skip it.
At the end, every pattern character must have been consumed.

Data structure choice:
Only a pointer is needed because matching is order-based. A trie or regex would
add complexity without improving the asymptotic behavior for these constraints.

Correctness:
The scan accepts exactly the characters that can come from the original pattern
and ignores only lowercase insertions, which are the only allowed insertions.
If an unmatched uppercase character appears, it could not have been inserted,
so rejecting is necessary. If the pattern pointer reaches the end, all required
pattern characters appeared in order; otherwise the query is missing at least
one required character.

Complexity:
Let T be the total length of all queries. Time is O(T), and extra space is
O(1) besides the returned answer list.

Tests and edge cases:
- Pattern has length 1: all extra lowercase letters are allowed around it.
- Query has extra uppercase letters: must return False.
- Query equals pattern exactly: True.
- Query contains all pattern letters but in the wrong order: pointer will not
  consume the whole pattern, so False.
"""
