#
# @lc app=leetcode id=1474 lang=python3
#
# [1474] Delete N Nodes After M Nodes of a Linked List
#
# https://leetcode.com/problems/delete-n-nodes-after-m-nodes-of-a-linked-list/description/
#
# algorithms
# Easy (74.36%)
# Likes:    434
# Dislikes: 18
# Total Accepted:    42.7K
# Total Submissions: 57.4K
# Testcase Example:  "[1,2,3,4,5,6,7,8,9,10,11,12,13]\n2\n3"
#
#
# You are given the head of a linked list and two integers m and n.
#
# Traverse the linked list and remove some nodes in the following way:
#
# Start with the head as the current node.
#
# Keep the first m nodes starting with the current node.
#
# Remove the next n nodes
#
# Keep repeating steps 2 and 3 until you reach the end of the list.
#
# Return the head of the modified list after removing the mentioned nodes.
#
# Example 1:
#
# Input: head = [1,2,3,4,5,6,7,8,9,10,11,12,13], m = 2, n = 3
# Output: [1,2,6,7,11,12]
# Explanation: Keep the first (m = 2) nodes starting from the head of the
# linked List  (1 ->2) show in black nodes.
# Delete the next (n = 3) nodes (3 -> 4 -> 5) show in read nodes.
# Continue with the same procedure until reaching the tail of the Linked
# List.
# Head of the linked list after removing nodes is returned.
#
# Example 2:
#
# Input: head = [1,2,3,4,5,6,7,8,9,10,11], m = 1, n = 3
# Output: [1,5,9]
# Explanation: Head of linked list after removing nodes is returned.
#
# Constraints:
#
# The number of nodes in the list is in the range [1, 10^4].
#
# 1 <= Node.val <= 10^6
#
# 1 <= m, n <= 1000
#
# Follow up: Could you solve this problem by modifying the list in-place?
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
    def deleteNodes(self, head: Optional[ListNode], m: int, n: int) -> Optional[ListNode]:
        """
        Interview explanation:
        Premium. Keep m nodes, delete next n nodes, repeat until end.

        Algorithm:
        - Walk: advance m-1 kept nodes; from there skip n nodes by relinking.

        Complexity: O(L) time, O(1) space.
        """
        cur = head
        while cur:
            for _ in range(1, m):
                if not cur:
                    return head
                cur = cur.next
            if not cur:
                break
            # delete n nodes after cur
            tail = cur.next
            for _ in range(n):
                if not tail:
                    break
                tail = tail.next
            cur.next = tail
            cur = cur.next
        return head
# @lc code=end
