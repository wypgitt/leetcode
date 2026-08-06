#
# @lc app=leetcode id=2130 lang=python3
#
# [2130] Maximum Twin Sum of a Linked List
#
# https://leetcode.com/problems/maximum-twin-sum-of-a-linked-list/description/
#
# algorithms
# Medium (83.26%)
# Likes:    4163
# Dislikes: 130
# Total Accepted:    636K
# Total Submissions: 763.9K
# Testcase Example:  "[5,4,2,1]"
#
# In a linked list of size n, where n is even, the i^th node (0-indexed) of the
# linked list is known as the twin of the (n-1-i)^th node, if 0 <= i <= (n / 2)
# - 1.
#
#
# For example, if n = 4, then node 0 is the twin of node 3, and node 1 is the
# twin of node 2. These are the only nodes with twins for n = 4.
#
# The twin sum is defined as the sum of a node and its twin.
#
# Given the head of a linked list with even length, return the maximum twin sum
# of the linked list.
#
#
#
# Example 1:
#
# Input: head = [5,4,2,1]
# Output: 6
# Explanation:
# Nodes 0 and 1 are the twins of nodes 3 and 2, respectively. All have twin sum
# = 6.
# There are no other nodes with twins in the linked list.
# Thus, the maximum twin sum of the linked list is 6.
#
# Example 2:
#
# Input: head = [4,2,2,3]
# Output: 7
# Explanation:
# The nodes with twins present in this linked list are:
# - Node 0 is the twin of node 3 having a twin sum of 4 + 3 = 7.
# - Node 1 is the twin of node 2 having a twin sum of 2 + 2 = 4.
# Thus, the maximum twin sum of the linked list is max(7, 4) = 7.
#
# Example 3:
#
# Input: head = [1,100000]
# Output: 100001
# Explanation:
# There is only one node with a twin in the linked list having twin sum of 1 +
# 100000 = 100001.
#
#
#
# Constraints:
#
#
# The number of nodes in the list is an even integer in the range [2, 10^5].
#
#
# 1 <= Node.val <= 10^5
#


# @lc code=start
from typing import Optional

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution:
    def pairSum(self, head: Optional['ListNode']) -> int:
        """
        Interview explanation:
        Twin of i is n-1-i in an even-length list. Max twin sum.

        Algorithm:
        - Slow/fast to mid; reverse second half; walk pairing sums.

        Complexity: O(n) time, O(1) space.
        """
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        prev = None
        while slow:
            nxt = slow.next
            slow.next = prev
            prev = slow
            slow = nxt
        ans = 0
        a, b = head, prev
        while b:
            ans = max(ans, a.val + b.val)
            a = a.next
            b = b.next
        return ans

    def pairSum_array(self, head: Optional['ListNode']) -> int:
        """
        Interview explanation:
        Alternate: copy values to array; two pointers.

        Algorithm:
        - List values; max vals[i]+vals[n-1-i].

        Complexity: O(n) time, O(n) space.
        """
        vals = []
        while head:
            vals.append(head.val)
            head = head.next
        n = len(vals)
        return max(vals[i] + vals[n - 1 - i] for i in range(n // 2))
# @lc code=end

