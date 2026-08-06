#
# @lc app=leetcode id=2538 lang=python3
#
# [2538] Difference Between Maximum and Minimum Price Sum
#
# https://leetcode.com/problems/difference-between-maximum-and-minimum-price-sum/description/
#
# algorithms
# Hard (34.06%)
# Likes:    484
# Dislikes: 20
# Total Accepted:    11.8K
# Total Submissions: 34.7K
# Testcase Example:  "6\n[[0,1],[1,2],[1,3],[3,4],[3,5]]\n[9,8,7,6,10,5]"
#
# There exists an undirected and initially unrooted tree with n nodes indexed
# from 0 to n - 1. You are given the integer n and a 2D integer array edges of
# length n - 1, where edges[i] = [a_i, b_i] indicates that there is an edge
# between nodes a_i and b_i in the tree.
#
# Each node has an associated price. You are given an integer array price, where
# price[i] is the price of the i^th node.
#
# The price sum of a given path is the sum of the prices of all nodes lying on
# that path.
#
# The tree can be rooted at any node root of your choice. The incurred cost
# after choosing root is the difference between the maximum and minimum price
# sum amongst all paths starting at root.
#
# Return the maximum possible cost amongst all possible root choices.
#
#
#
# Example 1:
#
# Input: n = 6, edges = [[0,1],[1,2],[1,3],[3,4],[3,5]], price = [9,8,7,6,10,5]
# Output: 24
# Explanation: The diagram above denotes the tree after rooting it at node 2.
# The first part (colored in red) shows the path with the maximum price sum. The
# second part (colored in blue) shows the path with the minimum price sum.
# - The first path contains nodes [2,1,3,4]: the prices are [7,8,6,10], and the
# sum of the prices is 31.
# - The second path contains the node [2] with the price [7].
# The difference between the maximum and minimum price sum is 24. It can be
# proved that 24 is the maximum cost.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[1,2]], price = [1,1,1]
# Output: 2
# Explanation: The diagram above denotes the tree after rooting it at node 0.
# The first part (colored in red) shows the path with the maximum price sum. The
# second part (colored in blue) shows the path with the minimum price sum.
# - The first path contains nodes [0,1,2]: the prices are [1,1,1], and the sum
# of the prices is 3.
# - The second path contains node [0] with a price [1].
# The difference between the maximum and minimum price sum is 2. It can be
# proved that 2 is the maximum cost.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^5
#
#
# edges.length == n - 1
#
#
# 0 <= a_i, b_i <= n - 1
#
#
# edges represents a valid tree.
#
#
# price.length == n
#
#
# 1 <= price[i] <= 10^5
#

# @lc code=start
from typing import List
import sys

sys.setrecursionlimit(10**6)


class Solution:
    def maxOutput(self, n: int, edges: List[List[int]], price: List[int]) -> int:
        """
        Interview explanation:
        Tree with node prices. Root at any node; cost = max path-sum from root
        minus min path-sum from root. Min is always price[root] (singleton path).
        Maximize cost over root choices. Optimal roots are leaves.

        Algorithm:
        (Tree DP + rerooting)
        - First DFS: maxSums[u] = price[u] + max child downward path sum.
        - Second DFS reroot: at u keep top-2 child maxSums and parent-side sum;
          for leaves, ans = max(parentSum, best child sum) (= max path - price[u]).
          Pass next parent-side sum into each child.

        Complexity: O(n) time, O(n) space.
        """
        if n == 1:
            return 0

        tree: list[list[int]] = [[] for _ in range(n)]
        for u, v in edges:
            tree[u].append(v)
            tree[v].append(u)

        max_sums = [0] * n

        def dfs_down(u: int, parent: int) -> int:
            best = 0
            for v in tree[u]:
                if v != parent:
                    best = max(best, dfs_down(v, u))
            max_sums[u] = price[u] + best
            return max_sums[u]

        dfs_down(0, -1)

        ans = 0

        def reroot(u: int, parent: int, parent_sum: int) -> None:
            nonlocal ans
            top1 = top2 = 0
            top_node = -1
            for v in tree[u]:
                if v == parent:
                    continue
                if max_sums[v] > top1:
                    top2 = top1
                    top1 = max_sums[v]
                    top_node = v
                elif max_sums[v] > top2:
                    top2 = max_sums[v]

            # Optimal cost achieved at degree-1 nodes (leaves)
            if len(tree[u]) == 1:
                ans = max(ans, parent_sum, top1)

            for v in tree[u]:
                if v == parent:
                    continue
                # path sum from u toward parent / other children, excluding v
                side = top2 if v == top_node else top1
                next_parent = price[u] + max(parent_sum, side)
                reroot(v, u, next_parent)

        reroot(0, -1, 0)
        return ans
# @lc code=end
