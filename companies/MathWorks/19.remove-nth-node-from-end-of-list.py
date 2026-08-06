#
# @lc app=leetcode id=19 lang=python3
#
# [19] Remove Nth Node From End of List
#
# https://leetcode.com/problems/remove-nth-node-from-end-of-list/description/
#
# algorithms
# Medium (51.50%)
# Likes:    21287
# Dislikes: 910
# Total Accepted:    4.2M
# Total Submissions: 8.2M
# Testcase Example:  '[1,2,3,4,5]\n2'
#
# Given the head of a linked list, remove the n^th node from the end of the
# list and return its head.
# 
# 
# Example 1:
# 
# 
# Input: head = [1,2,3,4,5], n = 2
# Output: [1,2,3,5]
# 
# 
# Example 2:
# 
# 
# Input: head = [1], n = 1
# Output: []
# 
# 
# Example 3:
# 
# 
# Input: head = [1,2], n = 1
# Output: [1]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the list is sz.
# 1 <= sz <= 30
# 0 <= Node.val <= 100
# 1 <= n <= sz
# 
# 
# 
# Follow up: Could you do this in one pass?
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
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        """
        Interview explanation:
        A two-pointer gap of n nodes finds the predecessor of the node to delete
        in one pass. A dummy node is the right helper structure because deleting
        the original head then becomes the same pointer operation as deleting
        any other node.

        Algorithm:
        - Move fast n steps ahead from dummy.
        - Move fast and slow together until fast reaches the tail.
        - slow.next is the target; bypass it.

        Edge cases and tests:
        - Removing the head, e.g. [1], n=1, returns None.
        - Removing the last node works because slow stops at its predecessor.
        - n is guaranteed valid by constraints.

        Complexity: O(L) time, O(1) space.
        """
        dummy = ListNode(0, head)
        fast = slow = dummy

        for _ in range(n):
            fast = fast.next

        while fast.next:
            fast = fast.next
            slow = slow.next

        slow.next = slow.next.next
        return dummy.next
# @lc code=end


