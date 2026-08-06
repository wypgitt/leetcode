#
# @lc app=leetcode id=2646 lang=python3
#
# [2646] Minimize the Total Price of the Trips
#

# --- Notes (problem, path counts, tree DP, independence, complexity, edges, interview) ---
#
# Problem restatement
# Undirected tree on n nodes with integer prices price[u]. You are given several trips [start, end];
# each trip walks along the unique simple path between those endpoints (standard on a tree).
# For each node u, every time a trip path goes through u, you pay price[u] toward that trip’s
# contribution — equivalently, total cost equals sum_u price[u] * freq[u], where freq[u] is how
# many trip-paths include u.
# Before counting trips, you may choose a set of nodes whose prices are HALVED (integer division)
# for every traversal payment through them, with the rule that you cannot halve two adjacent nodes.
# Minimize the resulting total cost over all trips combined.
#
# Step 1 — frequency on paths (why not multiply per trip naïvely?)
# Each trip’s path is unique in a tree. For each [start, end], increment freq[u] by 1 for every u
# on that path. Implementation: DFS from start toward end by exploring neighbors except parent until
# hitting end; accumulate visited nodes on the successful branch (short-circuit once end found).
# Complexity O(sum of path lengths) <= O(n * |trips|) worst case; acceptable for LC constraints.
# Improvement: LCA + difference-on-tree marks all paths in O((n + |trips|) log n) if paths are long.
#
# Step 2 — tree DP after collapsing weights
# Define weighted cost w[u] = price[u] * freq[u]. Halving u saves w[u] / 2 on payments through u
# (cost becomes w[u]/2). Adjacent halving forbidden ⇒ chosen halving vertices form an independent
# set — weighted MIS-style DP on a tree.
# State: dfs(u, prev, parentHalved) = minimum total downstream contribution for the subtree rooted at
# u when edge (parent(u), u) is fixed and parentHalved tells whether parent’s price was halved.
# Transitions at u:
#   - Always allowed: pay full w[u] at u; children see parentHalved = False.
#   - If parent was NOT halved, optionally halve u: pay w[u]//2 at u; children must see
#     parentHalved = True (cannot halve a child if u is halved — equivalent constraint).
#   - If parent WAS halved, u cannot be halved — only full-price branch.
# Answer: dfs(root, -1, False). Root 0 after fixing an arbitrary tree orientation.
#
# Why this DP is correct
# On a tree, decisions at children depend only on whether their parent took half pricing — global
# independence constraint propagates exactly this one bit; subtrees are independent given that bit.
#
# Time complexity
# - Path marking: O(total nodes across all trip paths) <= O(n * |trips|) worst case.
# - DP: O(n) states with degree-sum work -> O(n).
#
# Space complexity
# - O(n) for graph, freq, recursion stack / memo (e.g. lru_cache depth O(n) worst).
#
# Edge cases
# - freq[u] == 0: node never used by trips — contributes 0 regardless of halving (still consistent).
# - Single node trips (start == end): path is one node; freq increments correctly via DFS base case.
# - price halving uses integer division // per statement / examples.
#
# Improvements
# - Binary lifting LCA + difference array for frequencies when paths are long and many trips.
# - Iterative DP / explicit memo table instead of lru_cache if recursion depth is a concern (convert
#   tree to rooted order via stack).
#
# LeetCode submission
# Put `from typing import List` and `functools.lru_cache` inside the LC code section markers.
#
# Interview walkthrough
# 1) Separate “how often each node is paid” from “which nodes we halve”.
# 2) Recognize independent-set structure on a tree -> parent-state DP.
# 3) Implement freq then DP; discuss faster freq counting if asked.
# --- end notes ---

# @lc code=start
import functools
from typing import List


class Solution:
    def minimumTotalPrice(self, n: int, edges: List[List[int]], price: List[int], trips: List[List[int]]) -> int:
        """
        Interview explanation:
        On a tree, each trip pays price[u] for every visit through u. Halve some nodes'
        prices (integer //) with no two adjacent halved; minimize total trip cost.

        Algorithm:
        - Count freq[u] = how many trip paths include u (DFS mark each start→end path).
        - Tree DP: at u, either pay full price[u]*freq[u], or if parent not halved pay
          half and forbid children from halving; take the min over the independent-set bit.

        Complexity: O(n · |trips|) time (path marking), O(n) DP; O(n) space.
        """
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)

        freq = [0] * n

        def mark_path(start: int, end: int) -> None:
            path: List[int] = []

            def dfs(u: int, parent: int) -> bool:
                path.append(u)
                if u == end:
                    for x in path:
                        freq[x] += 1
                    path.pop()
                    return True
                for v in g[u]:
                    if v != parent and dfs(v, u):
                        path.pop()
                        return True
                path.pop()
                return False

            dfs(start, -1)

        for s, e in trips:
            mark_path(s, e)

        @functools.lru_cache(maxsize=None)
        def dfs(u: int, prev: int, parent_halved: bool) -> int:
            pay_full = price[u] * freq[u] + sum(
                dfs(v, u, False) for v in g[u] if v != prev
            )
            if parent_halved:
                return pay_full
            pay_half = (price[u] // 2) * freq[u] + sum(
                dfs(v, u, True) for v in g[u] if v != prev
            )
            return min(pay_full, pay_half)

        return dfs(0, -1, False)


# @lc code=end
