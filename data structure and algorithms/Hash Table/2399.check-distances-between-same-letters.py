#
# @lc app=leetcode id=2399 lang=python3
#
# [2399] Check Distances Between Same Letters
#
# https://leetcode.com/problems/check-distances-between-same-letters/description/
#
# algorithms
# Easy (71.44%)
# Likes:    534
# Dislikes: 73
# Total Accepted:    66.1K
# Total Submissions: 92.5K
# Testcase Example:  "\"abaccb\"\n[1,3,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]"
#
# You are given a 0-indexed string s consisting of only lowercase English
# letters, where each letter in s appears exactly twice. You are also given a
# 0-indexed integer array distance of length 26.
#
# Each letter in the alphabet is numbered from 0 to 25 (i.e. 'a' -> 0, 'b' -> 1,
# 'c' -> 2, ... , 'z' -> 25).
#
# In a well-spaced string, the number of letters between the two occurrences of
# the i^th letter is distance[i]. If the i^th letter does not appear in s, then
# distance[i] can be ignored.
#
# Return true if s is a well-spaced string, otherwise return false.
#
#
#
# Example 1:
#
# Input: s = "abaccb", distance =
# [1,3,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# Output: true
# Explanation:
# - 'a' appears at indices 0 and 2 so it satisfies distance[0] = 1.
# - 'b' appears at indices 1 and 5 so it satisfies distance[1] = 3.
# - 'c' appears at indices 3 and 4 so it satisfies distance[2] = 0.
# Note that distance[3] = 5, but since 'd' does not appear in s, it can be
# ignored.
# Return true because s is a well-spaced string.
#
# Example 2:
#
# Input: s = "aa", distance =
# [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# Output: false
# Explanation:
# - 'a' appears at indices 0 and 1 so there are zero letters between them.
# Because distance[0] = 1, s is not a well-spaced string.
#
#
#
# Constraints:
#
#
# 2 <= s.length <= 52
#
#
# s consists only of lowercase English letters.
#
#
# Each letter appears in s exactly twice.
#
#
# distance.length == 26
#
#
# 0 <= distance[i] <= 50
#

# @lc code=start

from typing import List


class Solution:
    def checkDistances(self, s: str, distance: List[int]) -> bool:
        """
        Interview explanation:
        Each letter appears exactly twice. Between the two occurrences of
        letter c there should be exactly distance[c-'a'] characters.

        Algorithm:
        - Record first index of each letter; on second, verify gap-1 == distance.

        Complexity: O(n) time, O(1) space.
        """
        first = [-1] * 26
        for i, ch in enumerate(s):
            idx = ord(ch) - 97
            if first[idx] == -1:
                first[idx] = i
            else:
                if i - first[idx] - 1 != distance[idx]:
                    return False
        return True
# @lc code=end
