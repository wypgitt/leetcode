#
# @lc app=leetcode id=206 lang=python3
#
# [206] Reverse Linked List
#
# https://leetcode.com/problems/reverse-linked-list/description/
#
# algorithms
# Easy (80.89%)
# Likes:    24797
# Dislikes: 590
# Total Accepted:    6.6M
# Total Submissions: 8.1M
# Testcase Example:  "[1,2,3,4,5]"
#
# Given the head of a singly linked list, reverse the list, and return the
# reversed list.
#
# Example 1:
#
# Input: head = [1,2,3,4,5]
# Output: [5,4,3,2,1]
#
# Example 2:
#
# Input: head = [1,2]
# Output: [2,1]
#
# Example 3:
#
# Input: head = []
# Output: []
#
# Constraints:
#
# The number of nodes in the list is the range [0, 5000].
#
# -5000 <= Node.val <= 5000
#
# Follow up: A linked list can be reversed either iteratively or recursively.
# Could you implement both?
#

# @lc code=start
from typing import Optional
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Iterative reverse: walk the list and reverse each next pointer in place.
        Keep prev as the head of the already-reversed prefix.

        Algorithm:
        - prev = None, cur = head.
        - While cur: save next, set cur.next = prev, advance prev/cur.
        - Return prev.

        Complexity: O(n) time, O(1) space.
        """
        prev = None
        cur = head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        return prev

    def reverseListRecursive(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Recursively reverse the tail, then fix the current node's link:
        head.next.next = head; head.next = None.

        Algorithm:
        - Base: empty or single node returns itself.
        - new_head = reverse(head.next); rewire head; return new_head.

        Complexity: O(n) time, O(n) recursion stack.
        """
        if not head or not head.next:
            return head
        new_head = self.reverseListRecursive(head.next)
        head.next.next = head
        head.next = None
        return new_head
# @lc code=end
