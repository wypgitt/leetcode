#
# @lc app=leetcode id=1721 lang=python3
#
# [1721] Swapping Nodes in a Linked List
#
# https://leetcode.com/problems/swapping-nodes-in-a-linked-list/description/
#
# algorithms
# Medium (69.65%)
# Likes:    5764
# Dislikes: 213
# Total Accepted:    481K
# Total Submissions: 691K
# Testcase Example:  "[1,2,3,4,5]"
#
# You are given the head of a linked list, and an integer k.
#
# Return the head of the linked list after swapping the values of the k^th node
# from the beginning and the k^th node from the end (the list is 1-indexed).
#
# Example 1:
#
# Input: head = [1,2,3,4,5], k = 2
# Output: [1,4,3,2,5]
#
# Example 2:
#
# Input: head = [7,9,6,6,7,8,3,0,9,5], k = 5
# Output: [7,9,6,6,8,7,3,0,9,5]
#
# Constraints:
#
# The number of nodes in the list is n.
#
# 1 <= k <= n <= 10^5
#
# 0 <= Node.val <= 100
#

# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def swapNodes(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        """
        Interview explanation:
        Swap values of k-th from start and k-th from end. One pass: advance first
        to k-th; then advance first and second together from head so when first
        hits end, second is k-th from end.

        Algorithm:
        - first = head; walk k-1 steps → nodeA
        - second = head; while first.next: first, second = first.next, second.next
        - Swap nodeA.val and second.val

        Complexity: O(n) time, O(1) space.
        """
        first = head
        for _ in range(k - 1):
            first = first.next
        node_a = first
        second = head
        while first.next:
            first = first.next
            second = second.next
        node_a.val, second.val = second.val, node_a.val
        return head

    def swapNodes_twopass(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        """
        Interview explanation:
        Alternate: count length n; swap k-th and (n-k+1)-th by index walk.

        Algorithm:
        - Count n; find both nodes; swap values.

        Complexity: O(n) time, O(1) space.
        """
        n = 0
        cur = head
        while cur:
            n += 1
            cur = cur.next
        a = b = head
        for _ in range(k - 1):
            a = a.next
        for _ in range(n - k):
            b = b.next
        a.val, b.val = b.val, a.val
        return head
# @lc code=end
