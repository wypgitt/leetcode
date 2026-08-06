#
# @lc app=leetcode id=2816 lang=python3
#
# [2816] Double a Number Represented as a Linked List
#
# https://leetcode.com/problems/double-a-number-represented-as-a-linked-list/description/
#
# algorithms
# Medium (61.34%)
# Likes:    1293
# Dislikes: 32
# Total Accepted:    207.5K
# Total Submissions: 338.2K
# Testcase Example:  "[1,8,9]"
#
#
# You are given the head of a non-empty linked list representing a
# non-negative integer without leading zeroes.
#
# Return the head of the linked list after doubling it.
#
# Example 1:
#
# Input: head = [1,8,9]
# Output: [3,7,8]
# Explanation: The figure above corresponds to the given linked list which
# represents the number 189. Hence, the returned linked list represents
# the number 189 * 2 = 378.
#
# Example 2:
#
# Input: head = [9,9,9]
# Output: [1,9,9,8]
# Explanation: The figure above corresponds to the given linked list which
# represents the number 999. Hence, the returned linked list reprersents
# the number 999 * 2 = 1998.
#
# Constraints:
#
# The number of nodes in the list is in the range [1, 10^4]
#
# 0 <= Node.val <= 9
#
# The input is generated such that the list represents a number that does
# not have leading zeros, except the number 0 itself.
#

# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

try:
    ListNode  # type: ignore[name-defined]
except NameError:

    class ListNode:  # type: ignore[no-redef]
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next


class Solution:
    def doubleIt(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Linked list is a big-endian non-negative integer; return 2 * number
        as a linked list.

        Algorithm:
        - If head.val >= 5, prepend 0 so a new leading digit can appear.
        - Left-to-right: write (2*val)%10; add 1 if the next digit >= 5
          (that next digit will produce a carry when doubled).

        Complexity: O(n) time, O(1) extra space.
        """
        if head.val >= 5:
            head = ListNode(0, head)
        cur = head
        while cur:
            cur.val = (cur.val * 2) % 10
            if cur.next and cur.next.val >= 5:
                cur.val += 1
            cur = cur.next
        return head

    def doubleIt_reverse(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Alternate: reverse, double with carry from LSD, reverse back.

        Algorithm:
        - Reverse list; multiply by 2 with carry; reverse again; handle final carry.

        Complexity: O(n) time, O(1) space.
        """

        def rev(node: Optional[ListNode]) -> Optional[ListNode]:
            prev = None
            while node:
                nxt = node.next
                node.next = prev
                prev = node
                node = nxt
            return prev

        head = rev(head)
        cur = head
        carry = 0
        prev = None
        while cur:
            val = cur.val * 2 + carry
            cur.val = val % 10
            carry = val // 10
            prev = cur
            cur = cur.next
        if carry and prev:
            prev.next = ListNode(carry)
        return rev(head)
# @lc code=end
