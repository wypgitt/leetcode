#
# @lc app=leetcode id=234 lang=python3
#
# [234] Palindrome Linked List
#
# https://leetcode.com/problems/palindrome-linked-list/description/
#
# algorithms
# Easy (58.53%)
# Likes:    18527
# Dislikes: 988
# Total Accepted:    3.1M
# Total Submissions: 5.2M
# Testcase Example:  "[1,2,2,1]"
#
# Given the head of a singly linked list, return true if it is a palindrome or
# false otherwise.
#
# Example 1:
#
# Input: head = [1,2,2,1]
# Output: true
#
# Example 2:
#
# Input: head = [1,2]
# Output: false
#
# Constraints:
#
# The number of nodes in the list is in the range [1, 10^5].
#
# 0 <= Node.val <= 9
#
# Follow up: Could you do it in O(n) time and O(1) space?
#

# @lc code=start
from typing import List, Optional
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        """
        Interview explanation:
        Find the middle, reverse the second half, compare halves, then optionally
        restore. Achieves O(1) extra space.

        Algorithm:
        - Slow/fast to middle; reverse from slow (second half).
        - Compare first half with reversed second half values.
        - Return whether all pairs match.

        Complexity: O(n) time, O(1) space.
        """
        if not head or not head.next:
            return True

        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        prev = None
        cur = slow
        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt

        left, right = head, prev
        while right:
            if left.val != right.val:
                return False
            left = left.next
            right = right.next
        return True

    def isPalindromeArray(self, head: Optional[ListNode]) -> bool:
        """
        Interview explanation:
        Copy values to an array and check palindrome with two pointers.
        Simpler O(n) space alternate.

        Algorithm:
        - Walk list into a list of values; compare with its reverse.

        Complexity: O(n) time, O(n) space.
        """
        vals: List[int] = []
        cur = head
        while cur:
            vals.append(cur.val)
            cur = cur.next
        return vals == vals[::-1]
# @lc code=end
