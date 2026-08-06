#
# @lc app=leetcode id=82 lang=python3
#
# [82] Remove Duplicates from Sorted List II
#
# https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/description/
#
# algorithms
# Medium (51.73%)
# Likes:    9706
# Dislikes: 283
# Total Accepted:    1.1M
# Total Submissions: 2.1M
# Testcase Example:  '[1,2,3,3,4,4,5]'
#
# Given the head of a sorted linked list, delete all nodes that have duplicate
# numbers, leaving only distinct numbers from the original list. Return the
# linked list sorted as well.
# 
# 
# Example 1:
# 
# 
# Input: head = [1,2,3,3,4,4,5]
# Output: [1,2,5]
# 
# 
# Example 2:
# 
# 
# Input: head = [1,1,1,2,3]
# Output: [2,3]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the list is in the range [0, 300].
# -100 <= Node.val <= 100
# The list is guaranteed to be sorted in ascending order.
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
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        The list is sorted, so duplicates appear in consecutive runs. A dummy
        node handles deleting a duplicated run at the head. prev always points to
        the last node known to be unique in the output; cur scans each run.

        Edge cases and tests:
        - Duplicates at the head are removed.
        - Duplicates at the tail are removed.
        - A list with no duplicates is unchanged.
        - A list where every value duplicates returns None.

        Complexity: O(n) time, O(1) space.
        """
        dummy = ListNode(0, head)
        prev = dummy
        cur = head

        while cur:
            duplicate = False
            while cur.next and cur.val == cur.next.val:
                duplicate = True
                cur = cur.next
            if duplicate:
                prev.next = cur.next
            else:
                prev = prev.next
            cur = cur.next

        return dummy.next
# @lc code=end


