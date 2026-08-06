#
# @lc app=leetcode id=756 lang=python3
#
# [756] Pyramid Transition Matrix
#
# https://leetcode.com/problems/pyramid-transition-matrix/description/
#
# algorithms
# Medium (60.59%)
# Likes:    974
# Dislikes: 552
# Total Accepted:    110K
# Total Submissions: 182K
# Testcase Example:  "\"BCD\""
#
# You are stacking blocks to form a pyramid. Each block has a color, which is
# represented by a single letter. Each row of blocks contains one less block
# than the row beneath it and is centered on top.
#
# To make the pyramid aesthetically pleasing, there are only specific
# triangular patterns that are allowed. A triangular pattern consists of a
# single block stacked on top of two blocks. The patterns are given as a list
# of three-letter strings allowed, where the first two characters of a pattern
# represent the left and right bottom blocks respectively, and the third
# character is the top block.
#
# For example, "ABC" represents a triangular pattern with a 'C' block stacked
# on top of an 'A' (left) and 'B' (right) block. Note that this is different
# from "BAC" where 'B' is on the left bottom and 'A' is on the right bottom.
#
# You start with a bottom row of blocks bottom, given as a single string, that
# you must use as the base of the pyramid.
#
# Given bottom and allowed, return true if you can build the pyramid all the
# way to the top such that every triangular pattern in the pyramid is in
# allowed, or false otherwise.
#
# Example 1:
#
# Input: bottom = "BCD", allowed = ["BCC","CDE","CEA","FFF"]
# Output: true
# Explanation: The allowed triangular patterns are shown on the right.
# Starting from the bottom (level 3), we can build "CE" on level 2 and then
# build "A" on level 1.
# There are three triangular patterns in the pyramid, which are "BCC", "CDE",
# and "CEA". All are allowed.
#
# Example 2:
#
# Input: bottom = "AAAA", allowed = ["AAB","AAC","BCD","BBE","DEF"]
# Output: false
# Explanation: The allowed triangular patterns are shown on the right.
# Starting from the bottom (level 4), there are multiple ways to build level 3,
# but trying all the possibilites, you will get always stuck before building
# level 1.
#
# Constraints:
#
# 2 <= bottom.length <= 6
#
# 0 <= allowed.length <= 216
#
# allowed[i].length == 3
#
# The letters in all input strings are from the set {'A', 'B', 'C', 'D', 'E',
# 'F'}.
#
# All the values of allowed are unique.
#


# @lc code=start
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class Solution:
    def pyramidTransition(self, bottom: str, allowed: List[str]) -> bool:
        """
        Interview explanation:
        Build a pyramid upward: each pair of adjacent blocks can be topped by
        allowed[2]. DFS/backtracking tries all valid next rows; memoize rows
        already proven impossible/possible.

        Algorithm:
        - Map (left,right) -> set of allowed tops
        - dfs(row): if len==1 True; generate all next rows via backtrack on pairs
        - Memoize results for each row string

        Complexity: exponential in worst case; O(A) space for allowed map plus
        recursion/memo on encountered rows.
        """
        triples: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        for a, b, c in allowed:
            triples[(a, b)].add(c)
        memo = {}

        def dfs(row: str) -> bool:
            if len(row) == 1:
                return True
            if row in memo:
                return memo[row]
            n = len(row)

            def build(i: int, path: List[str]) -> bool:
                if i == n - 1:
                    return dfs("".join(path))
                for top in triples.get((row[i], row[i + 1]), ()):
                    path.append(top)
                    if build(i + 1, path):
                        return True
                    path.pop()
                return False

            memo[row] = build(0, [])
            return memo[row]

        return dfs(bottom)
# @lc code=end

