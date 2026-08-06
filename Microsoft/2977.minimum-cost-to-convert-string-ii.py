#
# @lc app=leetcode id=2977 lang=python3
#
# [2977] Minimum Cost to Convert String II
#
# https://leetcode.com/problems/minimum-cost-to-convert-string-ii/description/
#
# algorithms
# Hard (59.54%)
# Likes:    394
# Dislikes: 116
# Total Accepted:    65.9K
# Total Submissions: 110.7K
# Testcase Example:  "\"abcd\"\n\"acbe\"\n[\"a\",\"b\",\"c\",\"c\",\"e\",\"d\"]\n[\"b\",\"c\",\"b\",\"e\",\"b\",\"e\"]\n[2,5,5,1,2,20]"
#
#
# You are given two 0-indexed strings source and target, both of length n
# and consisting of lowercase English characters. You are also given two
# 0-indexed string arrays original and changed, and an integer array cost,
# where cost[i] represents the cost of converting the string original[i]
# to the string changed[i].
#
# You start with the string source. In one operation, you can pick a
# substring x from the string, and change it to y at a cost of z if there
# exists any index j such that cost[j] == z, original[j] == x, and
# changed[j] == y. You are allowed to do any number of operations, but any
# pair of operations must satisfy either of these two conditions:
#
# The substrings picked in the operations are source[a..b] and
# source[c..d] with either b < c or d < a. In other words, the indices
# picked in both operations are disjoint.
#
# The substrings picked in the operations are source[a..b] and
# source[c..d] with a == c and b == d. In other words, the indices picked
# in both operations are identical.
#
# Return the minimum cost to convert the string source to the string
# target using any number of operations. If it is impossible to convert
# source to target, return -1.
#
# Note that there may exist indices i, j such that original[j] ==
# original[i] and changed[j] == changed[i].
#
# Example 1:
#
# Input: source = "abcd", target = "acbe", original =
# ["a","b","c","c","e","d"], changed = ["b","c","b","e","b","e"], cost =
# [2,5,5,1,2,20]
# Output: 28
# Explanation: To convert "abcd" to "acbe", do the following operations:
# - Change substring source[1..1] from "b" to "c" at a cost of 5.
# - Change substring source[2..2] from "c" to "e" at a cost of 1.
# - Change substring source[2..2] from "e" to "b" at a cost of 2.
# - Change substring source[3..3] from "d" to "e" at a cost of 20.
# The total cost incurred is 5 + 1 + 2 + 20 = 28.
# It can be shown that this is the minimum possible cost.
#
# Example 2:
#
# Input: source = "abcdefgh", target = "acdeeghh", original =
# ["bcd","fgh","thh"], changed = ["cde","thh","ghh"], cost = [1,3,5]
# Output: 9
# Explanation: To convert "abcdefgh" to "acdeeghh", do the following
# operations:
# - Change substring source[1..3] from "bcd" to "cde" at a cost of 1.
# - Change substring source[5..7] from "fgh" to "thh" at a cost of 3. We
# can do this operation because indices [5,7] are disjoint with indices
# picked in the first operation.
# - Change substring source[5..7] from "thh" to "ghh" at a cost of 5. We
# can do this operation because indices [5,7] are disjoint with indices
# picked in the first operation, and identical with indices picked in the
# second operation.
# The total cost incurred is 1 + 3 + 5 = 9.
# It can be shown that this is the minimum possible cost.
#
# Example 3:
#
# Input: source = "abcdefgh", target = "addddddd", original =
# ["bcd","defgh"], changed = ["ddd","ddddd"], cost = [100,1578]
# Output: -1
# Explanation: It is impossible to convert "abcdefgh" to "addddddd".
# If you select substring source[1..3] as the first operation to change
# "abcdefgh" to "adddefgh", you cannot select substring source[3..7] as
# the second operation because it has a common index, 3, with the first
# operation.
# If you select substring source[3..7] as the first operation to change
# "abcdefgh" to "abcddddd", you cannot select substring source[1..3] as
# the second operation because it has a common index, 3, with the first
# operation.
#
# Constraints:
#
# 1 <= source.length == target.length <= 1000
#
# source, target consist only of lowercase English characters.
#
# 1 <= cost.length == original.length == changed.length <= 100
#
# 1 <= original[i].length == changed[i].length <= source.length
#
# original[i], changed[i] consist only of lowercase English characters.
#
# original[i] != changed[i]
#
# 1 <= cost[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def minimumCost(
        self,
        source: str,
        target: str,
        original: List[str],
        changed: List[str],
        cost: List[int],
    ) -> int:
        """
        Interview explanation:
        Like 2976 but operations replace equal-length substrings; ops on a span may
        chain, and different spans must be disjoint.

        Algorithm:
        - Map all distinct strings in original/changed to ids; Floyd-Warshall on those
          nodes for substring conversion costs.
        - DP: dp[i] = min cost to convert source[:i] → target[:i]. Transition: match
          next char for free if equal; or replace source[i:i+L]→target[i:i+L] using
          precomputed dist if both strings appear in the map.

        Complexity: O(m^3 + n^2 + n·Σ|ops|) roughly; m <= 200 unique strings, n <= 1000.
        """
        INF = 10**18
        nodes = {}
        for s in original + changed:
            if s not in nodes:
                nodes[s] = len(nodes)
        m = len(nodes)
        dist = [[INF] * m for _ in range(m)]
        for i in range(m):
            dist[i][i] = 0
        for a, b, c in zip(original, changed, cost):
            u, v = nodes[a], nodes[b]
            dist[u][v] = min(dist[u][v], c)
        for k in range(m):
            for i in range(m):
                dik = dist[i][k]
                if dik == INF:
                    continue
                for j in range(m):
                    dist[i][j] = min(dist[i][j], dik + dist[k][j])

        lengths = sorted({len(s) for s in nodes})
        n = len(source)
        dp = [INF] * (n + 1)
        dp[0] = 0
        for i in range(n):
            if dp[i] == INF:
                continue
            if source[i] == target[i]:
                dp[i + 1] = min(dp[i + 1], dp[i])
            for L in lengths:
                j = i + L
                if j > n:
                    break
                a = source[i:j]
                b = target[i:j]
                if a not in nodes or b not in nodes:
                    continue
                d = dist[nodes[a]][nodes[b]]
                if d < INF:
                    dp[j] = min(dp[j], dp[i] + d)
        return -1 if dp[n] >= INF else dp[n]
# @lc code=end
