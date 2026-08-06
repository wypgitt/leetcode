#
# @lc app=leetcode id=555 lang=python3
#
# [555] Split Concatenated Strings
#
# https://leetcode.com/problems/split-concatenated-strings/description/
#
# algorithms
# Medium (43.55%)
# Likes:    80
# Dislikes: 265
# Total Accepted:    7.5K
# Total Submissions: 17.3K
# Testcase Example:  '["abc","xyz"]'
#
# You are given an array of strings strs. You could concatenate these strings
# together into a loop, where for each string, you could choose to reverse it
# or not. Among all the possible loops
# 
# Return the lexicographically largest string after cutting the loop, which
# will make the looped string into a regular one.
# 
# Specifically, to find the lexicographically largest string, you need to
# experience two phases:
# 
# 
# Concatenate all the strings into a loop, where you can reverse some strings
# or not and connect them in the same order as given.
# Cut and make one breakpoint in any place of the loop, which will make the
# looped string into a regular one starting from the character at the
# cutpoint.
# 
# 
# And your job is to find the lexicographically largest one among all the
# possible regular strings.
# 
# 
# Example 1:
# 
# 
# Input: strs = ["abc","xyz"]
# Output: "zyxcba"
# Explanation: You can get the looped string "-abcxyz-", "-abczyx-",
# "-cbaxyz-", "-cbazyx-", where '-' represents the looped status. 
# The answer string came from the fourth looped one, where you could cut from
# the middle character 'a' and get "zyxcba".
# 
# 
# Example 2:
# 
# 
# Input: strs = ["abc"]
# Output: "cba"
# 
# 
# 
# Constraints:
# 
# 
# 1 <= strs.length <= 1000
# 1 <= strs[i].length <= 1000
# 1 <= sum(strs[i].length) <= 1000
# strs[i] consists of lowercase English letters.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def splitLoopedString(self, strs: List[str]) -> str:
        parts = [max(s, s[::-1]) for s in strs]
        best = ''
        for i, original in enumerate(strs):
            middle = ''.join(parts[i + 1:] + parts[:i])
            for candidate_source in (original, original[::-1]):
                for cut in range(len(candidate_source)):
                    candidate = candidate_source[cut:] + middle + candidate_source[:cut]
                    if candidate > best:
                        best = candidate
        return best
# @lc code=end

"""
Interview explanation:
For every string that is not cut, independently choose the larger of the string and its reverse, because its internal orientation is fixed in the final concatenation. Then try every possible split point in every possible orientation of the one string that crosses the final start/end boundary.

Data structure: a list of best orientations keeps the fixed contribution of all non-boundary strings.

Edge cases: the boundary string must be tried in both original and reversed forms; using only its locally larger form can miss the global optimum after cutting.

Complexity: if total length is L, building candidates naively is O(L^2) in the worst case. This is accepted for the original constraints. Extra space is O(L) for candidate strings.
"""
