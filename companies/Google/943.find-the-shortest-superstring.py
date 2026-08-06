#
# @lc app=leetcode id=943 lang=python3
#
# [943] Find the Shortest Superstring
#
# https://leetcode.com/problems/find-the-shortest-superstring/description/
#
# algorithms
# Hard (45.61%)
# Likes:    1533
# Dislikes: 152
# Total Accepted:    36.9K
# Total Submissions: 80.9K
# Testcase Example:  "[\"alex\",\"loves\",\"leetcode\"]"
#
# Given an array of strings words, return the smallest string that contains
# each string in words as a substring. If there are multiple valid strings of
# the smallest length, return any of them.
#
# You may assume that no string in words is a substring of another string in
# words.
#
# Example 1:
#
# Input: words = ["alex","loves","leetcode"]
# Output: "alexlovesleetcode"
# Explanation: All permutations of "alex","loves","leetcode" would also be
# accepted.
#
# Example 2:
#
# Input: words = ["catg","ctaagt","gcta","ttca","atgcatc"]
# Output: "gctaagttcatgcatc"
#
# Constraints:
#
# 1 <= words.length <= 12
#
# 1 <= words[i].length <= 20
#
# words[i] consists of lowercase English letters.
#
# All the strings of words are unique.
#

# @lc code=start
from typing import List


class Solution:
    def shortestSuperstring(self, words: List[str]) -> str:
        """
        Interview explanation:
        Shortest superstring is NP-hard; n<=12 ⇒ TSP-style DP on subsets.
        Precompute overlap[i][j] = max suffix of i matching prefix of j; DP
        state (mask, i) = best path visiting mask ending at i; reconstruct.

        Algorithm (TSP DP):
        - n words; overlap[i][j] for i!=j
        - dp[mask][i] = best string (or parent) for mask ending at i
        - Transition: for j not in mask: append words[j][overlap[i][j]:]
        - Among full masks, pick shortest; reconstruct via parent pointers

        Complexity: O(n^2 * 2^n + n^2 * L) time, O(n * 2^n * L) space strings
        (store parents to reduce space).
        """
        n = len(words)
        overlap = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                a, b = words[i], words[j]
                mx = min(len(a), len(b))
                for k in range(mx, 0, -1):
                    if a.endswith(b[:k]):
                        overlap[i][j] = k
                        break

        N = 1 << n
        dp = [[None] * n for _ in range(N)]
        parent = [[None] * n for _ in range(N)]
        for i in range(n):
            dp[1 << i][i] = words[i]

        for mask in range(N):
            for i in range(n):
                if not (mask & (1 << i)) or dp[mask][i] is None:
                    continue
                for j in range(n):
                    if mask & (1 << j):
                        continue
                    cand = dp[mask][i] + words[j][overlap[i][j]:]
                    nmask = mask | (1 << j)
                    if dp[nmask][j] is None or len(cand) < len(dp[nmask][j]):
                        dp[nmask][j] = cand
                        parent[nmask][j] = i

        full = N - 1
        best = None
        end = 0
        for i in range(n):
            if dp[full][i] is not None and (best is None or len(dp[full][i]) < len(best)):
                best = dp[full][i]
                end = i
        return best
# @lc code=end

