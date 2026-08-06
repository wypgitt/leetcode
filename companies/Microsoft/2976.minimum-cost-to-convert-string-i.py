#
# @lc app=leetcode id=2976 lang=python3
#
# [2976] Minimum Cost to Convert String I
#
# https://leetcode.com/problems/minimum-cost-to-convert-string-i/description/
#
# algorithms
# Medium (63.02%)
# Likes:    1356
# Dislikes: 94
# Total Accepted:    198K
# Total Submissions: 314.1K
# Testcase Example:  "\"abcd\"\n\"acbe\"\n[\"a\",\"b\",\"c\",\"c\",\"e\",\"d\"]\n[\"b\",\"c\",\"b\",\"e\",\"b\",\"e\"]\n[2,5,5,1,2,20]"
#
#
# You are given two 0-indexed strings source and target, both of length n
# and consisting of lowercase English letters. You are also given two
# 0-indexed character arrays original and changed, and an integer array
# cost, where cost[i] represents the cost of changing the character
# original[i] to the character changed[i].
#
# You start with the string source. In one operation, you can pick a
# character x from the string and change it to the character y at a cost
# of z if there exists any index j such that cost[j] == z, original[j] ==
# x, and changed[j] == y.
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
# Explanation: To convert the string "abcd" to string "acbe":
# - Change value at index 1 from 'b' to 'c' at a cost of 5.
# - Change value at index 2 from 'c' to 'e' at a cost of 1.
# - Change value at index 2 from 'e' to 'b' at a cost of 2.
# - Change value at index 3 from 'd' to 'e' at a cost of 20.
# The total cost incurred is 5 + 1 + 2 + 20 = 28.
# It can be shown that this is the minimum possible cost.
#
# Example 2:
#
# Input: source = "aaaa", target = "bbbb", original = ["a","c"], changed =
# ["c","b"], cost = [1,2]
# Output: 12
# Explanation: To change the character 'a' to 'b' change the character 'a'
# to 'c' at a cost of 1, followed by changing the character 'c' to 'b' at
# a cost of 2, for a total cost of 1 + 2 = 3. To change all occurrences of
# 'a' to 'b', a total cost of 3 * 4 = 12 is incurred.
#
# Example 3:
#
# Input: source = "abcd", target = "abce", original = ["a"], changed =
# ["e"], cost = [10000]
# Output: -1
# Explanation: It is impossible to convert source to target because the
# value at index 3 cannot be changed from 'd' to 'e'.
#
# Constraints:
#
# 1 <= source.length == target.length <= 10^5
#
# source, target consist of lowercase English letters.
#
# 1 <= cost.length == original.length == changed.length <= 2000
#
# original[i], changed[i] are lowercase English letters.
#
# 1 <= cost[i] <= 10^6
#
# original[i] != changed[i]
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
        Change characters with given directed costs (and chains). Min cost source→target.

        Algorithm:
        - Build 26×26 graph of min direct costs; Floyd-Warshall all-pairs. Sum dist[s][t]
          per position (0 if equal); impossible if any INF.

        Complexity: O(26^3 + n + m) time, O(1) extra (26×26).
        """
        INF = 10**18
        dist = [[INF] * 26 for _ in range(26)]
        for i in range(26):
            dist[i][i] = 0
        for a, b, c in zip(original, changed, cost):
            u, v = ord(a) - 97, ord(b) - 97
            dist[u][v] = min(dist[u][v], c)
        for k in range(26):
            for i in range(26):
                dik = dist[i][k]
                if dik == INF:
                    continue
                for j in range(26):
                    dist[i][j] = min(dist[i][j], dik + dist[k][j])
        ans = 0
        for s, t in zip(source, target):
            if s == t:
                continue
            d = dist[ord(s) - 97][ord(t) - 97]
            if d == INF:
                return -1
            ans += d
        return ans
# @lc code=end
