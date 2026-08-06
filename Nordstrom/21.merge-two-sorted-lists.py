#
# @lc app=leetcode id=21 lang=python3
#
# [21] Merge Two Sorted Lists
#
# https://leetcode.com/problems/merge-two-sorted-lists/description/
#
# algorithms
# Easy (68.69%)
# Likes:    25249
# Dislikes: 2456
# Total Accepted:    6.5M
# Total Submissions: 9.5M
# Testcase Example:  "[1,2,4]"
#
# You are given the heads of two sorted linked lists list1 and list2.
#
# Merge the two lists into one sorted list. The list should be made by splicing
# together the nodes of the first two lists.
#
# Return the head of the merged linked list.
#
# Example 1:
#
# Input: list1 = [1,2,4], list2 = [1,3,4]
# Output: [1,1,2,3,4,4]
#
# Example 2:
#
# Input: list1 = [], list2 = []
# Output: []
#
# Example 3:
#
# Input: list1 = [], list2 = [0]
# Output: [0]
#
# Constraints:
#
# The number of nodes in both lists is in the range [0, 50].
#
# -100 <= Node.val <= 100
#
# Both list1 and list2 are sorted in non-decreasing order.
#

# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def mergeTwoLists(
        self, list1: Optional[ListNode], list2: Optional[ListNode]
    ) -> Optional[ListNode]:
        """
        Interview explanation:
        Merge two already-sorted linked lists into one sorted list by splicing
        existing nodes (no new value nodes needed beyond a dummy head).

        Algorithm:
        - Create a dummy node and a `tail` pointer.
        - While both lists are non-empty, append the smaller head to `tail`.
        - Attach the remaining non-empty list.
        - Return dummy.next.

        Complexity: O(m + n) time, O(1) space.
        """
        dummy = ListNode()
        tail = dummy

        while list1 and list2:
            if list1.val <= list2.val:
                tail.next = list1
                list1 = list1.next
            else:
                tail.next = list2
                list2 = list2.next
            tail = tail.next

        tail.next = list1 or list2
        return dummy.next

    def mergeTwoListsRecursive(
        self, list1: Optional[ListNode], list2: Optional[ListNode]
    ) -> Optional[ListNode]:
        """
        Interview explanation:
        Recursively choose the smaller head and merge the rest onto its next.
        Clean to express, but uses call-stack space.

        Algorithm:
        - If either list is empty, return the other.
        - If list1.val <= list2.val, set list1.next to merge(list1.next, list2)
          and return list1.
        - Otherwise set list2.next to merge(list1, list2.next) and return list2.

        Complexity: O(m + n) time, O(m + n) space for the call stack.
        """
        if not list1:
            return list2
        if not list2:
            return list1

        if list1.val <= list2.val:
            list1.next = self.mergeTwoListsRecursive(list1.next, list2)
            return list1

        list2.next = self.mergeTwoListsRecursive(list1, list2.next)
        return list2
# @lc code=end
