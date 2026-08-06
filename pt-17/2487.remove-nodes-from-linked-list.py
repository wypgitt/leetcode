#
# @lc app=leetcode id=2487 lang=python3
#
# [2487] Remove Nodes From Linked List
#
# https://leetcode.com/problems/remove-nodes-from-linked-list/description/
#
# algorithms
# Medium (75.13%)
# Likes:    2461
# Dislikes: 88
# Total Accepted:    284.8K
# Total Submissions: 379.1K
# Testcase Example:  "[5,2,13,3,8]"
#
# You are given the head of a linked list.
#
# Remove every node which has a node with a greater value anywhere to the right
# side of it.
#
# Return the head of the modified linked list.
#
#
#
# Example 1:
#
# Input: head = [5,2,13,3,8]
# Output: [13,8]
# Explanation: The nodes that should be removed are 5, 2 and 3.
# - Node 13 is to the right of node 5.
# - Node 13 is to the right of node 2.
# - Node 8 is to the right of node 3.
#
# Example 2:
#
# Input: head = [1,1,1,1]
# Output: [1,1,1,1]
# Explanation: Every node has value 1, so no nodes are removed.
#
#
#
# Constraints:
#
#
# The number of the nodes in the given list is in the range [1, 10^5].
#
#
# 1 <= Node.val <= 10^5
#

# @lc code=start
from typing import Optional


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeNodes(self, head: Optional["ListNode"]) -> Optional["ListNode"]:
        """
        Interview explanation:
        Delete every node with a strictly greater node somewhere to its right.

        Algorithm:
        - Reverse list; keep running max, drop smaller; reverse back.
          Or monotonic decreasing stack of nodes.

        Complexity: O(n) time, O(1) space (reverse).
        """
        def rev(node):
            prev = None
            while node:
                nxt = node.next
                node.next = prev
                prev = node
                node = nxt
            return prev

        head = rev(head)
        cur = head
        mx = head.val
        while cur and cur.next:
            if cur.next.val < mx:
                cur.next = cur.next.next
            else:
                cur = cur.next
                mx = cur.val
        return rev(head)

    def removeNodes_stack(self, head: Optional["ListNode"]) -> Optional["ListNode"]:
        """
        Interview explanation:
        Alternate monotonic stack of decreasing values.

        Algorithm:
        - Push nodes; pop while stack.top.val < current.val; link survivors.

        Complexity: O(n) time, O(n) space.
        """
        stack = []
        cur = head
        while cur:
            while stack and stack[-1].val < cur.val:
                stack.pop()
            if stack:
                stack[-1].next = cur
            stack.append(cur)
            cur = cur.next
        if stack:
            stack[-1].next = None
        return stack[0] if stack else None
# @lc code=end

