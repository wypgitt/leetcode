#
# @lc app=leetcode id=1290 lang=python3
#
# [1290] Convert Binary Number in a Linked List to Integer
#
# https://leetcode.com/problems/convert-binary-number-in-a-linked-list-to-integer/description/
#
# algorithms
# Easy (82.39%)
# Likes:    4711
# Dislikes: 179
# Total Accepted:    745K
# Total Submissions: 905K
# Testcase Example:  "[1,0,1]"
#
# Given head which is a reference node to a singly-linked list. The value of
# each node in the linked list is either 0 or 1. The linked list holds the
# binary representation of a number.
#
# Return the decimal value of the number in the linked list.
#
# The most significant bit is at the head of the linked list.
#
# Example 1:
#
# Input: head = [1,0,1]
# Output: 5
# Explanation: (101) in base 2 = (5) in base 10
#
# Example 2:
#
# Input: head = [0]
# Output: 0
#
# Constraints:
#
# The Linked List is not empty.
#
# Number of nodes will not exceed 30.
#
# Each node's value is either 0 or 1.
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
    def getDecimalValue(self, head: Optional[ListNode]) -> int:
        """
        Interview explanation:
        Binary linked list MSB first: accumulate ans = ans*2 + val while walking.

        Algorithm:
        - ans=0; while head: ans=(ans<<1)|head.val; head=head.next; return ans.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        while head:
            ans = (ans << 1) | head.val
            head = head.next
        return ans

    def getDecimalValue_str(self, head: Optional[ListNode]) -> int:
        """
        Interview explanation:
        Alternate: build bit string then int(s,2).

        Algorithm:
        - Collect bits; int(''.join, 2).

        Complexity: O(n) time/space.
        """
        bits = []
        while head:
            bits.append(str(head.val))
            head = head.next
        return int("".join(bits), 2) if bits else 0
# @lc code=end
