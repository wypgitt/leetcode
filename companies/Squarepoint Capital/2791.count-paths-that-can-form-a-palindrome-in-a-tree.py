#
# @lc app=leetcode id=2791 lang=python3
#
# [2791] Count Paths That Can Form a Palindrome in a Tree
#
# https://leetcode.com/problems/count-paths-that-can-form-a-palindrome-in-a-tree/description/
#
# algorithms
# Hard (53.25%)
# Likes:    469
# Dislikes: 20
# Total Accepted:    16.3K
# Total Submissions: 30.7K
# Testcase Example:  "[-1,0,0,1,1,2]\n\"acaabc\""
#
# You are given a tree (i.e. a connected, undirected graph that has no cycles)
# rooted at node 0 consisting of n nodes numbered from 0 to n - 1. The tree is
# represented by a 0-indexed array parent of size n, where parent[i] is the
# parent of node i. Since node 0 is the root, parent[0] == -1.
#
# You are also given a string s of length n, where s[i] is the character
# assigned to the edge between i and parent[i]. s[0] can be ignored.
#
# Return the number of pairs of nodes (u, v) such that u < v and the characters
# assigned to edges on the path from u to v can be rearranged to form a
# palindrome.
#
# A string is a palindrome when it reads the same backwards as forwards.
#
#
#
# Example 1:
#
# Input: parent = [-1,0,0,1,1,2], s = "acaabc"
# Output: 8
# Explanation: The valid pairs are:
# - All the pairs (0,1), (0,2), (1,3), (1,4) and (2,5) result in one character
# which is always a palindrome.
# - The pair (2,3) result in the string "aca" which is a palindrome.
# - The pair (1,5) result in the string "cac" which is a palindrome.
# - The pair (3,5) result in the string "acac" which can be rearranged into the
# palindrome "acca".
#
# Example 2:
#
# Input: parent = [-1,0,0,0,0], s = "aaaaa"
# Output: 10
# Explanation: Any pair of nodes (u,v) where u < v is valid.
#
#
#
# Constraints:
#
#
# n == parent.length == s.length
#
#
# 1 <= n <= 10^5
#
#
# 0 <= parent[i] <= n - 1 for all i >= 1
#
#
# parent[0] == -1
#
#
# parent represents a valid tree.
#
#
# s consists of only lowercase English letters.
#

# @lc code=start
from collections import Counter, defaultdict
from typing import List


class Solution:
    def countPalindromePaths(self, parent: List[int], s: str) -> int:
        """
        Interview explanation:
        Tree rooted at 0; edge to i labeled s[i]. Count pairs of nodes whose path
        character multiset can rearrange to a palindrome (at most one odd count).

        Algorithm:
        - XOR bitmasks of char parity along root paths; DFS: for mask x, add
          cnt[x] and cnt[x^(1<<c)] for each c; then record x.

        Complexity: O(n * 26) time, O(n) space.
        """
        n = len(parent)
        g = defaultdict(list)
        for i in range(1, n):
            g[parent[i]].append((i, 1 << (ord(s[i]) - ord("a"))))
        ans = 0
        cnt = Counter({0: 1})

        def dfs(i: int, xor: int) -> None:
            nonlocal ans
            for j, v in g[i]:
                x = xor ^ v
                ans += cnt[x]
                for k in range(26):
                    ans += cnt[x ^ (1 << k)]
                cnt[x] += 1
                dfs(j, x)

        dfs(0, 0)
        return ans
# @lc code=end
