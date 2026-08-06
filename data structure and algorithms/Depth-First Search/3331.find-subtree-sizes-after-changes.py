#
# @lc app=leetcode id=3331 lang=python3
#
# [3331] Find Subtree Sizes After Changes
#
# https://leetcode.com/problems/find-subtree-sizes-after-changes/description/
#
# algorithms
# Medium (52.83%)
# Likes:    108
# Dislikes: 37
# Total Accepted:    17.1K
# Total Submissions: 32.4K
# Testcase Example:  "[-1,0,0,1,1,1]\n\"abaabc\""
#
#
# You are given a tree rooted at node 0 that consists of n nodes numbered
# from 0 to n - 1. The tree is represented by an array parent of size n,
# where parent[i] is the parent of node i. Since node 0 is the root,
# parent[0] == -1.
#
# You are also given a string s of length n, where s[i] is the character
# assigned to node i.
#
# We make the following changes on the tree one time simultaneously for
# all nodes x from 1 to n - 1:
#
# Find the closest node y to node x such that y is an ancestor of x, and
# s[x] == s[y].
#
# If node y does not exist, do nothing.
#
# Otherwise, remove the edge between x and its current parent and make
# node y the new parent of x by adding an edge between them.
#
# Return an array answer of size n where answer[i] is the size of the
# subtree rooted at node i in the final tree.
#
# Example 1:
#
# Input: parent = [-1,0,0,1,1,1], s = "abaabc"
#
# Output: [6,3,1,1,1,1]
#
# Explanation:
#
# The parent of node 3 will change from node 1 to node 0.
#
# Example 2:
#
# Input: parent = [-1,0,4,0,1], s = "abbba"
#
# Output: [5,2,1,1,1]
#
# Explanation:
#
# The following changes will happen at the same time:
#
# The parent of node 4 will change from node 1 to node 0.
#
# The parent of node 2 will change from node 4 to node 1.
#
# Constraints:
#
# n == parent.length == s.length
#
# 1 <= n <= 10^5
#
# 0 <= parent[i] <= n - 1 for all i >= 1.
#
# parent[0] == -1
#
# parent represents a valid tree.
#
# s consists only of lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def findSubtreeSizes(self, parent: List[int], s: str) -> List[int]:
        """
        Interview explanation:
        Simultaneously reparent each node to its closest same-letter ancestor
        (if any), then report subtree sizes in the final forest/tree.

        Algorithm:
        - DFS the original tree while tracking the last ancestor per character;
          that last ancestor is the new parent when present.
        - Rebuild adjacency from new parents and DFS sizes from root 0.

        Complexity: O(n) time and space.
        """
        n = len(parent)
        g: List[List[int]] = [[] for _ in range(n)]
        for i in range(1, n):
            g[parent[i]].append(i)

        new_parent = parent[:]
        last = [-1] * 26

        def mark(u: int) -> None:
            c = ord(s[u]) - 97
            prev = last[c]
            if u != 0 and prev != -1:
                new_parent[u] = prev
            last[c] = u
            for v in g[u]:
                mark(v)
            last[c] = prev

        mark(0)

        tree: List[List[int]] = [[] for _ in range(n)]
        for i in range(1, n):
            tree[new_parent[i]].append(i)

        ans = [0] * n

        def size(u: int) -> int:
            sz = 1
            for v in tree[u]:
                sz += size(v)
            ans[u] = sz
            return sz

        size(0)
        return ans
# @lc code=end

