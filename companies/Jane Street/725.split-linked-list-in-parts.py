#
# @lc app=leetcode id=725 lang=python3
#
# [725] Split Linked List in Parts
#
# https://leetcode.com/problems/split-linked-list-in-parts/description/
#
# algorithms
# Medium (70.67%)
# Likes:    4769
# Dislikes: 376
# Total Accepted:    364K
# Total Submissions: 514K
# Testcase Example:  "[1,2,3]"
#
# Given the head of a singly linked list and an integer k, split the linked
# list into k consecutive linked list parts.
#
# The length of each part should be as equal as possible: no two parts should
# have a size differing by more than one. This may lead to some parts being
# null.
#
# The parts should be in the order of occurrence in the input list, and parts
# occurring earlier should always have a size greater than or equal to parts
# occurring later.
#
# Return an array of the k parts.
#
# Example 1:
#
# Input: head = [1,2,3], k = 5
# Output: [[1],[2],[3],[],[]]
# Explanation:
# The first element output[0] has output[0].val = 1, output[0].next = null.
# The last element output[4] is null, but its string representation as a
# ListNode is [].
#
# Example 2:
#
# Input: head = [1,2,3,4,5,6,7,8,9,10], k = 3
# Output: [[1,2,3,4],[5,6,7],[8,9,10]]
# Explanation:
# The input has been split into consecutive parts with size difference at most
# 1, and earlier parts are a larger size than the later parts.
#
# Constraints:
#
# The number of nodes in the list is in the range [0, 1000].
#
# 0 <= Node.val <= 1000
#
# 1 <= k <= 50
#


# @lc code=start
from typing import List, Optional
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def splitListToParts(
        self, head: Optional[ListNode], k: int
    ) -> List[Optional[ListNode]]:
        """
        Interview explanation:
        Split into k parts as evenly as possible: first (n % k) parts get size
        n//k + 1, the rest get n//k. Walk the list cutting after each part size.

        Algorithm:
        - Count length n; width, rem = divmod(n, k)
        - For each of k parts: take width + (1 if rem else 0) nodes, detach, rem--

        Complexity: O(n + k) time, O(1) extra space besides the answer array.
        """
        n, cur = 0, head
        while cur:
            n += 1
            cur = cur.next
        width, rem = divmod(n, k)
        ans: List[Optional[ListNode]] = []
        cur = head
        for i in range(k):
            part_head = cur
            size = width + (1 if i < rem else 0)
            for _ in range(size - 1):
                if cur:
                    cur = cur.next
            if cur:
                nxt = cur.next
                cur.next = None
                cur = nxt
            ans.append(part_head)
        return ans
# @lc code=end

