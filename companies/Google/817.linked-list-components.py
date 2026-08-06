#
# @lc app=leetcode id=817 lang=python3
#
# [817] Linked List Components
#
# https://leetcode.com/problems/linked-list-components/description/
#
# algorithms
# Medium (58.12%)
# Likes:    1211
# Dislikes: 2298
# Total Accepted:    130K
# Total Submissions: 224K
# Testcase Example:  "[0,1,2,3]"
#
# You are given the head of a linked list containing unique integer values and
# an integer array nums that is a subset of the linked list values.
#
# Return the number of connected components in nums. A connected component is a
# non-empty, maximal sequence of consecutive nodes in the linked list such that
# every node's value belongs to nums.
#
# Example 1:
#
# Input: head = [0,1,2,3], nums = [0,1,3]
# Output: 2
# Explanation: 0 and 1 are connected, so [0, 1] and [3] are the two connected
# components.
#
# Example 2:
#
# Input: head = [0,1,2,3,4], nums = [0,3,1,4]
# Output: 2
# Explanation: 0 and 1 are connected, 3 and 4 are connected, so [0, 1] and [3,
# 4] are the two connected components.
#
# Constraints:
#
# The number of nodes in the linked list is n.
#
# 1 <= n <= 10^4
#
# 0 <= Node.val < n
#
# All the values Node.val are unique.
#
# 1 <= nums.length <= n
#
# 0 <= nums[i] < n
#
# All the values of nums are unique.
#

# @lc code=start

from typing import List, Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

try:
    ListNode  # type: ignore[name-defined]
except NameError:
    class ListNode:
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next


class Solution:
    def numComponents(self, head: Optional[ListNode], nums: List[int]) -> int:
        """
        Interview explanation:
        Components are maximal consecutive runs of nodes whose values are in
        nums. Walk the list; count a component when we see a nums-node whose
        next is not in nums (or None).

        Algorithm:
        - put nums in a set; traverse; if cur in set and (next None or not in set): count++.

        Complexity: O(n) time, O(|nums|) space.
        """
        s = set(nums)
        ans = 0
        cur = head
        while cur:
            if cur.val in s and (cur.next is None or cur.next.val not in s):
                ans += 1
            cur = cur.next
        return ans
# @lc code=end
