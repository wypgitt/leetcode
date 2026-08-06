#
# @lc app=leetcode id=3217 lang=python3
#
# [3217] Delete Nodes From Linked List Present in Array
#
# https://leetcode.com/problems/delete-nodes-from-linked-list-present-in-array/description/
#
# algorithms
# Medium (69.27%)
# Likes:    1102
# Dislikes: 50
# Total Accepted:    345.8K
# Total Submissions: 499.2K
# Testcase Example:  "[1,2,3]\n[1,2,3,4,5]"
#
#
# You are given an array of integers nums and the head of a linked list.
# Return the head of the modified linked list after removing all nodes
# from the linked list that have a value that exists in nums.
#
# Example 1:
#
# Input: nums = [1,2,3], head = [1,2,3,4,5]
#
# Output: [4,5]
#
# Explanation:
#
# Remove the nodes with values 1, 2, and 3.
#
# Example 2:
#
# Input: nums = [1], head = [1,2,1,2,1,2]
#
# Output: [2,2,2]
#
# Explanation:
#
# Remove the nodes with value 1.
#
# Example 3:
#
# Input: nums = [5], head = [1,2,3,4]
#
# Output: [1,2,3,4]
#
# Explanation:
#
# No node has value 5.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# All elements in nums are unique.
#
# The number of nodes in the given list is in the range [1, 10^5].
#
# 1 <= Node.val <= 10^5
#
# The input is generated such that there is at least one node in the
# linked list that has a value not present in nums.
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

    class ListNode:  # type: ignore[no-redef]
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next


class Solution:
    def modifiedList(self, nums: List[int], head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Interview explanation:
        Delete every list node whose value appears in nums.

        Algorithm:
        - Put nums in a set for O(1) lookup.
        - Dummy head; walk with prev; skip next when val is in the set.

        Complexity: O(n + m) time, O(n) space (n = |nums|, m = list length).
        """
        remove = set(nums)
        dummy = ListNode(0, head)
        prev = dummy
        while prev.next:
            if prev.next.val in remove:
                prev.next = prev.next.next
            else:
                prev = prev.next
        return dummy.next
# @lc code=end
