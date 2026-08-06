#
# @lc app=leetcode id=25 lang=python3
#
# [25] Reverse Nodes in k-Group
#
# https://leetcode.com/problems/reverse-nodes-in-k-group/description/
#
# algorithms
# Hard (66.85%)
# Likes:    15879
# Dislikes: 812
# Total Accepted:    1.6M
# Total Submissions: 2.5M
# Testcase Example:  "[1,2,3,4,5]"
#
# Given the head of a linked list, reverse the nodes of the list k at a time,
# and return the modified list.
#
# k is a positive integer and is less than or equal to the length of the linked
# list. If the number of nodes is not a multiple of k then left-out nodes, in
# the end, should remain as it is.
#
# You may not alter the values in the list's nodes, only nodes themselves may
# be changed.
#
# Example 1:
#
# Input: head = [1,2,3,4,5], k = 2
# Output: [2,1,4,3,5]
#
# Example 2:
#
# Input: head = [1,2,3,4,5], k = 3
# Output: [3,2,1,4,5]
#
# Constraints:
#
# The number of nodes in the list is n.
#
# 1 <= k <= n <= 5000
#
# 0 <= Node.val <= 1000
#
# Follow-up: Can you solve the problem in O(1) extra memory space?
#

# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        """
        Interview explanation:
        Reverse each contiguous block of exactly k nodes in place. Walk ahead
        to ensure a full group exists; if not, leave the remainder untouched.

        Algorithm:
        - Use a dummy node before head; group_prev points before the current
          group.
        - Count k nodes ahead; if fewer than k remain, stop.
        - Reverse the k-node segment with standard 3-pointer reverse.
        - Relink group_prev.next to the new head and the group's old head to
          the next segment; advance group_prev.

        Complexity: O(n) time, O(1) extra space.
        """
        dummy = ListNode(0, head)
        group_prev = dummy

        while True:
            kth = group_prev
            for _ in range(k):
                kth = kth.next
                if not kth:
                    return dummy.next

            group_next = kth.next
            prev, curr = group_next, group_prev.next
            for _ in range(k):
                nxt = curr.next
                curr.next = prev
                prev = curr
                curr = nxt

            tail = group_prev.next
            group_prev.next = prev
            group_prev = tail
# @lc code=end
