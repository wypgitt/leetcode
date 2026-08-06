#
# @lc app=leetcode id=3263 lang=python3
#
# [3263] Convert Doubly Linked List to Array I
#
# https://leetcode.com/problems/convert-doubly-linked-list-to-array-i/description/
#
# algorithms
# Easy (94.97%)
# Likes:    21
# Dislikes: 6
# Total Accepted:    9.8K
# Total Submissions: 10.4K
# Testcase Example:  "[1,2,3,4,3,2,1]"
#
#
# You are given the head of a doubly linked list, which contains nodes
# that have a next pointer and a previous pointer.
#
# Return an integer array which contains the elements of the linked list
# in order.
#
# Example 1:
#
# Input: head = [1,2,3,4,3,2,1]
#
# Output: [1,2,3,4,3,2,1]
#
# Example 2:
#
# Input: head = [2,2,2,2,2]
#
# Output: [2,2,2,2,2]
#
# Example 3:
#
# Input: head = [3,2,3,2,3,2]
#
# Output: [3,2,3,2,3,2]
#
# Constraints:
#
# The number of nodes in the given list is in the range [1, 50].
#
# 1 <= Node.val <= 50
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
    def toArray(self, root: 'Optional[Node]') -> List[int]:
        """
        Interview explanation:
        Walk the doubly linked list from the given head via next pointers and
        collect values in order.

        Algorithm:
        - Iterate cur = root; append cur.val; advance cur = cur.next.

        Complexity: O(n) time, O(n) space for the answer.
        """
        ans: List[int] = []
        cur = root
        while cur:
            ans.append(cur.val)
            cur = cur.next
        return ans

    def toArray_recursive(self, root: 'Optional[Node]') -> List[int]:
        """
        Interview explanation:
        Alternate: recurse on next and build the list on the way down/up.

        Algorithm:
        - Base None → []; else [root.val] + toArray(root.next).

        Complexity: O(n) time, O(n) recursion space.
        """
        if root is None:
            return []
        return [root.val] + self.toArray_recursive(root.next)
# @lc code=end
