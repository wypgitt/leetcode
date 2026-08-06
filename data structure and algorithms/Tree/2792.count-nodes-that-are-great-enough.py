#
# @lc app=leetcode id=2792 lang=python3
#
# [2792] Count Nodes That Are Great Enough
#
# https://leetcode.com/problems/count-nodes-that-are-great-enough/description/
#
# algorithms
# Hard (56.77%)
# Likes:    24
# Dislikes: 0
# Total Accepted:    1.5K
# Total Submissions: 2.6K
# Testcase Example:  "[7,6,5,4,3,2,1]\n2"
#
#
# You are given a root to a binary tree and an integer k. A node of this
# tree is called great enough if the followings hold:
#
# Its subtree has at least k nodes.
#
# Its value is greater than the value of at least k nodes in its subtree.
#
# Return the number of nodes in this tree that are great enough.
#
# The node u is in the subtree of the node v, if u == v or v is an
# ancestor of u.
#
# Example 1:
#
# Input: root = [7,6,5,4,3,2,1], k = 2
# Output: 3
# Explanation: Number the nodes from 1 to 7.
# The values in the subtree of node 1: {1,2,3,4,5,6,7}. Since node.val ==
# 7, there are 6 nodes having a smaller value than its value. So it's
# great enough.
# The values in the subtree of node 2: {3,4,6}. Since node.val == 6, there
# are 2 nodes having a smaller value than its value. So it's great enough.
# The values in the subtree of node 3: {1,2,5}. Since node.val == 5, there
# are 2 nodes having a smaller value than its value. So it's great enough.
# It can be shown that other nodes are not great enough.
# See the picture below for a better understanding.
#
# Example 2:
#
# Input: root = [1,2,3], k = 1
# Output: 0
# Explanation: Number the nodes from 1 to 3.
# The values in the subtree of node 1: {1,2,3}. Since node.val == 1, there
# are no nodes having a smaller value than its value. So it's not great
# enough.
# The values in the subtree of node 2: {2}. Since node.val == 2, there are
# no nodes having a smaller value than its value. So it's not great
# enough.
# The values in the subtree of node 3: {3}. Since node.val == 3, there are
# no nodes having a smaller value than its value. So it's not great
# enough.
# See the picture below for a better understanding.
#
# Example 3:
#
# Input: root = [3,2,2], k = 2
# Output: 1
# Explanation: Number the nodes from 1 to 3.
# The values in the subtree of node 1: {2,2,3}. Since node.val == 3, there
# are 2 nodes having a smaller value than its value. So it's great enough.
# The values in the subtree of node 2: {2}. Since node.val == 2, there are
# no nodes having a smaller value than its value. So it's not great
# enough.
# The values in the subtree of node 3: {2}. Since node.val == 2, there are
# no nodes having a smaller value than its value. So it's not great
# enough.
# See the picture below for a better understanding.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# 1 <= Node.val <= 10^4
#
# 1 <= k <= 10
#
# @lc code=start
from heapq import heappop, heappush
from typing import List, Optional

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
    def countGreatEnoughNodes(self, root: Optional[TreeNode], k: int) -> int:
        """
        Interview explanation:
        Premium: a node is great enough if it has >= k nodes in its subtree
        strictly smaller than it. Count such nodes.

        Algorithm:
        - Post-order DFS returning a min-heap (size <= k) of the k smallest
          negated values in the subtree; node counts if heap size == k and
          -heap[0] < node.val.

        Complexity: O(n log k) time, O(n) space.
        """
        ans = 0

        def push(pq: List[int], x: int) -> None:
            heappush(pq, x)
            if len(pq) > k:
                heappop(pq)

        def dfs(node: Optional[TreeNode]) -> List[int]:
            nonlocal ans
            if node is None:
                return []
            left = dfs(node.left)
            right = dfs(node.right)
            for x in right:
                push(left, x)
            if len(left) == k and -left[0] < node.val:
                ans += 1
            push(left, -node.val)
            return left

        dfs(root)
        return ans
# @lc code=end
