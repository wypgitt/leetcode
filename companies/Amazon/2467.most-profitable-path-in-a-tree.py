#
# @lc app=leetcode id=2467 lang=python3
#
# [2467] Most Profitable Path in a Tree
#
# https://leetcode.com/problems/most-profitable-path-in-a-tree/description/
#
# algorithms
# Medium (67.27%)
# Likes:    1422
# Dislikes: 248
# Total Accepted:    111K
# Total Submissions: 165K
# Testcase Example:  "[[0,1],[1,2],[1,3],[3,4]]\n3\n[-2,4,2,-4,6]"
#
# There is an undirected tree with n nodes labeled from 0 to n - 1, rooted at
# node 0. You are given a 2D integer array edges of length n - 1 where edges[i]
# = [a_i, b_i] indicates that there is an edge between nodes a_i and b_i in the
# tree.
#
# At every node i, there is a gate. You are also given an array of even integers
# amount, where amount[i] represents:
#
#
# the price needed to open the gate at node i, if amount[i] is negative, or,
#
#
# the cash reward obtained on opening the gate at node i, otherwise.
#
# The game goes on as follows:
#
#
# Initially, Alice is at node 0 and Bob is at node bob.
#
#
# At every second, Alice and Bob each move to an adjacent node. Alice moves
# towards some leaf node, while Bob moves towards node 0.
#
#
# For every node along their path, Alice and Bob either spend money to open the
# gate at that node, or accept the reward. Note that:
#
#
#
# If the gate is already open, no price will be required, nor will there be any
# cash reward.
#
#
# If Alice and Bob reach the node simultaneously, they share the price/reward
# for opening the gate there. In other words, if the price to open the gate is
# c, then both Alice and Bob pay c / 2 each. Similarly, if the reward at the
# gate is c, both of them receive c / 2 each.
#
#
#
#
#
#
# If Alice reaches a leaf node, she stops moving. Similarly, if Bob reaches node
# 0, he stops moving. Note that these events are independent of each other.
#
# Return the maximum net income Alice can have if she travels towards the
# optimal leaf node.
#
#
#
# Example 1:
#
# Input: edges = [[0,1],[1,2],[1,3],[3,4]], bob = 3, amount = [-2,4,2,-4,6]
# Output: 6
# Explanation:
# The above diagram represents the given tree. The game goes as follows:
# - Alice is initially on node 0, Bob on node 3. They open the gates of their
# respective nodes.
#   Alice's net income is now -2.
# - Both Alice and Bob move to node 1.
#   Since they reach here simultaneously, they open the gate together and share
# the reward.
#   Alice's net income becomes -2 + (4 / 2) = 0.
# - Alice moves on to node 3. Since Bob already opened its gate, Alice's income
# remains unchanged.
#   Bob moves on to node 0, and stops moving.
# - Alice moves on to node 4 and opens the gate there. Her net income becomes 0
# + 6 = 6.
# Now, neither Alice nor Bob can make any further moves, and the game ends.
# It is not possible for Alice to get a higher net income.
#
# Example 2:
#
# Input: edges = [[0,1]], bob = 1, amount = [-7280,2350]
# Output: -7280
# Explanation:
# Alice follows the path 0->1 whereas Bob follows the path 1->0.
# Thus, Alice opens the gate at node 0 only. Hence, her net income is -7280.
#
#
#
# Constraints:
#
#
# 2 <= n <= 10^5
#
#
# edges.length == n - 1
#
#
# edges[i].length == 2
#
#
# 0 <= a_i, b_i < n
#
#
# a_i != b_i
#
#
# edges represents a valid tree.
#
#
# 1 <= bob < n
#
#
# amount.length == n
#
#
# amount[i] is an even integer in the range [-10^4, 10^4].
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def mostProfitablePath(
        self, edges: List[List[int]], bob: int, amount: List[int]
    ) -> int:
        """
        Interview explanation:
        Alice starts at 0, Bob at bob; both move each second. Alice maximizes
        income; when they meet on a node same time, split amount. Gate opens
        after first visit (Bob zeros a node after visiting).

        Algorithm:
        - Find Bob's path times to 0; DFS Alice maximizing profit with shared
          amounts when times equal / Alice-first / Bob-first.

        Complexity: O(n) time, O(n) space.
        """
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        n = len(amount)
        bob_time = [n] * n

        def dfs_bob(u: int, p: int, t: int) -> bool:
            if u == 0:
                bob_time[u] = t
                return True
            for v in g[u]:
                if v != p and dfs_bob(v, u, t + 1):
                    bob_time[u] = t
                    return True
            return False

        dfs_bob(bob, -1, 0)
        ans = float("-inf")

        def dfs_alice(u: int, p: int, t: int, income: int) -> None:
            nonlocal ans
            if t < bob_time[u]:
                income += amount[u]
            elif t == bob_time[u]:
                income += amount[u] // 2
            is_leaf = True
            for v in g[u]:
                if v != p:
                    is_leaf = False
                    dfs_alice(v, u, t + 1, income)
            if is_leaf:
                ans = max(ans, income)

        dfs_alice(0, -1, 0, 0)
        return ans
# @lc code=end

