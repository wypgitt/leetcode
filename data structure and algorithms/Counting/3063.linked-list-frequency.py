#
# @lc app=leetcode id=3063 lang=python3
#
# [3063] Linked List Frequency
#
# https://leetcode.com/problems/linked-list-frequency/description/
#
# algorithms
# Easy (85.52%)
# Likes:    49
# Dislikes: 21
# Total Accepted:    15.5K
# Total Submissions: 18.1K
# Testcase Example:  "[1,1,2,1,2,3]"
#
#
# Given the head of a linked list containing k distinct elements, return
# the head to a linked list of length k containing the frequency of each
# distinct element in the given linked list in any order.
#
# Example 1:
#
# Input:   head = [1,1,2,1,2,3]
#
# Output:   [3,2,1]
#
# Explanation:  There are 3 distinct elements in the list. The frequency
# of 1 is 3, the frequency of 2 is 2 and the frequency of 3 is 1. Hence,
# we return 3 -> 2 -> 1.
#
# Note that 1 -> 2 -> 3, 1 -> 3 -> 2, 2 -> 1 -> 3, 2 -> 3 -> 1, and 3 -> 1
# -> 2 are also valid answers.
#
# Example 2:
#
# Input:   head = [1,1,2,2,2]
#
# Output:   [2,3]
#
# Explanation:  There are 2 distinct elements in the list. The frequency
# of 1 is 2 and the frequency of 2 is 3. Hence, we return 2 -> 3.
#
# Example 3:
#
# Input:   head = [6,5,4,3,2,1]
#
# Output:   [1,1,1,1,1,1]
#
# Explanation:  There are 6 distinct elements in the list. The frequency
# of each of them is 1. Hence, we return 1 -> 1 -> 1 -> 1 -> 1 -> 1.
#
# Constraints:
#
# The number of nodes in the list is in the range [1, 10^5].
#
# 1 <= Node.val <= 10^5
#

# @lc code=start
from typing import Optional
from collections import Counter

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
    def frequenciesOfElements(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Build a new list whose values are the frequencies of each distinct
        element in the input list (any order is acceptable).

        Algorithm:
        - One pass Counter over node values; emit a linked list of counts.

        Complexity: O(n) time, O(k) space for k distinct values.
        """
        cnt = Counter()
        cur = head
        while cur:
            cnt[cur.val] += 1
            cur = cur.next
        dummy = ListNode(0)
        tail = dummy
        for f in cnt.values():
            tail.next = ListNode(f)
            tail = tail.next
        return dummy.next

    def frequenciesOfElements_dict(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Alternate without Counter: plain dict frequency map, same construction.

        Algorithm:
        - Traverse and tally; build frequency nodes.

        Complexity: O(n) time, O(k) space.
        """
        freq = {}
        cur = head
        while cur:
            freq[cur.val] = freq.get(cur.val, 0) + 1
            cur = cur.next
        dummy = ListNode(0)
        tail = dummy
        for f in freq.values():
            tail.next = ListNode(f)
            tail = tail.next
        return dummy.next
# @lc code=end
