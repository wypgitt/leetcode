#
# @lc app=leetcode id=3437 lang=python3
#
# [3437] Permutations III
#
# https://leetcode.com/problems/permutations-iii/description/
#
# algorithms
# Medium (85.85%)
# Likes:    17
# Dislikes: 2
# Total Accepted:    3.4K
# Total Submissions: 4K
# Testcase Example:  "4"
#
#
# Given an integer n, an alternating permutation is a permutation of the
# first n positive integers such that no two adjacent elements are both
# odd or both even.
#
# Return all such alternating permutations sorted in lexicographical
# order.
#
# Example 1:
#
# Input: n = 4
#
# Output:
# [[1,2,3,4],[1,4,3,2],[2,1,4,3],[2,3,4,1],[3,2,1,4],[3,4,1,2],[4,1,2,3],[4,3,2,1]]
#
# Example 2:
#
# Input: n = 2
#
# Output: [[1,2],[2,1]]
#
# Example 3:
#
# Input: n = 3
#
# Output: [[1,2,3],[3,2,1]]
#
# Constraints:
#
# 1 <= n <= 10
#

# @lc code=start
from typing import List


class Solution:
    def permute(self, n: int) -> List[List[int]]:
        """
        Interview explanation:
        Alternating permutations of 1..n: adjacent values must have opposite
        parity. Backtrack in increasing candidate order for lexicographic output.

        Algorithm:
        - DFS with used mask; skip candidates with same parity as previous.
        - Collect complete paths.

        Complexity: O(n! * n) time worst-case, O(n) recursion space.
        """
        ans: List[List[int]] = []
        used = [False] * (n + 1)

        def dfs(path: List[int]) -> None:
            if len(path) == n:
                ans.append(path[:])
                return
            for x in range(1, n + 1):
                if used[x]:
                    continue
                if path and (path[-1] % 2) == (x % 2):
                    continue
                used[x] = True
                path.append(x)
                dfs(path)
                path.pop()
                used[x] = False

        dfs([])
        return ans
# @lc code=end
