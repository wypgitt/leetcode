#
# @lc app=leetcode id=445 lang=python3
#
# [445] Add Two Numbers II
#
# https://leetcode.com/problems/add-two-numbers-ii/description/
#
# algorithms
# Medium (62.91%)
# Likes:    6213
# Dislikes: 303
# Total Accepted:    598K
# Total Submissions: 951K
# Testcase Example:  "[7,2,4,3]"
#
# You are given two non-empty linked lists representing two non-negative
# integers. The most significant digit comes first and each of their nodes
# contains a single digit. Add the two numbers and return the sum as a linked
# list.
#
# You may assume the two numbers do not contain any leading zero, except the
# number 0 itself.
#
# Example 1:
#
# Input: l1 = [7,2,4,3], l2 = [5,6,4]
# Output: [7,8,0,7]
#
# Example 2:
#
# Input: l1 = [2,4,3], l2 = [5,6,4]
# Output: [8,0,7]
#
# Example 3:
#
# Input: l1 = [0], l2 = [0]
# Output: [0]
#
# Constraints:
#
# The number of nodes in each linked list is in the range [1, 100].
#
# 0 <= Node.val <= 9
#
# It is guaranteed that the list represents a number that does not have leading
# zeros.
#
# Follow up: Could you solve it without reversing the input lists?
#

# @lc code=start

from typing import Optional
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Stack approach (no reverse of inputs needed for the algorithm): push
        digits of both lists, then pop and add with carry, building the result
        list from least significant digit via prepending.

        Algorithm:
        - Push all of l1 and l2 onto stacks.
        - While stacks or carry: sum pops + carry; prepend new node.
        - Return head.

        Complexity: O(m+n) time and space.
        """
        s1, s2 = [], []
        while l1:
            s1.append(l1.val)
            l1 = l1.next
        while l2:
            s2.append(l2.val)
            l2 = l2.next
        carry = 0
        head = None
        while s1 or s2 or carry:
            a = s1.pop() if s1 else 0
            b = s2.pop() if s2 else 0
            total = a + b + carry
            node = ListNode(total % 10)
            node.next = head
            head = node
            carry = total // 10
        return head

    def addTwoNumbersReverse(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Alternate: reverse both lists, add like Add Two Numbers I, reverse result.

        Algorithm:
        - reverse(l1), reverse(l2); add with carry; reverse sum list.

        Complexity: O(m+n) time, O(1) extra space besides output.
        """
        def reverse(node: Optional[ListNode]) -> Optional[ListNode]:
            prev = None
            while node:
                nxt = node.next
                node.next = prev
                prev = node
                node = nxt
            return prev

        l1, l2 = reverse(l1), reverse(l2)
        carry = 0
        dummy = ListNode(0)
        cur = dummy
        while l1 or l2 or carry:
            a = l1.val if l1 else 0
            b = l2.val if l2 else 0
            s = a + b + carry
            cur.next = ListNode(s % 10)
            cur = cur.next
            carry = s // 10
            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next
        return reverse(dummy.next)
# @lc code=end
