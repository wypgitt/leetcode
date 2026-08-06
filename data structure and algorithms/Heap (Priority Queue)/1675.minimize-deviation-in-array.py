#
# @lc app=leetcode id=1675 lang=python3
#
# [1675] Minimize Deviation in Array
#
# https://leetcode.com/problems/minimize-deviation-in-array/description/
#
# algorithms
# Hard (54.01%)
# Likes:    3098
# Dislikes: 175
# Total Accepted:    102K
# Total Submissions: 189K
# Testcase Example:  "[1,2,3,4]"
#
# You are given an array nums of n positive integers.
#
# You can perform two types of operations on any element of the array any
# number of times:
#
# If the element is even, divide it by 2.
#
# For example, if the array is [1,2,3,4], then you can do this operation on the
# last element, and the array will be [1,2,3,2].
#
# If the element is odd, multiply it by 2.
#
# For example, if the array is [1,2,3,4], then you can do this operation on the
# first element, and the array will be [2,2,3,4].
#
# The deviation of the array is the maximum difference between any two elements
# in the array.
#
# Return the minimum deviation the array can have after performing some number
# of operations.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
# Output: 1
# Explanation: You can transform the array to [1,2,3,2], then to [2,2,3,2],
# then the deviation will be 3 - 2 = 1.
#
# Example 2:
#
# Input: nums = [4,1,5,20,3]
# Output: 3
# Explanation: You can transform the array after two operations to [4,2,5,5,3],
# then the deviation will be 5 - 2 = 3.
#
# Example 3:
#
# Input: nums = [2,10,8]
# Output: 3
#
# Constraints:
#
# n == nums.length
#
# 2 <= n <= 5 * 10^4
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minimumDeviation(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Odd numbers may *2 once; even may /2 until odd. Minimize max-min after
        ops. Normalize: multiply all odds by 2 so only decreases (/2) remain;
        max-heap of currents + track global min; repeatedly /2 the max while even.

        Algorithm (max-heap):
        - Make all even (odds*2); heap=-v; mn=min; while max even: pop, /2, push, update ans.

        Complexity: O(n log n * log M) time, O(n) space.
        """
        heap = []
        mn = float("inf")
        for v in nums:
            if v % 2:
                v *= 2
            mn = min(mn, v)
            heapq.heappush(heap, -v)
        ans = float("inf")
        while True:
            mx = -heapq.heappop(heap)
            ans = min(ans, mx - mn)
            if mx % 2:
                break
            mx //= 2
            mn = min(mn, mx)
            heapq.heappush(heap, -mx)
        return ans
# @lc code=end
