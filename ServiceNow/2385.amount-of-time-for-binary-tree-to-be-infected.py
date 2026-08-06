#
# @lc app=leetcode id=2385 lang=python3
#
# [2385] Amount of Time for Binary Tree to Be Infected
#
# https://leetcode.com/problems/amount-of-time-for-binary-tree-to-be-infected/description/
#
# algorithms
# Medium (65.82%)
# Likes:    3318
# Dislikes: 70
# Total Accepted:    219.3K
# Total Submissions: 333.2K
# Testcase Example:  "[1,5,3,null,4,10,6,9,2]\n3"
#
# You are given the root of a binary tree with unique values, and an integer
# start. At minute 0, an infection starts from the node with value start.
#
# Each minute, a node becomes infected if:
#
#
# The node is currently uninfected.
#
#
# The node is adjacent to an infected node.
#
# Return the number of minutes needed for the entire tree to be infected.
#
#
#
# Example 1:
#
# Input: root = [1,5,3,null,4,10,6,9,2], start = 3
# Output: 4
# Explanation: The following nodes are infected during:
# - Minute 0: Node 3
# - Minute 1: Nodes 1, 10 and 6
# - Minute 2: Node 5
# - Minute 3: Node 4
# - Minute 4: Nodes 9 and 2
# It takes 4 minutes for the whole tree to be infected so we return 4.
#
# Example 2:
#
# Input: root = [1], start = 1
# Output: 0
# Explanation: At minute 0, the only node in the tree is infected so we return
# 0.
#
#
#
# Constraints:
#
#
# The number of nodes in the tree is in the range [1, 10^5].
#
#
# 1 <= Node.val <= 10^5
#
#
# Each node has a unique value.
#
#
# A node with a value of start exists in the tree.
#

# @lc code=start

from typing import Optional
from collections import defaultdict, deque


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def amountOfTime(self, root: Optional[TreeNode], start: int) -> int:
        """
        Interview explanation:
        Infection starts at start; spreads to adjacent (parent/child) each
        minute. Return time to infect the whole tree.

        Algorithm:
        - Build undirected adjacency from tree; BFS from start for eccentricity.

        Complexity: O(n) time, O(n) space.
        """
        g = defaultdict(list)

        def build(node: Optional[TreeNode], parent: Optional[TreeNode]) -> None:
            if not node:
                return
            if parent:
                g[node.val].append(parent.val)
                g[parent.val].append(node.val)
            build(node.left, node)
            build(node.right, node)

        build(root, None)
        q = deque([start])
        seen = {start}
        minutes = -1
        while q:
            minutes += 1
            for _ in range(len(q)):
                u = q.popleft()
                for v in g[u]:
                    if v not in seen:
                        seen.add(v)
                        q.append(v)
        return max(0, minutes)

    def amountOfTime_dfs(self, root: Optional[TreeNode], start: int) -> int:
        """
        Interview explanation:
        Alternate one-pass DFS: return height and distance to start; update
        global max infection time when the path crosses through a parent.

        Algorithm:
        - dfs returns (height, dist_to_start|-1); if start in one child,
          ans = max(ans, dist+1+other_height); at start, ans = max(child heights).

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node: Optional[TreeNode]):
            if not node:
                return 0, -1
            lh, ld = dfs(node.left)
            rh, rd = dfs(node.right)
            h = 1 + max(lh, rh)
            if node.val == start:
                self.ans = max(self.ans, lh, rh)
                return h, 0
            if ld >= 0:
                self.ans = max(self.ans, ld + 1 + rh)
                return h, ld + 1
            if rd >= 0:
                self.ans = max(self.ans, rd + 1 + lh)
                return h, rd + 1
            return h, -1

        dfs(root)
        return self.ans
# @lc code=end
