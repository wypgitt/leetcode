#
# @lc app=leetcode id=1265 lang=python3
#
# [1265] Print Immutable Linked List in Reverse
#
# https://leetcode.com/problems/print-immutable-linked-list-in-reverse/description/
#
# algorithms
# Medium (94.06%)
# Likes:    599
# Dislikes: 106
# Total Accepted:    67.4K
# Total Submissions: 71.6K
# Testcase Example:  '[1,2,3,4]'
#
# You are given an immutable linked list, print out all values of each node in
# reverse with the help of the following interface:
# 
# 
# ImmutableListNode: An interface of immutable linked list, you are given the
# head of the list.
# 
# 
# You need to use the following functions to access the linked list (you can't
# access the ImmutableListNode directly):
# 
# 
# ImmutableListNode.printValue(): Print value of the current node.
# ImmutableListNode.getNext(): Return the next node.
# 
# 
# The input is only given to initialize the linked list internally. You must
# solve this problem without modifying the linked list. In other words, you
# must operate the linked list using only the mentioned APIs.
# 
# 
# Example 1:
# 
# 
# Input: head = [1,2,3,4]
# Output: [4,3,2,1]
# 
# 
# Example 2:
# 
# 
# Input: head = [0,-4,-1,3,-5]
# Output: [-5,3,-1,-4,0]
# 
# 
# Example 3:
# 
# 
# Input: head = [-2,0,6,4,4,-6]
# Output: [-6,4,4,6,0,-2]
# 
# 
# 
# 
# 
# 
# Constraints:
# 
# 
# The length of the linked list is between [1, 1000].
# The value of each node in the linked list is between [-1000, 1000].
# 
# 
# 
# 
# Follow up:
# 
# Could you solve this problem in:
# 
# 
# Constant space complexity?
# Linear time complexity and less than linear space complexity?
# 
# 
#

# @lc code=start
# """
# This is the ImmutableListNode's API interface.
# You should not implement it, or speculate about its implementation.
# """
# class ImmutableListNode:
#     def printValue(self) -> None: # print the value of this node.
#     def getNext(self) -> 'ImmutableListNode': # return the next node.

class Solution:
    def printLinkedListInReverse(self, head: 'ImmutableListNode') -> None:
        if not head:
            return
        self.printLinkedListInReverse(head.getNext())
        head.printValue()
# @lc code=end

# Explanation
# -----------
# Because the list is immutable and singly linked, we cannot reverse pointers.
# Recursion first walks to the tail, then prints while the call stack unwinds.
# That naturally gives reverse order.
#
# The call stack is acting as the data structure that stores the path from head
# to tail. This is the simplest interview solution and uses only the API
# methods getNext and printValue.
#
# Edge cases: an empty head returns immediately; a one-node list prints that
# node after the recursive call on None.
#
# Time complexity: O(n), one visit per node.
# Space complexity: O(n) recursion stack. A follow-up with stricter memory
# could use block decomposition, but this direct solution is clear and accepted
# for the standard constraints.
