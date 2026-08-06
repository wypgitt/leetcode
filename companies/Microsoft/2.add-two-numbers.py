#
# @lc app=leetcode id=2 lang=python3
#
# [2] Add Two Numbers
#
# https://leetcode.com/problems/add-two-numbers/description/
#
# algorithms
# Medium (48.40%)
# Likes:    36817
# Dislikes: 7263
# Total Accepted:    7M
# Total Submissions: 14.5M
# Testcase Example:  '[2,4,3]\n[5,6,4]'
#
# You are given two non-empty linked lists representing two non-negative
# integers. The digits are stored in reverse order, and each of their nodes
# contains a single digit. Add the two numbers and return the sum as a linked
# list.
# 
# You may assume the two numbers do not contain any leading zero, except the
# number 0 itself.
# 
# 
# Example 1:
# 
# 
# Input: l1 = [2,4,3], l2 = [5,6,4]
# Output: [7,0,8]
# Explanation: 342 + 465 = 807.
# 
# 
# Example 2:
# 
# 
# Input: l1 = [0], l2 = [0]
# Output: [0]
# 
# 
# Example 3:
# 
# 
# Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
# Output: [8,9,9,9,0,0,0,1]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in each linked list is in the range [1, 100].
# 0 <= Node.val <= 9
# It is guaranteed that the list represents a number that does not have leading
# zeros.
# 
# 
#

# @lc code=start
from typing import List, Optional
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        The lists store digits from least significant to most significant, so
        addition can be simulated exactly as elementary school addition from
        left to right over the linked lists. A dummy head is the simplest data
        structure choice because it lets us append result nodes uniformly
        without special-casing the first digit.

        Algorithm:
        1. Walk l1 and l2 while either still has digits or there is a carry.
        2. Add the current digit values plus carry.
        3. Store total % 10 in a new node and carry total // 10 forward.
        4. Advance whichever input nodes exist.

        Edge cases and tests:
        - [0] + [0] returns [0].
        - Lists with different lengths continue using 0 for the missing side.
        - A final carry, for example 999 + 1, creates one extra node.

        Complexity: O(max(m, n)) time and O(max(m, n)) output space.
        """
        dummy = ListNode(0)
        tail = dummy
        carry = 0

        while l1 or l2 or carry:
            total = carry
            if l1:
                total += l1.val
                l1 = l1.next
            if l2:
                total += l2.val
                l2 = l2.next

            carry, digit = divmod(total, 10)
            tail.next = ListNode(digit)
            tail = tail.next

        return dummy.next
# @lc code=end


