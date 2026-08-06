#
# @lc app=leetcode id=1379 lang=python3
#
# [1379] Find a Corresponding Node of a Binary Tree in a Clone of That Tree
#
# https://leetcode.com/problems/find-a-corresponding-node-of-a-binary-tree-in-a-clone-of-that-tree/description/
#
# algorithms
# Easy (85.84%)
# Likes:    1821
# Dislikes: 2019
# Total Accepted:    269K
# Total Submissions: 314K
# Testcase Example:  "[7,4,3,null,null,6,19]"
#
# Given two binary trees original and cloned and given a reference to a node
# target in the original tree.
#
# The cloned tree is a copy of the original tree.
#
# Return a reference to the same node in the cloned tree.
#
# Note that you are not allowed to change any of the two trees or the target
# node and the answer must be a reference to a node in the cloned tree.
#
# Example 1:
#
# Input: tree = [7,4,3,null,null,6,19], target = 3
# Output: 3
# Explanation: In all examples the original and cloned trees are shown. The
# target node is a green node from the original tree. The answer is the yellow
# node from the cloned tree.
#
# Example 2:
#
# Input: tree = [7], target = 7
# Output: 7
#
# Example 3:
#
# Input: tree = [8,null,6,null,5,null,4,null,3,null,2,null,1], target = 4
# Output: 4
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# The values of the nodes of the tree are unique.
#
# target node is a node from the original tree and is not null.
#
# Follow up: Could you solve the problem if repeated values on the tree are
# allowed?
#

# @lc code=start

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None


class Solution:
    def getTargetCopy(self, original: "TreeNode", cloned: "TreeNode", target: "TreeNode") -> "TreeNode":
        """
        Interview explanation:
        Trees are identical in structure; walk original and cloned in sync;
        when original is target, return cloned node.

        Algorithm (DFS):
        - If original is target return cloned; recurse left then right

        Complexity: O(n) time, O(h) space.
        """
        if original is target:
            return cloned
        if not original:
            return None
        left = self.getTargetCopy(original.left, cloned.left, target)
        if left:
            return left
        return self.getTargetCopy(original.right, cloned.right, target)

    def getTargetCopy_bfs(self, original: "TreeNode", cloned: "TreeNode", target: "TreeNode") -> "TreeNode":
        """
        Interview explanation:
        Alternate BFS paired queues on original and cloned.

        Algorithm:
        - Queue pairs; when o is target return c

        Complexity: O(n) time, O(w) space.
        """
        from collections import deque
        q = deque([(original, cloned)])
        while q:
            o, c = q.popleft()
            if o is target:
                return c
            if o.left:
                q.append((o.left, c.left))
            if o.right:
                q.append((o.right, c.right))
        return None
# @lc code=end
