#
# @lc app=leetcode id=559 lang=python3
#
# [559] Maximum Depth of N-ary Tree
#
# https://leetcode.com/problems/maximum-depth-of-n-ary-tree/description/
#
# algorithms
# Easy (73.73%)
# Likes:    2891
# Dislikes: 96
# Total Accepted:    365K
# Total Submissions: 495K
# Testcase Example:  "[1,null,3,2,4,null,5,6]"
#
# Given a n-ary tree, find its maximum depth.
#
# The maximum depth is the number of nodes along the longest path from the root
# node down to the farthest leaf node.
#
# Nary-Tree input serialization is represented in their level order traversal,
# each group of children is separated by the null value (See examples).
#
# Example 1:
#
# Input: root = [1,null,3,2,4,null,5,6]
# Output: 3
#
# Example 2:
#
# Input: root =
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
# Output: 5
#
# Constraints:
#
# The total number of nodes is in the range [0, 10^4].
#
# The depth of the n-ary tree is less than or equal to 1000.
#

# @lc code=start
from collections import deque
from typing import List, Optional
"""
# Definition for a Node.
class Node:
    def __init__(self, val: Optional[int] = None, children: Optional[List['Node']] = None):
        self.val = val
        self.children = children
"""

class Solution:
    def maxDepth(self, root: 'Node') -> int:
        """
        Interview explanation:
        N-ary depth is 1 + max depth among children (0 if empty). DFS returns
        that bottom-up.

        Algorithm:
        - Empty → 0; else 1 + max(maxDepth(c) for c in children) or 1 if none.

        Complexity: O(n) time, O(h) recursion space.
        """
        if not root:
            return 0
        if not root.children:
            return 1
        return 1 + max(self.maxDepth(c) for c in root.children)

    def maxDepth_bfs(self, root: 'Node') -> int:
        """
        Interview explanation:
        Alternate level-order BFS: count levels until the queue is empty.

        Complexity: O(n) time, O(w) queue space.
        """
        if not root:
            return 0
        depth = 0
        q = deque([root])
        while q:
            for _ in range(len(q)):
                node = q.popleft()
                for c in node.children or []:
                    q.append(c)
            depth += 1
        return depth
# @lc code=end

