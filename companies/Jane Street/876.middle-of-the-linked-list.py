#
# @lc app=leetcode id=876 lang=python3
#
# [876] Middle of the Linked List
#
# https://leetcode.com/problems/middle-of-the-linked-list/description/
#
# algorithms
# Easy (82.22%)
# Likes:    13404
# Dislikes: 451
# Total Accepted:    3.2M
# Total Submissions: 3.9M
# Testcase Example:  "[1,2,3,4,5]"
#
# Given the head of a singly linked list, return the middle node of the linked
# list.
#
# If there are two middle nodes, return the second middle node.
#
# Example 1:
#
# Input: head = [1,2,3,4,5]
# Output: [3,4,5]
# Explanation: The middle node of the list is node 3.
#
# Example 2:
#
# Input: head = [1,2,3,4,5,6]
# Output: [4,5,6]
# Explanation: Since the list has two middle nodes with values 3 and 4, we
# return the second one.
#
# Constraints:
#
# The number of nodes in the list is in the range [1, 100].
#
# 1 <= Node.val <= 100
#

# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Floyd tortoise/hare: slow moves 1, fast moves 2; when fast ends, slow
        is at middle (second middle for even length).

        Algorithm (Floyd):
        - slow=fast=head; while fast and fast.next: slow=slow.next, fast=fast.next.next.

        Complexity: O(n) time, O(1) space.
        """
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        return slow

    def middleNode_count(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Alternate: count length, then advance n//2 steps from head.

        Algorithm:
        - Walk to count n; walk n//2 from head.

        Complexity: O(n) time, O(1) space.
        """
        n = 0
        cur = head
        while cur:
            n += 1
            cur = cur.next
        cur = head
        for _ in range(n // 2):
            cur = cur.next
        return cur
# @lc code=end

