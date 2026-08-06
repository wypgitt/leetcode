#
# @lc app=leetcode id=3841 lang=python3
#
# [3841] Palindromic Path Queries in a Tree
#
# https://leetcode.com/problems/palindromic-path-queries-in-a-tree/description/
#
# algorithms
# Hard (37.11%)
# Likes:    61
# Dislikes: 3
# Total Accepted:    4.1K
# Total Submissions: 11.1K
# Testcase Example:  "3\n[[0,1],[1,2]]\n\"aac\"\n[\"query 0 2\",\"update 1 b\",\"query 0 2\"]"
#
#
# You are given an undirected tree with n nodes labeled 0 to n - 1. This
# is represented by a 2D array edges of length n - 1, where edges[i] =
# [u_i, v_i] indicates an undirected edge between nodes u_i and v_i.
#
# You are also given a string s of length n consisting of lowercase
# English letters, where s[i] represents the character assigned to node i.
#
# You are also given a string array queries, where each queries[i] is
# either:
#
# "update u_i c": Change the character at node u_i to c. Formally, update
# s[u_i] = c.
#
# "query u_i v_i": Determine whether the string formed by the characters
# on the unique path from u_i to v_i (inclusive) can be rearranged into a
# palindrome.
#
# Return a boolean array answer, where answer[j] is true if the j^th query
# of type "query u_i v_i"​​​​​​​ can be rearranged into a palindrome, and
# false otherwise.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[1,2]], s = "aac", queries = ["query 0
# 2","update 1 b","query 0 2"]
#
# Output: [true,false]
#
# Explanation:
#
# "query 0 2": Path 0 → 1 → 2 gives "aac", which can be rearranged to form
# "aca", a palindrome. Thus, answer[0] = true.
#
# "update 1 b": Update node 1 to 'b', now s = "abc".
#
# "query 0 2": Path characters are "abc", which cannot be rearranged to
# form a palindrome. Thus, answer[1] = false.
#
# Thus, answer = [true, false].
#
# Example 2:
#
# Input: n = 4, edges = [[0,1],[0,2],[0,3]], s = "abca", queries = ["query
# 1 2","update 0 b","query 2 3","update 3 a","query 1 3"]
#
# Output: [false,false,true]
#
# Explanation:
#
# "query 1 2": Path 1 → 0 → 2 gives "bac", which cannot be rearranged to
# form a palindrome. Thus, answer[0] = false.
#
# "update 0 b": Update node 0 to 'b', now s = "bbca".
#
# "query 2 3": Path 2 → 0 → 3 gives "cba", which cannot be rearranged to
# form a palindrome. Thus, answer[1] = false.
#
# "update 3 a": Update node 3 to 'a', s = "bbca".
#
# "query 1 3": Path 1 → 0 → 3 gives "bba", which can be rearranged to form
# "bab", a palindrome. Thus, answer[2] = true.
#
# Thus, answer = [false, false, true].
#
# Constraints:
#
# 1 <= n == s.length <= 5 * 10^4
#
# edges.length == n - 1
#
# edges[i] = [u_i, v_i]
#
# 0 <= u_i, v_i <= n - 1
#
# s consists of lowercase English letters.
#
# The input is generated such that edges represents a valid tree.
#
# 1 <= queries.length <= 5 * 10^4​​​​​​​
#
# queries[i] = "update u_i c" or
#
# queries[i] = "query u_i v_i"
#
# 0 <= u_i, v_i <= n - 1
#
# c is a lowercase English letter.
#

# @lc code=start
from typing import List


class SegmentTreeXor:
    def __init__(self, values: List[int]) -> None:
        """
        Interview explanation:
        Iterative segment tree storing XOR of ranges for path character masks.

        Algorithm:
        - Pad to power of two; leaves hold values, parents store child XOR.

        Complexity: O(n) build time/space.
        """
        size = 1
        while size < len(values):
            size <<= 1
        self.size = size
        self.tree = [0] * (2 * size)

        for i, value in enumerate(values):
            self.tree[size + i] = value
        for i in range(size - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] ^ self.tree[2 * i + 1]

    def update(self, index: int, value: int) -> None:
        """
        Interview explanation:
        Point-assign a leaf and refresh ancestors' XOR.

        Algorithm:
        - Write leaf, walk up combining sibling pairs.

        Complexity: O(log n) time, O(1) space.
        """
        index += self.size
        self.tree[index] = value
        index //= 2
        while index:
            self.tree[index] = self.tree[2 * index] ^ self.tree[2 * index + 1]
            index //= 2

    def query(self, left: int, right: int) -> int:
        """
        Interview explanation:
        Range XOR on inclusive [left, right].

        Algorithm:
        - Standard iterative segment-tree pull from both ends.

        Complexity: O(log n) time, O(1) space.
        """
        left += self.size
        right += self.size
        ans = 0

        while left <= right:
            if left & 1:
                ans ^= self.tree[left]
                left += 1
            if not (right & 1):
                ans ^= self.tree[right]
                right -= 1
            left //= 2
            right //= 2

        return ans


class Solution:
    def palindromePath(
        self, n: int, edges: List[List[int]], s: str, queries: List[str]
    ) -> List[bool]:
        """
        Interview explanation:
        Path letters rearrange to a palindrome iff at most one char has odd
        frequency. Answer updates and path queries on a tree.

        Algorithm:
        - Heavy-light decompose; store bitmasks (1<<letter) in an XOR segtree.
        - Path XOR of masks = parity vector of frequencies along the path.
        - Palindrome check: mask & (mask - 1) == 0 (0 or 1 odd bit).

        Complexity: O((n + q) log^2 n) time, O(n) space.
        """
        graph = [[] for _ in range(n)]
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)

        parent = [-1] * n
        depth = [0] * n
        order = [0]

        for node in order:
            for nei in graph[node]:
                if nei == parent[node]:
                    continue
                parent[nei] = node
                depth[nei] = depth[node] + 1
                order.append(nei)

        size = [1] * n
        heavy = [-1] * n
        for node in reversed(order):
            best_size = 0
            for nei in graph[node]:
                if parent[nei] == node:
                    size[node] += size[nei]
                    if size[nei] > best_size:
                        best_size = size[nei]
                        heavy[node] = nei

        head = [0] * n
        pos = [0] * n
        base = [0] * n
        current_pos = 0
        stack = [(0, 0)]

        while stack:
            start, chain_head = stack.pop()
            node = start
            while node != -1:
                head[node] = chain_head
                pos[node] = current_pos
                base[current_pos] = self._mask(s[node])
                current_pos += 1

                for nei in graph[node]:
                    if parent[nei] == node and nei != heavy[node]:
                        stack.append((nei, nei))

                node = heavy[node]

        seg = SegmentTreeXor(base)
        chars = list(s)
        answer = []

        for raw in queries:
            parts = raw.split()
            if parts[0] == "update":
                node = int(parts[1])
                chars[node] = parts[2]
                seg.update(pos[node], self._mask(parts[2]))
            else:
                u = int(parts[1])
                v = int(parts[2])
                mask = self._path_xor(u, v, head, parent, depth, pos, seg)
                answer.append(mask & (mask - 1) == 0)

        return answer

    def _path_xor(
        self,
        u: int,
        v: int,
        head: List[int],
        parent: List[int],
        depth: List[int],
        pos: List[int],
        seg: SegmentTreeXor,
    ) -> int:
        ans = 0

        while head[u] != head[v]:
            if depth[head[u]] < depth[head[v]]:
                u, v = v, u
            ans ^= seg.query(pos[head[u]], pos[u])
            u = parent[head[u]]

        if depth[u] > depth[v]:
            u, v = v, u
        ans ^= seg.query(pos[u], pos[v])
        return ans

    def _mask(self, ch: str) -> int:
        return 1 << (ord(ch) - ord("a"))
# @lc code=end
