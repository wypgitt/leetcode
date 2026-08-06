#
# @lc app=leetcode id=141 lang=python3
#
# [141] Linked List Cycle
#
# https://leetcode.com/problems/linked-list-cycle/description/
#
# algorithms
# Easy (54.84%)
# Likes:    17753
# Dislikes: 1600
# Total Accepted:    5.2M
# Total Submissions: 9.4M
# Testcase Example:  "[3,2,0,-4]"
#
# Given head, the head of a linked list, determine if the linked list has a
# cycle in it.
#
# There is a cycle in a linked list if there is some node in the list that can
# be reached again by continuously following the next pointer. Internally, pos
# is used to denote the index of the node that tail's next pointer is connected
# to. Note that pos is not passed as a parameter.
#
# Return true if there is a cycle in the linked list. Otherwise, return false.
#
# Example 1:
#
# Input: head = [3,2,0,-4], pos = 1
# Output: true
# Explanation: There is a cycle in the linked list, where the tail connects to
# the 1st node (0-indexed).
#
# Example 2:
#
# Input: head = [1,2], pos = 0
# Output: true
# Explanation: There is a cycle in the linked list, where the tail connects to
# the 0th node.
#
# Example 3:
#
# Input: head = [1], pos = -1
# Output: false
# Explanation: There is no cycle in the linked list.
#
# Constraints:
#
# The number of the nodes in the list is in the range [0, 10^4].
#
# -10^5 <= Node.val <= 10^5
#
# pos is -1 or a valid index in the linked-list.
#
# Follow up: Can you solve it using O(1) (i.e. constant) memory?
#

# @lc code=start
from typing import Optional, Set
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        """
        Interview explanation:
        Floyd's tortoise and hare: slow moves one step, fast two. If there is a
        cycle they must meet; if not, fast hits None. Best O(1) memory solution.

        Algorithm:
        - Initialize slow = fast = head.
        - While fast and fast.next exist, advance slow by 1 and fast by 2.
        - If they meet, a cycle exists.

        Complexity: O(n) time, O(1) space.
        """
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False

    def hasCycleHashSet(self, head: Optional[ListNode]) -> bool:
        """
        Interview explanation:
        Track visited nodes in a set. Seeing a node again proves a cycle.
        Simpler but uses extra memory.

        Algorithm:
        - Walk the list; if current is in the set, return True; else add it.

        Complexity: O(n) time, O(n) space.
        """
        seen: Set[ListNode] = set()
        cur = head
        while cur:
            if cur in seen:
                return True
            seen.add(cur)
            cur = cur.next
        return False
# @lc code=end
