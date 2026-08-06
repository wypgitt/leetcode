#
# @lc app=leetcode id=2049 lang=python3
#
# [2049] Count Nodes With the Highest Score
#
# https://leetcode.com/problems/count-nodes-with-the-highest-score/description/
#
# algorithms
# Medium (52.76%)
# Likes:    1203
# Dislikes: 101
# Total Accepted:    43.3K
# Total Submissions: 82K
# Testcase Example:  "[-1,2,0,2,0]"
#
# There is a binary tree rooted at 0 consisting of n nodes. The nodes are
# labeled from 0 to n - 1. You are given a 0-indexed integer array parents
# representing the tree, where parents[i] is the parent of node i. Since node 0
# is the root, parents[0] == -1.
#
# Each node has a score. To find the score of a node, consider if the node and
# the edges connected to it were removed. The tree would become one or more
# non-empty subtrees. The size of a subtree is the number of the nodes in it.
# The score of the node is the product of the sizes of all those subtrees.
#
# Return the number of nodes that have the highest score.
#
#
#
# Example 1:
#
# Input: parents = [-1,2,0,2,0]
# Output: 3
# Explanation:
# - The score of node 0 is: 3 * 1 = 3
# - The score of node 1 is: 4 = 4
# - The score of node 2 is: 1 * 1 * 2 = 2
# - The score of node 3 is: 4 = 4
# - The score of node 4 is: 4 = 4
# The highest score is 4, and three nodes (node 1, node 3, and node 4) have the
# highest score.
#
# Example 2:
#
# Input: parents = [-1,2,0]
# Output: 2
# Explanation:
# - The score of node 0 is: 2 = 2
# - The score of node 1 is: 2 = 2
# - The score of node 2 is: 1 * 1 = 1
# The highest score is 2, and two nodes (node 0 and node 1) have the highest
# score.
#
#
#
# Constraints:
#
#
# n == parents.length
#
#
# 2 <= n <= 10^5
#
#
# parents[0] == -1
#
#
# 0 <= parents[i] <= n - 1 for i != 0
#
#
# parents represents a valid binary tree.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def countHighestScoreNodes(self, parents: List[int]) -> int:
        """
        Interview explanation:
        Tree from parents array. Score of removing node = product of component
        sizes (children subtrees and remainder). Count nodes with max score.

        Algorithm:
        - DFS sizes; for node u, product child sizes and (n-size[u]) if >0;
          track max and count.

        Complexity: O(n) time, O(n) space.
        """
        n = len(parents)
        children = defaultdict(list)
        for i, p in enumerate(parents):
            if p != -1:
                children[p].append(i)
        ans = 0
        best = 0

        def dfs(u: int) -> int:
            nonlocal ans, best
            prod = 1
            size = 1
            for v in children[u]:
                sz = dfs(v)
                prod *= sz
                size += sz
            rest = n - size
            if rest > 0:
                prod *= rest
            if prod > best:
                best = prod
                ans = 1
            elif prod == best:
                ans += 1
            return size

        dfs(0)
        return ans
# @lc code=end
