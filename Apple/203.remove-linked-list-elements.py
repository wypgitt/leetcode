#
# @lc app=leetcode id=203 lang=python3
#
# [203] Remove Linked List Elements
#
# https://leetcode.com/problems/remove-linked-list-elements/description/
#
# algorithms
# Easy (55.12%)
# Likes:    9142
# Dislikes: 294
# Total Accepted:    1.7M
# Total Submissions: 3.0M
# Testcase Example:  "[1,2,6,3,4,5,6]"
#
# Given the head of a linked list and an integer val, remove all the nodes of
# the linked list that has Node.val == val, and return the new head.
#
# Example 1:
#
# Input: head = [1,2,6,3,4,5,6], val = 6
# Output: [1,2,3,4,5]
#
# Example 2:
#
# Input: head = [], val = 1
# Output: []
#
# Example 3:
#
# Input: head = [7,7,7,7], val = 7
# Output: []
#
# Constraints:
#
# The number of nodes in the list is in the range [0, 10^4].
#
# 1 <= Node.val <= 50
#
# 0 <= val <= 50
#

# @lc code=start
from typing import Optional
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeElements(self, head: Optional[ListNode], val: int) -> Optional[ListNode]:
        """
        Interview explanation:
        Use a sentinel (dummy) node before head so deleting the first node is
        the same as deleting any other: walk a predecessor and skip matches.

        Algorithm:
        - Create dummy -> head; cur = dummy.
        - While cur.next exists: if cur.next.val == val, unlink it; else advance.
        - Return dummy.next.

        Complexity: O(n) time, O(1) space.
        """
        dummy = ListNode(0, head)
        cur = dummy
        while cur.next:
            if cur.next.val == val:
                cur.next = cur.next.next
            else:
                cur = cur.next
        return dummy.next
# @lc code=end
