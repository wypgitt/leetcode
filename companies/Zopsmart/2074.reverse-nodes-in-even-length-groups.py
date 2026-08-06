#
# @lc app=leetcode id=2074 lang=python3
#
# [2074] Reverse Nodes in Even Length Groups
#
# https://leetcode.com/problems/reverse-nodes-in-even-length-groups/description/
#
# algorithms
# Medium (64.83%)
# Likes:    911
# Dislikes: 376
# Total Accepted:    50K
# Total Submissions: 77.1K
# Testcase Example:  "[5,2,6,3,9,1,7,3,8,4]"
#
# You are given the head of a linked list.
#
# The nodes in the linked list are sequentially assigned to non-empty groups
# whose lengths form the sequence of the natural numbers (1, 2, 3, 4, ...). The
# length of a group is the number of nodes assigned to it. In other words,
#
#
# The 1^st node is assigned to the first group.
#
#
# The 2^nd and the 3^rd nodes are assigned to the second group.
#
#
# The 4^th, 5^th, and 6^th nodes are assigned to the third group, and so on.
#
# Note that the length of the last group may be less than or equal to 1 + the
# length of the second to last group.
#
# Reverse the nodes in each group with an even length, and return the head of
# the modified linked list.
#
#
#
# Example 1:
#
# Input: head = [5,2,6,3,9,1,7,3,8,4]
# Output: [5,6,2,3,9,1,4,8,3,7]
# Explanation:
# - The length of the first group is 1, which is odd, hence no reversal occurs.
# - The length of the second group is 2, which is even, hence the nodes are
# reversed.
# - The length of the third group is 3, which is odd, hence no reversal occurs.
# - The length of the last group is 4, which is even, hence the nodes are
# reversed.
#
# Example 2:
#
# Input: head = [1,1,0,6]
# Output: [1,0,1,6]
# Explanation:
# - The length of the first group is 1. No reversal occurs.
# - The length of the second group is 2. The nodes are reversed.
# - The length of the last group is 1. No reversal occurs.
#
# Example 3:
#
# Input: head = [1,1,0,6,5]
# Output: [1,0,1,5,6]
# Explanation:
# - The length of the first group is 1. No reversal occurs.
# - The length of the second group is 2. The nodes are reversed.
# - The length of the last group is 2. The nodes are reversed.
#
#
#
# Constraints:
#
#
# The number of nodes in the list is in the range [1, 10^5].
#
#
# 0 <= Node.val <= 10^5
#

# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def reverseEvenLengthGroups(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Group nodes with lengths 1,2,3,... (last group may be shorter). Reverse
        nodes in groups whose actual length is even; leave odd groups as-is.

        Algorithm:
        - Traverse with group size g=1,2,...; count actual length; if even,
          reverse that segment in place.

        Complexity: O(n) time, O(1) space.
        """
        def reverse(start: ListNode, end: ListNode):
            # reverse nodes from start through end inclusive; return new head/tail
            prev = end.next
            cur = start
            while prev is not end:
                nxt = cur.next
                cur.next = prev
                prev = cur
                cur = nxt
            return end, start

        dummy = ListNode(0, head)
        prev_tail = dummy
        g = 1
        while prev_tail.next:
            # find group end / count
            cur = prev_tail.next
            cnt = 1
            while cnt < g and cur.next:
                cur = cur.next
                cnt += 1
            next_group = cur.next
            if cnt % 2 == 0:
                start = prev_tail.next
                end = cur
                new_head, new_tail = reverse(start, end)
                prev_tail.next = new_head
                new_tail.next = next_group
                prev_tail = new_tail
            else:
                prev_tail = cur
            g += 1
        return dummy.next
# @lc code=end
