#
# @lc app=leetcode id=1171 lang=python3
#
# [1171] Remove Zero Sum Consecutive Nodes from Linked List
#
# https://leetcode.com/problems/remove-zero-sum-consecutive-nodes-from-linked-list/description/
#
# algorithms
# Medium (53.26%)
# Likes:    3542
# Dislikes: 226
# Total Accepted:    191K
# Total Submissions: 359K
# Testcase Example:  "[1,2,-3,3,1]"
#
# Given the head of a linked list, we repeatedly delete consecutive sequences
# of nodes that sum to 0 until there are no such sequences.
#
# After doing so, return the head of the final linked list. You may return any
# such answer.
#
# (Note that in the examples below, all sequences are serializations of
# ListNode objects.)
#
# Example 1:
#
# Input: head = [1,2,-3,3,1]
# Output: [3,1]
# Note: The answer [1,2,1] would also be accepted.
#
# Example 2:
#
# Input: head = [1,2,3,-3,4]
# Output: [1,2,4]
#
# Example 3:
#
# Input: head = [1,2,3,-3,-2]
# Output: [1]
#
# Constraints:
#
# The given linked list will contain between 1 and 1000 nodes.
#
# Each node in the linked list has -1000 <= node.val <= 1000.
#

# @lc code=start

from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
try:
    ListNode  # type: ignore[name-defined]
except NameError:
    class ListNode:
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next


class Solution:
    def removeZeroSumSublists(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Prefix sums: if two nodes share the same prefix sum, the nodes between
        them sum to 0 and can be removed. Map each prefix sum to the latest node
        with that sum; second pass rewires next pointers past zero-sum spans.

        Algorithm (prefix sum + hash map):
        - Dummy before head; compute prefix while recording last node for each sum.
        - Walk again: for each node with prefix p, node.next = seen[p].next
          (skip the zero-sum segment), update p += next.val.

        Complexity: O(n) time, O(n) space.
        """
        dummy = ListNode(0)
        dummy.next = head
        prefix = 0
        seen = {0: dummy}
        cur = head
        while cur:
            prefix += cur.val
            seen[prefix] = cur
            cur = cur.next

        prefix = 0
        cur = dummy
        while cur:
            prefix += cur.val
            cur.next = seen[prefix].next
            cur = cur.next
        return dummy.next
# @lc code=end
