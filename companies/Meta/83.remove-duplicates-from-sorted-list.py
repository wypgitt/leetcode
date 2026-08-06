#
# @lc app=leetcode id=83 lang=python3
#
# [83] Remove Duplicates from Sorted List
#
# https://leetcode.com/problems/remove-duplicates-from-sorted-list/description/
#
# algorithms
# Easy (57.27%)
# Likes:    10003
# Dislikes: 380
# Total Accepted:    2.5M
# Total Submissions: 4.4M
# Testcase Example:  "[1,1,2]"
#
# Given the head of a sorted linked list, delete all duplicates such that each
# element appears only once. Return the linked list sorted as well.
#
# Example 1:
#
# Input: head = [1,1,2]
# Output: [1,2]
#
# Example 2:
#
# Input: head = [1,1,2,3,3]
# Output: [1,2,3]
#
# Constraints:
#
# The number of nodes in the list is in the range [0, 300].
#
# -100 <= Node.val <= 100
#
# The list is guaranteed to be sorted in ascending order.
#

# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Sorted list => duplicates are adjacent. Walk once and skip equal
        neighbors.

        Algorithm:
        - Start at head with pointer `current`.
        - While current and current.next exist:
          - If values equal, bypass current.next.
          - Else advance current.
        - Return head.

        Complexity: O(n) time, O(1) space.
        """
        current = head
        while current and current.next:
            if current.val == current.next.val:
                current.next = current.next.next
            else:
                current = current.next
        return head
# @lc code=end
