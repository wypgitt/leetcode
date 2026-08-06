#
# @lc app=leetcode id=24 lang=python3
#
# [24] Swap Nodes in Pairs
#
# https://leetcode.com/problems/swap-nodes-in-pairs/description/
#
# algorithms
# Medium (69.44%)
# Likes:    13186
# Dislikes: 517
# Total Accepted:    1.9M
# Total Submissions: 2.8M
# Testcase Example:  '[1,2,3,4]'
#
# Given a linked list, swap every two adjacent nodes and return its head. You
# must solve the problem without modifying the values in the list's nodes
# (i.e., only nodes themselves may be changed.)
# 
# 
# Example 1:
# 
# 
# Input: head = [1,2,3,4]
# 
# Output: [2,1,4,3]
# 
# Explanation:
# 
# 
# 
# 
# Example 2:
# 
# 
# Input: head = []
# 
# Output: []
# 
# 
# Example 3:
# 
# 
# Input: head = [1]
# 
# Output: [1]
# 
# 
# Example 4:
# 
# 
# Input: head = [1,2,3]
# 
# Output: [2,1,3]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the list is in the range [0, 100].
# 0 <= Node.val <= 100
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
    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        This is pointer rewiring, not value swapping. A dummy node simplifies the
        first pair because every pair has a predecessor named prev. For each
        pair a -> b, reconnect prev -> b -> a -> next_pair.

        Edge cases and tests:
        - Empty list and one-node list are unchanged.
        - Odd-length list leaves the last node unchanged.
        - Two-node list validates the basic rewiring.

        Complexity: O(n) time, O(1) space.
        """
        dummy = ListNode(0, head)
        prev = dummy

        while prev.next and prev.next.next:
            first = prev.next
            second = first.next

            first.next = second.next
            second.next = first
            prev.next = second

            prev = first

        return dummy.next
# @lc code=end


