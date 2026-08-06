#
# @lc app=leetcode id=2046 lang=python3
#
# [2046] Sort Linked List Already Sorted Using Absolute Values
#
# https://leetcode.com/problems/sort-linked-list-already-sorted-using-absolute-values/description/
#
# algorithms
# Medium (67.08%)
# Likes:    176
# Dislikes: 3
# Total Accepted:    11.4K
# Total Submissions: 17K
# Testcase Example:  "[0,2,-5,5,10,-10]"
#
#
# Given the head of a singly linked list that is sorted in non-decreasing
# order using the absolute values of its nodes, return the list sorted in
# non-decreasing order using the actual values of its nodes.
#
# Example 1:
#
# Input: head = [0,2,-5,5,10,-10]
# Output: [-10,-5,0,2,5,10]
# Explanation:
# The list sorted in non-descending order using the absolute values of the
# nodes is [0,2,-5,5,10,-10].
# The list sorted in non-descending order using the actual values is
# [-10,-5,0,2,5,10].
#
# Example 2:
#
# Input: head = [0,1,2]
# Output: [0,1,2]
# Explanation:
# The linked list is already sorted in non-decreasing order.
#
# Example 3:
#
# Input: head = [1]
# Output: [1]
# Explanation:
# The linked list is already sorted in non-decreasing order.
#
# Constraints:
#
# The number of nodes in the list is the range [1, 10^5].
#
# -5000 <= Node.val <= 5000
#
# head is sorted in non-decreasing order using the absolute value of its
# nodes.
#
# Follow up:
#
# Can you think of a solution with O(n) time complexity?
#
# @lc code=start
from typing import Optional


# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        """
        Interview explanation:
        Singly linked list node used by the premium sort problem.

        Algorithm:
        - Store val and next pointer.

        Complexity: O(1).
        """
        self.val = val
        self.next = next


class Solution:
    def sortLinkedList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Premium: list is sorted by absolute value. Resort into nondecreasing
        order. Negatives appear in reverse relative order — splice them to front.

        Algorithm:
        - Traverse; when node.val < 0, detach and insert at new head; else advance.

        Complexity: O(n) time, O(1) space.
        """
        if not head:
            return head
        prev = head
        cur = head.next
        while cur:
            if cur.val < 0:
                prev.next = cur.next
                cur.next = head
                head = cur
                cur = prev.next
            else:
                prev = cur
                cur = cur.next
        return head
# @lc code=end
