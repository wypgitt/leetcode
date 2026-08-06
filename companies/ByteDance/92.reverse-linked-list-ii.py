#
# @lc app=leetcode id=92 lang=python3
#
# [92] Reverse Linked List II
#
# https://leetcode.com/problems/reverse-linked-list-ii/description/
#
# algorithms
# Medium (51.46%)
# Likes:    12979
# Dislikes: 788
# Total Accepted:    1.3M
# Total Submissions: 2.6M
# Testcase Example:  '[1,2,3,4,5]\n2\n4'
#
# Given the head of a singly linked list and two integers left and right where
# left <= right, reverse the nodes of the list from position left to position
# right, and return the reversed list.
# 
# 
# Example 1:
# 
# 
# Input: head = [1,2,3,4,5], left = 2, right = 4
# Output: [1,4,3,2,5]
# 
# 
# Example 2:
# 
# 
# Input: head = [5], left = 1, right = 1
# Output: [5]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the list is n.
# 1 <= n <= 500
# -500 <= Node.val <= 500
# 1 <= left <= right <= n
# 
# 
# 
# Follow up: Could you do it in one pass?
#

# @lc code=start
from typing import List, Optional
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        """
        Interview explanation:
        Reverse only the sublist [left, right] in place. A dummy node handles
        left == 1. Move prev to the node before the sublist, then use head
        insertion: repeatedly take the node after cur and insert it right after
        prev. This reverses the segment without extra nodes.

        Edge cases and tests:
        - left == right leaves the list unchanged.
        - Reversing from the head works because of dummy.
        - Reversing to the tail works because pointers naturally terminate.

        Complexity: O(n) time, O(1) space.
        """
        dummy = ListNode(0, head)
        prev = dummy
        for _ in range(left - 1):
            prev = prev.next

        cur = prev.next
        for _ in range(right - left):
            move = cur.next
            cur.next = move.next
            move.next = prev.next
            prev.next = move

        return dummy.next
# @lc code=end


