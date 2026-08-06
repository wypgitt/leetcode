#
# @lc app=leetcode id=3294 lang=python3
#
# [3294] Convert Doubly Linked List to Array II
#
# https://leetcode.com/problems/convert-doubly-linked-list-to-array-ii/description/
#
# algorithms
# Medium (83.11%)
# Likes:    10
# Dislikes: 5
# Total Accepted:    3.8K
# Total Submissions: 4.6K
# Testcase Example:  "[1,2,3,4,5]\n5"
#
#
# You are given an arbitrary node from a doubly linked list, which
# contains nodes that have a next pointer and a previous pointer.
#
# Return an integer array which contains the elements of the linked list
# in order.
#
# Example 1:
#
# Input: head = [1,2,3,4,5], node = 5
#
# Output: [1,2,3,4,5]
#
# Example 2:
#
# Input: head = [4,5,6,7,8], node = 8
#
# Output: [4,5,6,7,8]
#
# Constraints:
#
# The number of nodes in the given list is in the range [1, 500].
#
# 1 <= Node.val <= 1000
#
# All nodes have unique Node.val.
#

# @lc code=start
from typing import List, Optional

"""
# Definition for a Node.
class Node:
    def __init__(self, val, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next
"""


class Solution:
    def __init__(self):
        """No state; kept for API parity with the Node/list helpers."""

    def toArray(self, node: "Optional[Node]") -> List[int]:
        """
        Interview explanation:
        Given any node of a doubly linked list, return values from head to tail.

        Algorithm:
        - Walk prev until the head.
        - Walk next collecting vals into a list.
        - Alternate: collect forward and backward then reverse the prefix.

        Complexity: O(n) time, O(n) space.
        """
        while node.prev:
            node = node.prev
        ans = []
        while node:
            ans.append(node.val)
            node = node.next
        return ans
# @lc code=end
