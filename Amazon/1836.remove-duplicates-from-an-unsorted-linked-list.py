#
# @lc app=leetcode id=1836 lang=python3
#
# [1836] Remove Duplicates From an Unsorted Linked List
#
# https://leetcode.com/problems/remove-duplicates-from-an-unsorted-linked-list/description/
#
# algorithms
# Medium (75.67%)
# Likes:    408
# Dislikes: 12
# Total Accepted:    40.6K
# Total Submissions: 53.6K
# Testcase Example:  "[1,2,3,2]"
#
#
# Given the head of a linked list, find all the values that appear more
# than once in the list and delete the nodes that have any of those
# values.
#
#
#
# Return the linked list after the deletions.
#
#
#
#
#
# Example 1:
#
#
#
#
# Input: head = [1,2,3,2]
# Output: [1,3]
# Explanation: 2 appears twice in the linked list, so all 2's should be
# deleted. After deleting all 2's, we are left with [1,3].
#
#
#
#
# Example 2:
#
#
#
#
# Input: head = [2,1,1,2]
# Output: []
# Explanation: 2 and 1 both appear twice. All the elements should be
# deleted.
#
#
#
#
# Example 3:
#
#
#
#
# Input: head = [3,2,2,1,3,2,4]
# Output: [1,4]
# Explanation: 3 appears twice and 2 appears three times. After deleting
# all 3's and 2's, we are left with [1,4].
#
#
#
#
#
#
# Constraints:
#
#
#
#
#
# The number of nodes in the list is in the range [1, 10^5]
#
#
# 1 <= Node.val <= 10^5
#
# @lc code=start
from typing import Optional
from collections import Counter


# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def deleteDuplicatesUnsorted(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Premium: remove all nodes whose values appear more than once in unsorted list.

        Algorithm (frequency + rebuild):
        - Count frequencies; second pass keep nodes with freq==1 via dummy.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter()
        cur = head
        while cur:
            cnt[cur.val] += 1
            cur = cur.next
        dummy = ListNode(0)
        tail = dummy
        cur = head
        while cur:
            if cnt[cur.val] == 1:
                tail.next = cur
                tail = cur
            cur = cur.next
        tail.next = None
        return dummy.next
# @lc code=end
