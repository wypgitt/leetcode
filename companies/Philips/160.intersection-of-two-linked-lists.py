#
# @lc app=leetcode id=160 lang=python3
#
# [160] Intersection of Two Linked Lists
#
# https://leetcode.com/problems/intersection-of-two-linked-lists/description/
#
# algorithms
# Easy (64.37%)
# Likes:    16807
# Dislikes: 1504
# Total Accepted:    2.5M
# Total Submissions: 3.9M
# Testcase Example:  "8"
#
# Given the heads of two singly linked-lists headA and headB, return the node
# at which the two lists intersect. If the two linked lists have no
# intersection at all, return null.
#
# For example, the following two linked lists begin to intersect at node c1:
#
# The test cases are generated such that there are no cycles anywhere in the
# entire linked structure.
#
# Note that the linked lists must retain their original structure after the
# function returns.
#
# Custom Judge:
#
# The inputs to the judge are given as follows (your program is not given these
# inputs):
#
# intersectVal - The value of the node where the intersection occurs. This is 0
# if there is no intersected node.
#
# listA - The first linked list.
#
# listB - The second linked list.
#
# skipA - The number of nodes to skip ahead in listA (starting from the head)
# to get to the intersected node.
#
# skipB - The number of nodes to skip ahead in listB (starting from the head)
# to get to the intersected node.
#
# The judge will then create the linked structure based on these inputs and
# pass the two heads, headA and headB to your program. If you correctly return
# the intersected node, then your solution will be accepted.
#
# Example 1:
#
# Input: intersectVal = 8, listA = [4,1,8,4,5], listB = [5,6,1,8,4,5], skipA =
# 2, skipB = 3
# Output: Intersected at '8'
# Explanation: The intersected node's value is 8 (note that this must not be 0
# if the two lists intersect).
# From the head of A, it reads as [4,1,8,4,5]. From the head of B, it reads as
# [5,6,1,8,4,5]. There are 2 nodes before the intersected node in A; There are
# 3 nodes before the intersected node in B.
# - Note that the intersected node's value is not 1 because the nodes with
# value 1 in A and B (2^nd node in A and 3^rd node in B) are different node
# references. In other words, they point to two different locations in memory,
# while the nodes with value 8 in A and B (3^rd node in A and 4^th node in B)
# point to the same location in memory.
#
# Example 2:
#
# Input: intersectVal = 2, listA = [1,9,1,2,4], listB = [3,2,4], skipA = 3,
# skipB = 1
# Output: Intersected at '2'
# Explanation: The intersected node's value is 2 (note that this must not be 0
# if the two lists intersect).
# From the head of A, it reads as [1,9,1,2,4]. From the head of B, it reads as
# [3,2,4]. There are 3 nodes before the intersected node in A; There are 1 node
# before the intersected node in B.
#
# Example 3:
#
# Input: intersectVal = 0, listA = [2,6,4], listB = [1,5], skipA = 3, skipB = 2
# Output: No intersection
# Explanation: From the head of A, it reads as [2,6,4]. From the head of B, it
# reads as [1,5]. Since the two lists do not intersect, intersectVal must be 0,
# while skipA and skipB can be arbitrary values.
# Explanation: The two lists do not intersect, so return null.
#
# Constraints:
#
# The number of nodes of listA is in the m.
#
# The number of nodes of listB is in the n.
#
# 1 <= m, n <= 3 * 10^4
#
# 1 <= Node.val <= 10^5
#
# 0 <= skipA <= m
#
# 0 <= skipB <= n
#
# intersectVal is 0 if listA and listB do not intersect.
#
# intersectVal == listA[skipA] == listB[skipB] if listA and listB intersect.
#
# Follow up: Could you write a solution that runs in O(m + n) time and use only
# O(1) memory?
#

# @lc code=start
from typing import Optional, Set
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> Optional[ListNode]:
        """
        Interview explanation:
        Two-pointer switch: after finishing one list, jump to the other head.
        Both pointers then travel the same remaining distance and meet at the
        intersection (or both become None). Best O(1)-space solution.

        Algorithm:
        - a, b start at headA, headB.
        - Advance each; when one hits None, redirect to the other list's head.
        - They meet at the intersection node or both None.

        Complexity: O(m + n) time, O(1) space.
        """
        a, b = headA, headB
        while a is not b:
            a = a.next if a else headB
            b = b.next if b else headA
        return a

    def getIntersectionNodeHashSet(self, headA: ListNode, headB: ListNode) -> Optional[ListNode]:
        """
        Interview explanation:
        Store all nodes of A in a set, then scan B for the first node already
        seen. Simple but uses extra memory.

        Algorithm:
        - Add every node from list A to a set.
        - Walk B; return the first node present in the set.

        Complexity: O(m + n) time, O(m) space.
        """
        seen: Set[ListNode] = set()
        cur = headA
        while cur:
            seen.add(cur)
            cur = cur.next
        cur = headB
        while cur:
            if cur in seen:
                return cur
            cur = cur.next
        return None
# @lc code=end
