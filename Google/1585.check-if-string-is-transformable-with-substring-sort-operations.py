#
# @lc app=leetcode id=1585 lang=python3
#
# [1585] Check If String Is Transformable With Substring Sort Operations
#
# https://leetcode.com/problems/check-if-string-is-transformable-with-substring-sort-operations/description/
#
# algorithms
# Hard (51.59%)
# Likes:    459
# Dislikes: 11
# Total Accepted:    13.3K
# Total Submissions: 25.8K
# Testcase Example:  "\"84532\""
#
# Given two strings s and t, transform string s into string t using the
# following operation any number of times:
#
# Choose a non-empty substring in s and sort it in place so the characters are
# in ascending order.
#
# For example, applying the operation on the underlined substring in "14234"
# results in "12344".
#
# Return true if it is possible to transform s into t. Otherwise, return false.
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: s = "84532", t = "34852"
# Output: true
# Explanation: You can transform s into t using the following sort operations:
# "84532" (from index 2 to 3) -> "84352"
# "84352" (from index 0 to 2) -> "34852"
#
# Example 2:
#
# Input: s = "34521", t = "23415"
# Output: true
# Explanation: You can transform s into t using the following sort operations:
# "34521" -> "23451"
# "23451" -> "23415"
#
# Example 3:
#
# Input: s = "12345", t = "12435"
# Output: false
#
# Constraints:
#
# s.length == t.length
#
# 1 <= s.length <= 10^5
#
# s and t consist of only digits.
#

# @lc code=start
from collections import deque


class Solution:
    def isTransformable(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Sorting any substring means digits can bubble left past larger digits
        only. t is reachable iff for each digit in order, its position in s is
        not blocked by a smaller digit still to its left that should appear
        later — equivalently: for each char of t, take the next occurrence in
        s; no smaller digit may have an unused occurrence before that index.

        Algorithm (queues of positions):
        - pos[d] = deque of indices where s has digit d.
        - For each ch in t: d=int(ch); if pos[d] empty False; i=popleft;
          for smaller x in 0..d-1: if pos[x] and pos[x][0] < i: False.

        Complexity: O(n * 10) time, O(n) space.
        """
        pos = [deque() for _ in range(10)]
        for i, ch in enumerate(s):
            pos[int(ch)].append(i)
        for ch in t:
            d = int(ch)
            if not pos[d]:
                return False
            i = pos[d].popleft()
            for x in range(d):
                if pos[x] and pos[x][0] < i:
                    return False
        return True
# @lc code=end

