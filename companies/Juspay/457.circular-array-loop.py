#
# @lc app=leetcode id=457 lang=python3
#
# [457] Circular Array Loop
#
# https://leetcode.com/problems/circular-array-loop/description/
#
# algorithms
# Medium (37.31%)
# Likes:    832
# Dislikes: 906
# Total Accepted:    109.3K
# Total Submissions: 292.9K
# Testcase Example:  '[2,-1,1,2,2]'
#
# You are playing a game involving a circular array of non-zero integers nums.
# Each nums[i] denotes the number of indices forward/backward you must move if
# you are located at index i:
# 
# 
# If nums[i] is positive, move nums[i] steps forward, and
# If nums[i] is negative, move abs(nums[i]) steps backward.
# 
# 
# Since the array is circular, you may assume that moving forward from the last
# element puts you on the first element, and moving backwards from the first
# element puts you on the last element.
# 
# A cycle in the array consists of a sequence of indices seq of length k
# where:
# 
# 
# Following the movement rules above results in the repeating index sequence
# seq[0] -> seq[1] -> ... -> seq[k - 1] -> seq[0] -> ...
# Every nums[seq[j]] is either all positive or all negative.
# k > 1
# 
# 
# Return true if there is a cycle in nums, or false otherwise.
# 
# 
# Example 1:
# 
# 
# Input: nums = [2,-1,1,2,2]
# Output: true
# Explanation: The graph shows how the indices are connected. White nodes are
# jumping forward, while red is jumping backward.
# We can see the cycle 0 --> 2 --> 3 --> 0 --> ..., and all of its nodes are
# white (jumping in the same direction).
# 
# 
# Example 2:
# 
# 
# Input: nums = [-1,-2,-3,-4,-5,6]
# Output: false
# Explanation: The graph shows how the indices are connected. White nodes are
# jumping forward, while red is jumping backward.
# The only cycle is of size 1, so we return false.
# 
# 
# Example 3:
# 
# 
# Input: nums = [1,-1,5,1,4]
# Output: true
# Explanation: The graph shows how the indices are connected. White nodes are
# jumping forward, while red is jumping backward.
# We can see the cycle 0 --> 1 --> 0 --> ..., and while it is of size > 1, it
# has a node jumping forward and a node jumping backward, so it is not a cycle.
# We can see the cycle 3 --> 4 --> 3 --> ..., and all of its nodes are white
# (jumping in the same direction).
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 5000
# -1000 <= nums[i] <= 1000
# nums[i] != 0
# 
# 
# 
# Follow up: Could you solve it in O(n) time complexity and O(1) extra space
# complexity?
# 
#

# @lc code=start
from typing import List


class Solution:
    def circularArrayLoop(self, nums: List[int]) -> bool:
        n = len(nums)

        def nxt(i: int) -> int:
            return (i + nums[i]) % n

        for i in range(n):
            if nums[i] == 0:
                continue
            direction = nums[i] > 0
            slow = fast = i

            while True:
                ns = nxt(slow)
                nf = nxt(fast)
                if nums[ns] == 0 or (nums[ns] > 0) != direction:
                    break
                nnf = nxt(nf)
                if nums[nf] == 0 or (nums[nf] > 0) != direction or nums[nnf] == 0 or (nums[nnf] > 0) != direction:
                    break
                slow = ns
                fast = nnf
                if slow == fast:
                    if slow == nxt(slow):
                        break
                    return True

            j = i
            while nums[j] != 0 and (nums[j] > 0) == direction:
                nj = nxt(j)
                nums[j] = 0
                j = nj
        return False
# @lc code=end

"""
Interview explanation:
A valid loop is a directed cycle with length greater than one and all moves in the same direction. Use Floyd's slow/fast pointers from each unvisited index. After a failed search, mark that traversed same-direction path as 0 so it is never processed again.

Data structure: the array itself is used for visited marking, which keeps auxiliary space constant.

Edge cases: one-element self loops are invalid and explicitly rejected by checking slow == next(slow). Direction changes break the candidate path immediately.

Complexity: every index is marked at most once, so total time is O(n). Extra space is O(1). The input array is modified, which is acceptable for this LeetCode problem; if not, use a separate visited array.
"""
