#
# @lc app=leetcode id=369 lang=python3
#
# [369] Plus One Linked List
#
# https://leetcode.com/problems/plus-one-linked-list/description/
#
# algorithms
# Medium (61.21%)
# Likes:    968
# Dislikes: 48
# Total Accepted:    88.7K
# Total Submissions: 144.9K
# Testcase Example:  "[1,2,3]"
#
#
# Given a non-negative integer represented as a linked list of digits,
# plus one to the integer.
#
# The digits are stored such that the most significant digit is at the
# head of the list.
#
# Example 1:
#
# Input: head = [1,2,3]
# Output: [1,2,4]
#
# Example 2:
#
# Input: head = [0]
# Output: [1]
#
# Constraints:
#
# The number of nodes in the linked list is in the range [1, 100].
#
# 0 <= Node.val <= 9
#
# The number represented by the linked list does not contain leading zeros
# except for the zero itself.
#
# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def plusOne(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Sentinel + find rightmost non-9 digit: increment it and set all
        following 9s to 0. If head was all 9s, sentinel becomes the new 1.

        Algorithm:
        - dummy = ListNode(0); dummy.next = head.
        - not_nine = dummy; scan: if node.val != 9, not_nine = node.
        - not_nine.val += 1; set all after to 0.
        - Return dummy if dummy.val else dummy.next.

        Complexity: O(n) time, O(1) space.
        """
        dummy = ListNode(0)
        dummy.next = head
        not_nine = dummy
        node = head
        while node:
            if node.val != 9:
                not_nine = node
            node = node.next
        not_nine.val += 1
        node = not_nine.next
        while node:
            node.val = 0
            node = node.next
        return dummy if dummy.val else dummy.next

    def plusOne_reverse(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Alternate: reverse list, add one with carry from LSD, reverse back.

        Complexity: O(n) time, O(1) space.
        """
        def reverse(node: Optional[ListNode]) -> Optional[ListNode]:
            prev = None
            while node:
                nxt = node.next
                node.next = prev
                prev = node
                node = nxt
            return prev

        head = reverse(head)
        cur = head
        carry = 1
        prev = None
        while cur and carry:
            cur.val += carry
            carry = cur.val // 10
            cur.val %= 10
            prev = cur
            cur = cur.next
        if carry:
            prev.next = ListNode(1)
        return reverse(head)
# @lc code=end
