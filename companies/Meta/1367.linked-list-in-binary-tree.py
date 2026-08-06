#
# @lc app=leetcode id=1367 lang=python3
#
# [1367] Linked List in Binary Tree
#
# https://leetcode.com/problems/linked-list-in-binary-tree/description/
#
# algorithms
# Medium (52.0%)
# Likes:    3042
# Dislikes: 90
# Total Accepted:    212K
# Total Submissions: 409K
# Testcase Example:  "[4,2,8]"
#
# Given a binary tree root and a linked list with head as the first node.
#
# Return True if all the elements in the linked list starting from the head
# correspond to some downward path connected in the binary tree otherwise
# return False.
#
# In this context downward path means a path that starts at some node and goes
# downwards.
#
# Example 1:
#
# Input: head = [4,2,8], root =
# [1,4,4,null,2,2,null,1,null,6,8,null,null,null,null,1,3]
# Output: true
# Explanation: Nodes in blue form a subpath in the binary Tree.
#
# Example 2:
#
# Input: head = [1,4,2,6], root =
# [1,4,4,null,2,2,null,1,null,6,8,null,null,null,null,1,3]
# Output: true
#
# Example 3:
#
# Input: head = [1,4,2,6,8], root =
# [1,4,4,null,2,2,null,1,null,6,8,null,null,null,null,1,3]
# Output: false
# Explanation: There is no path in the binary tree that contains all the
# elements of the linked list from head.
#
# Constraints:
#
# The number of nodes in the tree will be in the range [1, 2500].
#
# The number of nodes in the list will be in the range [1, 100].
#
# 1 <= Node.val <= 100 for each node in the linked list and binary tree.
#

# @lc code=start

from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def isSubPath(self, head: Optional[ListNode], root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Check if linked list is a downward path in the binary tree. DFS from
        every tree node trying to match the list consecutively.

        Algorithm:
        - dfs(tree, list): if not list True; if not tree False; match val and
          continue left/right with list.next
        - Walk tree: try dfs at each node or recurse children

        Complexity: O(N*L) time worst-case, O(H) space.
        """
        def match(node: Optional[TreeNode], cur: Optional[ListNode]) -> bool:
            if not cur:
                return True
            if not node or node.val != cur.val:
                return False
            return match(node.left, cur.next) or match(node.right, cur.next)

        def dfs(node: Optional[TreeNode]) -> bool:
            if not node:
                return False
            return match(node, head) or dfs(node.left) or dfs(node.right)

        return dfs(root)

    def isSubPath_kmp(self, head: Optional[ListNode], root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Alternate KMP: build pattern from list and LPS; DFS tree with KMP state
        to avoid re-checking prefixes on mismatch.

        Algorithm:
        - pattern from list; compute pi (LPS)
        - dfs(node, j): advance j on match; if j==len True; recurse children

        Complexity: O(N+L) time typical with KMP, O(H+L) space.
        """
        pat = []
        cur = head
        while cur:
            pat.append(cur.val)
            cur = cur.next
        m = len(pat)
        pi = [0] * m
        j = 0
        for i in range(1, m):
            while j and pat[i] != pat[j]:
                j = pi[j - 1]
            if pat[i] == pat[j]:
                j += 1
                pi[i] = j

        def dfs(node: Optional[TreeNode], j: int) -> bool:
            if not node:
                return False
            while j and node.val != pat[j]:
                j = pi[j - 1]
            if node.val == pat[j]:
                j += 1
            if j == m:
                return True
            return dfs(node.left, j) or dfs(node.right, j)

        return dfs(root, 0)
# @lc code=end
