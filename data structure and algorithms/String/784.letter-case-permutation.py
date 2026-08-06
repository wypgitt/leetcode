#
# @lc app=leetcode id=784 lang=python3
#
# [784] Letter Case Permutation
#
# https://leetcode.com/problems/letter-case-permutation/description/
#
# algorithms
# Medium (76.0%)
# Likes:    4866
# Dislikes: 162
# Total Accepted:    382K
# Total Submissions: 503K
# Testcase Example:  "\"a1b2\""
#
# Given a string s, you can transform every letter individually to be lowercase
# or uppercase to create another string.
#
# Return a list of all possible strings we could create. Return the output in
# any order.
#
# Example 1:
#
# Input: s = "a1b2"
# Output: ["a1b2","a1B2","A1b2","A1B2"]
#
# Example 2:
#
# Input: s = "3z4"
# Output: ["3z4","3Z4"]
#
# Constraints:
#
# 1 <= s.length <= 12
#
# s consists of lowercase English letters, uppercase English letters, and
# digits.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def letterCasePermutation(self, s: str) -> List[str]:
        """
        Interview explanation:
        For each letter, choose lower or upper case; digits stay fixed.
        Backtracking builds all 2^{letter_count} strings.

        Algorithm:
        - DFS index i: if digit, take as-is; if letter, branch lower and upper.
        - Collect completed strings.

        Complexity: O(n * 2^L) time/space (L = #letters).
        """
        s = list(s)
        n = len(s)
        res: List[str] = []

        def dfs(i: int) -> None:
            if i == n:
                res.append("".join(s))
                return
            if s[i].isdigit():
                dfs(i + 1)
            else:
                s[i] = s[i].lower()
                dfs(i + 1)
                s[i] = s[i].upper()
                dfs(i + 1)

        dfs(0)
        return res

    def letterCasePermutation_bfs(self, s: str) -> List[str]:
        """
        Interview explanation:
        Alternate: BFS/level build — start with [""]; for each char, extend
        all current strings (two ways if letter).

        Algorithm:
        - q=[""]; for ch in s: for each cur in level, append lower/upper or digit.
        - Return list(q).

        Complexity: O(n * 2^L) time/space.
        """
        q = deque([""])
        for ch in s:
            sz = len(q)
            for _ in range(sz):
                cur = q.popleft()
                if ch.isalpha():
                    q.append(cur + ch.lower())
                    q.append(cur + ch.upper())
                else:
                    q.append(cur + ch)
        return list(q)
# @lc code=end

