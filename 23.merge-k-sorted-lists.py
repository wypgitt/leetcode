#
# @lc app=leetcode id=23 lang=python3
#
# [23] Merge k Sorted Lists
#
# https://leetcode.com/problems/merge-k-sorted-lists/description/
#
# algorithms
# Hard (59.47%)
# Likes:    21339
# Dislikes: 794
# Total Accepted:    3M
# Total Submissions: 5M
# Testcase Example:  '[[1,4,5],[1,3,4],[2,6]]'
#
# You are given an array of k linked-lists lists, each linked-list is sorted in
# ascending order.
# 
# Merge all the linked-lists into one sorted linked-list and return it.
# 
# 
# Example 1:
# 
# 
# Input: lists = [[1,4,5],[1,3,4],[2,6]]
# Output: [1,1,2,3,4,4,5,6]
# Explanation: The linked-lists are:
# [
# ⁠ 1->4->5,
# ⁠ 1->3->4,
# ⁠ 2->6
# ]
# merging them into one sorted linked list:
# 1->1->2->3->4->4->5->6
# 
# 
# Example 2:
# 
# 
# Input: lists = []
# Output: []
# 
# 
# Example 3:
# 
# 
# Input: lists = [[]]
# Output: []
# 
# 
# 
# Constraints:
# 
# 
# k == lists.length
# 0 <= k <= 10^4
# 0 <= lists[i].length <= 500
# -10^4 <= lists[i][j] <= 10^4
# lists[i] is sorted in ascending order.
# The sum of lists[i].length will not exceed 10^4.
# 
# 
#

"""
Optimal approach: min-heap / priority queue.

We have k already-sorted linked lists. At any moment, the smallest node among
all unmerged nodes must be one of the current heads of those lists. That is the
key observation: we do not need to scan every remaining node. We only need to
efficiently know the smallest current head.

Data structure:
    A min-heap stores one candidate node per non-empty list:
        (node value, unique tie-breaker, node)

    Python's heap compares tuple elements from left to right. The tie-breaker is
    needed because two nodes can have the same value, and ListNode objects are
    not orderable.

Algorithm:
    1. Push the head of every non-empty list into the heap.
    2. Create a dummy node and a tail pointer for the merged result.
    3. Repeatedly pop the smallest node from the heap.
    4. Append that node to the result.
    5. If the popped node has a next node, push that next node into the heap.
    6. Return dummy.next.

Why this works:
    Each input list is sorted, so after taking a node from one list, the only
    new candidate from that list is its next node. The heap always contains the
    smallest not-yet-used node from each active list, so popping from the heap
    always gives the globally smallest remaining node.

Complexity:
    Let k be the number of lists and N be the total number of nodes.

    Time:  O(N log k)
        Every node is pushed into and popped from the heap once. The heap holds
        at most k nodes, so each heap operation costs O(log k).

    Space: O(k)
        The heap stores at most one node per list. The output list reuses the
        original nodes, so it does not count as extra auxiliary space.
"""

# @lc code=start
import heapq
from typing import List, Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        heap = []
        tie_breaker = 0

        for node in lists:
            if node:
                heapq.heappush(heap, (node.val, tie_breaker, node))
                tie_breaker += 1

        dummy = ListNode()
        tail = dummy

        while heap:
            _, _, node = heapq.heappop(heap)
            tail.next = node
            tail = tail.next

            if node.next:
                heapq.heappush(heap, (node.next.val, tie_breaker, node.next))
                tie_breaker += 1

        return dummy.next
# @lc code=end
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def mergeKLists(self, lists: Listp[Optional[ListNode]]) -> Optional[ListNode]:
        heap = []
        tie_breaker = 0

        for node in lists:
            if node:
                heapq.heappush(heap, (node.val, tie_breaker, node))
                tie_breaker += 1
        
        dummy = ListNode()
        head = dummy
        while heap:
            _, _, node = heapq.heappop(heap)
            head.next = node
            head = head.next

            if node.next:
                heapq.heappush(heap, (node.next.val, tie_breaker, node.next))
                tie_breaker += 1

        return dummy.next