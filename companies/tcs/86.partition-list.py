#
# @lc app=leetcode id=86 lang=python3
#
# [86] Partition List
#
# https://leetcode.com/problems/partition-list/description/
#
# algorithms
# Medium (61.11%)
# Likes:    8071
# Dislikes: 984
# Total Accepted:    911.1K
# Total Submissions: 1.5M
# Testcase Example:  '[1,4,3,2,5,2]\n3'
#
# Given the head of a linked list and a value x, partition it such that all
# nodes less than x come before nodes greater than or equal to x.
# 
# You should preserve the original relative order of the nodes in each of the
# two partitions.
# 
# 
# Example 1:
# 
# 
# Input: head = [1,4,3,2,5,2], x = 3
# Output: [1,2,2,4,3,5]
# 
# 
# Example 2:
# 
# 
# Input: head = [2,1], x = 2
# Output: [1,2]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the list is in the range [0, 200].
# -100 <= Node.val <= 100
# -200 <= x <= 200
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
    def partition(self, head: Optional[ListNode], x: int) -> Optional[ListNode]:
        """
        Interview explanation:
        Stable partitioning is easiest with two linked-list builders: one for
        nodes with val < x and one for nodes with val >= x. Appending existing
        nodes preserves relative order inside each partition. Finally connect
        the small list to the large list.

        Edge cases and tests:
        - All nodes less than x or all nodes greater/equal x.
        - Empty list returns None.
        - Mixed values preserve original relative order in each side.

        Complexity: O(n) time, O(1) extra space.
        """
        before_dummy = ListNode(0)
        after_dummy = ListNode(0)
        before = before_dummy
        after = after_dummy

        while head:
            nxt = head.next
            head.next = None
            if head.val < x:
                before.next = head
                before = before.next
            else:
                after.next = head
                after = after.next
            head = nxt

        before.next = after_dummy.next
        return before_dummy.next
# @lc code=end


