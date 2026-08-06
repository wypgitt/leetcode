#
# @lc app=leetcode id=1923 lang=python3
#
# [1923] Longest Common Subpath
#
# https://leetcode.com/problems/longest-common-subpath/description/
#
# algorithms
# Hard (30.14%)
# Likes:    522
# Dislikes: 39
# Total Accepted:    10.9K
# Total Submissions: 36.3K
# Testcase Example:  "5"
#
# There is a country of n cities numbered from 0 to n - 1. In this country,
# there is a road connecting every pair of cities.
#
# There are m friends numbered from 0 to m - 1 who are traveling through the
# country. Each one of them will take a path consisting of some cities. Each
# path is represented by an integer array that contains the visited cities in
# order. The path may contain a city more than once, but the same city will not
# be listed consecutively.
#
# Given an integer n and a 2D integer array paths where paths[i] is an integer
# array representing the path of the i^th friend, return the length of the
# longest common subpath that is shared by every friend's path, or 0 if there
# is no common subpath at all.
#
# A subpath of a path is a contiguous sequence of cities within that path.
#
# Example 1:
#
# Input: n = 5, paths = [[0,1,2,3,4],
# [2,3,4],
# [4,0,1,2,3]]
# Output: 2
# Explanation: The longest common subpath is [2,3].
#
# Example 2:
#
# Input: n = 3, paths = [[0],[1],[2]]
# Output: 0
# Explanation: There is no common subpath shared by the three paths.
#
# Example 3:
#
# Input: n = 5, paths = [[0,1,2,3,4],
# [4,3,2,1,0]]
# Output: 1
# Explanation: The possible longest common subpaths are [0], [1], [2], [3], and
# [4]. All have a length of 1.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# m == paths.length
#
# 2 <= m <= 10^5
#
# sum(paths[i].length) <= 10^5
#
# 0 <= paths[i][j] < n
#
# The same city is not listed multiple times consecutively in paths[i].
#

# @lc code=start
from typing import List


class Solution:
    def longestCommonSubpath(self, n: int, paths: List[List[int]]) -> int:
        """
        Interview explanation:
        Longest common contiguous subpath across all paths. Binary search length L;
        rolling hash all L-windows of each path; intersect hash sets.

        Algorithm:
        - Dual mod hashes to reduce collisions. Check(L): hashes of path0 ∩ ... ∩ last.

        Complexity: O(P log L * α) where P = total path length.
        """
        MOD1, MOD2 = 1_000_000_007, 1_000_000_009
        BASE1, BASE2 = 100003, 100019
        m = len(paths)

        def window_hashes(path: List[int], L: int):
            h1 = h2 = 0
            for i in range(L):
                h1 = (h1 * BASE1 + path[i] + 1) % MOD1
                h2 = (h2 * BASE2 + path[i] + 1) % MOD2
            seen = {(h1, h2)}
            p1 = pow(BASE1, L - 1, MOD1)
            p2 = pow(BASE2, L - 1, MOD2)
            for i in range(L, len(path)):
                h1 = (h1 - (path[i - L] + 1) * p1) % MOD1
                h2 = (h2 - (path[i - L] + 1) * p2) % MOD2
                h1 = (h1 * BASE1 + path[i] + 1) % MOD1
                h2 = (h2 * BASE2 + path[i] + 1) % MOD2
                seen.add((h1, h2))
            return seen

        def check(L: int) -> bool:
            if L == 0:
                return True
            if any(len(p) < L for p in paths):
                return False
            common = window_hashes(paths[0], L)
            for path in paths[1:]:
                common &= window_hashes(path, L)
                if not common:
                    return False
            return True

        lo, hi = 0, min(map(len, paths))
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if check(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
