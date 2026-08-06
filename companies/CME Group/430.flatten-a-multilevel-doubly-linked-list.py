#
# @lc app=leetcode id=430 lang=python3
#
# [430] Flatten a Multilevel Doubly Linked List
#
# https://leetcode.com/problems/flatten-a-multilevel-doubly-linked-list/description/
#
# algorithms
# Medium (63.24%)
# Likes:    5512
# Dislikes: 352
# Total Accepted:    457K
# Total Submissions: 723K
# Testcase Example:  "[1,2,3,4,5,6,null,null,null,7,8,9,10,null,null,11,12]"
#
# You are given a doubly linked list, which contains nodes that have a next
# pointer, a previous pointer, and an additional child pointer. This child
# pointer may or may not point to a separate doubly linked list, also
# containing these special nodes. These child lists may have one or more
# children of their own, and so on, to produce a multilevel data structure as
# shown in the example below.
#
# Given the head of the first level of the list, flatten the list so that all
# the nodes appear in a single-level, doubly linked list. Let curr be a node
# with a child list. The nodes in the child list should appear after curr and
# before curr.next in the flattened list.
#
# Return the head of the flattened list. The nodes in the list must have all of
# their child pointers set to null.
#
# Example 1:
#
# Input: head = [1,2,3,4,5,6,null,null,null,7,8,9,10,null,null,11,12]
# Output: [1,2,3,7,8,11,12,9,10,4,5,6]
# Explanation: The multilevel linked list in the input is shown.
# After flattening the multilevel linked list it becomes:
#
# Example 2:
#
# Input: head = [1,2,null,3]
# Output: [1,3,2]
# Explanation: The multilevel linked list in the input is shown.
# After flattening the multilevel linked list it becomes:
#
# Example 3:
#
# Input: head = []
# Output: []
# Explanation: There could be empty list in the input.
#
# Constraints:
#
# The number of Nodes will not exceed 1000.
#
# 1 <= Node.val <= 10^5
#
# How the multilevel linked list is represented in test cases:
#
# We use the multilevel linked list from Example 1 above:
#
# 1---2---3---4---5---6--NULL
# |
# 7---8---9---10--NULL
# |
# 11--12--NULL
#
# The serialization of each level is as follows:
#
# [1,2,3,4,5,6,null]
# [7,8,9,10,null]
# [11,12,null]
#
# To serialize all levels together, we will add nulls in each level to signify
# no node connects to the upper node of the previous level. The serialization
# becomes:
#
# [1, 2, 3, 4, 5, 6, null]
# |
# [null, null, 7, 8, 9, 10, null]
# |
# [ null, 11, 12, null]
#
# Merging the serialization of each level and removing trailing nulls we
# obtain:
#
# [1,2,3,4,5,6,null,null,null,7,8,9,10,null,null,11,12]
#

# @lc code=start

from typing import Optional

"""
# Definition for a Node.
class Node:
    def __init__(self, val, prev, next, child):
        self.val = val
        self.prev = prev
        self.next = next
        self.child = child
"""


class Solution:
    def flatten(self, head: "Optional[Node]") -> "Optional[Node]":
        """
        Interview explanation:
        DFS/stack flatten: when a node has a child, splice the flattened child
        list between node and node.next, then clear child pointer.

        Algorithm:
        - Iterate with curr; if curr.child: save next; connect child as next;
          find child-list tail; link tail to saved next; child=None.
        - Return head.

        Complexity: O(n) time, O(1) extra space (iterative splice).
        """
        if not head:
            return None
        curr = head
        while curr:
            if curr.child:
                nxt = curr.next
                child = curr.child
                curr.next = child
                child.prev = curr
                curr.child = None
                tail = child
                while tail.next:
                    tail = tail.next
                if nxt:
                    tail.next = nxt
                    nxt.prev = tail
            curr = curr.next
        return head

    def flattenDFS(self, head: "Optional[Node]") -> "Optional[Node]":
        """
        Interview explanation:
        Alternate recursive: flatten returns the tail of the flattened segment;
        when child exists, recurse child then rest, wire pointers.

        Algorithm:
        - dfs(node) flattens from node and returns tail.
        - On child: link node->child, flatten child get mid_tail, link to next.

        Complexity: O(n) time, O(d) recursion depth (nesting depth).
        """
        def dfs(node: "Node") -> "Node":
            curr = node
            last = node
            while curr:
                nxt = curr.next
                if curr.child:
                    child_head = curr.child
                    child_tail = dfs(child_head)
                    curr.next = child_head
                    child_head.prev = curr
                    curr.child = None
                    if nxt:
                        child_tail.next = nxt
                        nxt.prev = child_tail
                    last = child_tail
                    curr = nxt
                else:
                    last = curr
                    curr = nxt
            return last

        if head:
            dfs(head)
        return head
# @lc code=end
