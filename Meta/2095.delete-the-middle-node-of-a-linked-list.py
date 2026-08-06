#
# @lc app=leetcode id=2095 lang=python3
#
# [2095] Delete the Middle Node of a Linked List
#
# https://leetcode.com/problems/delete-the-middle-node-of-a-linked-list/description/
#
# algorithms
# Medium (60.92%)
# Likes:    5207
# Dislikes: 111
# Total Accepted:    1.1M
# Total Submissions: 1.9M
# Testcase Example:  "[1,3,4,7,1,2,6]"
#
# You are given the head of a linked list. Delete the middle node, and return
# the head of the modified linked list.
#
# The middle node of a linked list of size n is the ⌊n / 2⌋^th node from the
# start using 0-based indexing, where ⌊x⌋ denotes the largest integer less than
# or equal to x.
#
#
# For n = 1, 2, 3, 4, and 5, the middle nodes are 0, 1, 1, 2, and 2,
# respectively.
#
#
#
# Example 1:
#
# Input: head = [1,3,4,7,1,2,6]
# Output: [1,3,4,1,2,6]
# Explanation:
# The above figure represents the given linked list. The indices of the nodes
# are written below.
# Since n = 7, node 3 with value 7 is the middle node, which is marked in red.
# We return the new list after removing this node.
#
# Example 2:
#
# Input: head = [1,2,3,4]
# Output: [1,2,4]
# Explanation:
# The above figure represents the given linked list.
# For n = 4, node 2 with value 3 is the middle node, which is marked in red.
#
# Example 3:
#
# Input: head = [2,1]
# Output: [2]
# Explanation:
# The above figure represents the given linked list.
# For n = 2, node 1 with value 1 is the middle node, which is marked in red.
# Node 0 with value 2 is the only node remaining after removing node 1.
#
#
#
# Constraints:
#
#
# The number of nodes in the list is in the range [1, 10^5].
#
#
# 1 <= Node.val <= 10^5
#

# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def deleteMiddle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Delete the middle node (0-based index n//2) of a singly linked list.

        Algorithm:
        - Dummy + slow/fast; fast moves 2, slow 1; when fast hits end, slow is
          before middle; unlink slow.next.

        Complexity: O(n) time, O(1) space.
        """
        if not head.next:
            return None
        dummy = ListNode(0, head)
        slow = dummy
        fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        slow.next = slow.next.next
        return dummy.next

    def deleteMiddle_count(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Alternate two-pass: count length, then delete node at n//2.

        Algorithm:
        - Count n; walk to n//2 - 1; unlink next.

        Complexity: O(n) time, O(1) space.
        """
        n = 0
        cur = head
        while cur:
            n += 1
            cur = cur.next
        if n == 1:
            return None
        cur = head
        for _ in range(n // 2 - 1):
            cur = cur.next
        cur.next = cur.next.next
        return head
# @lc code=end
