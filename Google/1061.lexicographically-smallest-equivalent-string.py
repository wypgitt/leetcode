#
# @lc app=leetcode id=1061 lang=python3
#
# [1061] Lexicographically Smallest Equivalent String
#
# https://leetcode.com/problems/lexicographically-smallest-equivalent-string/description/
#
# algorithms
# Medium (81.07%)
# Likes:    2900
# Dislikes: 186
# Total Accepted:    186K
# Total Submissions: 229K
# Testcase Example:  "\"parker\""
#
# You are given two strings of the same length s1 and s2 and a string baseStr.
#
# We say s1[i] and s2[i] are equivalent characters.
#
# For example, if s1 = "abc" and s2 = "cde", then we have 'a' == 'c', 'b' ==
# 'd', and 'c' == 'e'.
#
# Equivalent characters follow the usual rules of any equivalence relation:
#
# Reflexivity: 'a' == 'a'.
#
# Symmetry: 'a' == 'b' implies 'b' == 'a'.
#
# Transitivity: 'a' == 'b' and 'b' == 'c' implies 'a' == 'c'.
#
# For example, given the equivalency information from s1 = "abc" and s2 =
# "cde", "acd" and "aab" are equivalent strings of baseStr = "eed", and "aab"
# is the lexicographically smallest equivalent string of baseStr.
#
# Return the lexicographically smallest equivalent string of baseStr by using
# the equivalency information from s1 and s2.
#
# Example 1:
#
# Input: s1 = "parker", s2 = "morris", baseStr = "parser"
# Output: "makkek"
# Explanation: Based on the equivalency information in s1 and s2, we can group
# their characters as [m,p], [a,o], [k,r,s], [e,i].
# The characters in each group are equivalent and sorted in lexicographical
# order.
# So the answer is "makkek".
#
# Example 2:
#
# Input: s1 = "hello", s2 = "world", baseStr = "hold"
# Output: "hdld"
# Explanation: Based on the equivalency information in s1 and s2, we can group
# their characters as [h,w], [d,e,o], [l,r].
# So only the second letter 'o' in baseStr is changed to 'd', the answer is
# "hdld".
#
# Example 3:
#
# Input: s1 = "leetcode", s2 = "programs", baseStr = "sourcecode"
# Output: "aauaaaaada"
# Explanation: We group the equivalent characters in s1 and s2 as
# [a,o,e,r,s,c], [l,p], [g,t] and [d,m], thus all letters in baseStr except 'u'
# and 'd' are transformed to 'a', the answer is "aauaaaaada".
#
# Constraints:
#
# 1 <= s1.length, s2.length, baseStr <= 1000
#
# s1.length == s2.length
#
# s1, s2, and baseStr consist of lowercase English letters.
#

# @lc code=start
class Solution:
    def smallestEquivalentString(self, s1: str, s2: str, baseStr: str) -> str:
        """
        Interview explanation:
        Characters linked by s1[i]~s2[i] are equivalent (transitive). Union-Find
        always linking toward the lexicographically smaller root; map baseStr.

        Algorithm:
        - parent[26]; find with path compression; union by smaller char
        - For each pair s1[i],s2[i] union; translate baseStr via find

        Complexity: O((n+m) α(26)) time, O(1) space.
        """
        parent = list(range(26))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

        for a, b in zip(s1, s2):
            union(ord(a) - 97, ord(b) - 97)
        return "".join(chr(find(ord(c) - 97) + 97) for c in baseStr)

    def smallestEquivalentString_dfs(self, s1: str, s2: str, baseStr: str) -> str:
        """
        Interview explanation:
        Alternate: build undirected graph of equivalences; for each component
        DFS/BFS find min char; map all members to that min.

        Algorithm:
        - adj lists; for each unvisited letter DFS component; assign min

        Complexity: O(n + 26) time, O(26) space.
        """
        from collections import defaultdict

        adj = defaultdict(set)
        for a, b in zip(s1, s2):
            adj[a].add(b)
            adj[b].add(a)
        rep = {}

        def dfs(c: str, comp: list) -> None:
            rep[c] = c  # mark visited
            comp.append(c)
            for nei in adj[c]:
                if nei not in rep:
                    dfs(nei, comp)

        for ch in list(adj.keys()):
            if ch not in rep:
                comp = []
                dfs(ch, comp)
                m = min(comp)
                for x in comp:
                    rep[x] = m
        return "".join(rep.get(c, c) for c in baseStr)
# @lc code=end
