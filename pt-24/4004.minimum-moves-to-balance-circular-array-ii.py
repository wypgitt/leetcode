#
# @lc app=leetcode id=4004 lang=python3
#
# [4004] Minimum Moves to Balance Circular Array II
#
# https://leetcode.com/problems/minimum-moves-to-balance-circular-array-ii/description/
#
# algorithms
# Hard (69.74%)
# Likes:    1
# Dislikes: 1
# Total Accepted:    136
# Total Submissions: 195
# Testcase Example:  "[-1,2,-1]"
#
#
# You are given a circular array balance of length n, where balance[i] is
# the net balance of person i.
#
# In one move, a person can transfer exactly 1 unit of balance to either
# their left or right neighbor.
#
# Return the minimum number of moves required so that every person has a
# non-negative balance. If it is impossible, return -1.
#
# Example 1:
#
# Input: balance = [-1,2,-1]
#
# Output: 2
#
# Explanation:
#
# One optimal sequence of moves is:
#
# Move 1 unit from i = 1 to i = 0, resulting in balance = [0, 1, -1]
#
# Move 1 unit from i = 1 to i = 2, resulting in balance = [0, 0, 0]
#
# Thus, the minimum number of moves required is 2.
#
# Example 2:
#
# Input: balance = [4,-1,-2]
#
# Output: 3
#
# Explanation:
#
# One optimal sequence of moves is:
#
# Move 1 unit from i = 0 to i = 1, resulting in balance = [3, 0, -2]
#
# Move 1 unit from i = 0 to i = 2, resulting in balance = [2, 0, -1]
#
# Move 1 unit from i = 0 to i = 2, resulting in balance = [1, 0, 0]
#
# Thus, the minimum number of moves required is 3.
#
# Example 3:
#
# Input: balance = [-3,-3,5]
#
# Output: -1
#
# Explanation:
#
# It is impossible to make all balances non-negative for balance = [-3,
# -3, 5], so the answer is -1.
#
# Constraints:
#
# 1 <= n == balance.length <= 1000
#
# -10^5 <= balance[i] <= 10^5
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def minMoves(self, balance: List[int]) -> int:
        """
        Interview explanation:
        Units must flow from surplus people to deficit people along the circle;
        each step to a neighbor costs 1 move. Impossible iff total sum < 0.

        Algorithm:
        - Model as min-cost max-flow: source→surpluses, deficits→sink,
          bidirectional unit-cost edges around the cycle.
        - Successive shortest paths (SPFA) push bottleneck flow until the
          total deficit is satisfied; total cost is the answer.

        Complexity: O(n^2) typical / O(n^3) worst, O(n) space (n ≤ 1000).
        """
        INF = 10**18
        total_balance = sum(balance)
        if total_balance < 0:
            return -1

        n = len(balance)
        total_deficit = sum(-x for x in balance if x < 0)
        if total_deficit == 0:
            return 0

        source, sink = n, n + 1
        num_nodes = n + 2
        graph = [[] for _ in range(num_nodes)]

        def add_edge(u: int, v: int, cap: int, cost: int) -> None:
            graph[u].append([v, cap, cost, len(graph[v])])
            graph[v].append([u, 0, -cost, len(graph[u]) - 1])

        for i in range(n):
            if balance[i] > 0:
                add_edge(source, i, balance[i], 0)
            elif balance[i] < 0:
                add_edge(i, sink, -balance[i], 0)
            add_edge(i, (i + 1) % n, INF, 1)
            add_edge(i, (i - 1 + n) % n, INF, 1)

        total_cost = 0
        current_flow = 0
        while current_flow < total_deficit:
            dist = [INF] * num_nodes
            parent_node = [-1] * num_nodes
            parent_edge = [-1] * num_nodes
            in_queue = [False] * num_nodes
            queue = deque([source])
            dist[source] = 0
            in_queue[source] = True
            while queue:
                u = queue.popleft()
                in_queue[u] = False
                for idx, (v, cap, cost, _) in enumerate(graph[u]):
                    if cap > 0 and dist[v] > dist[u] + cost:
                        dist[v] = dist[u] + cost
                        parent_node[v] = u
                        parent_edge[v] = idx
                        if not in_queue[v]:
                            queue.append(v)
                            in_queue[v] = True
            if dist[sink] == INF:
                break
            push_flow = total_deficit - current_flow
            curr = sink
            while curr != source:
                p = parent_node[curr]
                idx = parent_edge[curr]
                push_flow = min(push_flow, graph[p][idx][1])
                curr = p
            curr = sink
            while curr != source:
                p = parent_node[curr]
                idx = parent_edge[curr]
                rev_idx = graph[p][idx][3]
                graph[p][idx][1] -= push_flow
                graph[curr][rev_idx][1] += push_flow
                curr = p
            current_flow += push_flow
            total_cost += push_flow * dist[sink]

        return total_cost if current_flow == total_deficit else -1
# @lc code=end
