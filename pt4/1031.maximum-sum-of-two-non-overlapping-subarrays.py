#
# @lc app=leetcode id=1031 lang=python3
#
# [1031] Maximum Sum of Two Non-Overlapping Subarrays
#
# https://leetcode.com/problems/maximum-sum-of-two-non-overlapping-subarrays/description/
#
# algorithms
# Medium (60.84%)
# Likes:    2666
# Dislikes: 88
# Total Accepted:    85.3K
# Total Submissions: 140.3K
# Testcase Example:  '[0,6,5,2,2,5,1,9,4]\n1\n2'
#
# Given an integer array nums and two integers firstLen and secondLen, return
# the maximum sum of elements in two non-overlapping subarrays with lengths
# firstLen and secondLen.
# 
# The array with length firstLen could occur before or after the array with
# length secondLen, but they have to be non-overlapping.
# 
# A subarray is a contiguous part of an array.
# 
# 
# Example 1:
# 
# 
# Input: nums = [0,6,5,2,2,5,1,9,4], firstLen = 1, secondLen = 2
# Output: 20
# Explanation: One choice of subarrays is [9] with length 1, and [6,5] with
# length 2.
# 
# 
# Example 2:
# 
# 
# Input: nums = [3,8,1,3,2,1,8,9,0], firstLen = 3, secondLen = 2
# Output: 29
# Explanation: One choice of subarrays is [3,8,1] with length 3, and [8,9] with
# length 2.
# 
# 
# Example 3:
# 
# 
# Input: nums = [2,1,5,6,0,9,5,0,3,8], firstLen = 4, secondLen = 3
# Output: 31
# Explanation: One choice of subarrays is [5,6,0,9] with length 4, and [0,3,8]
# with length 3.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= firstLen, secondLen <= 1000
# 2 <= firstLen + secondLen <= 1000
# firstLen + secondLen <= nums.length <= 1000
# 0 <= nums[i] <= 1000
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def maxSumTwoNoOverlap(self, nums: List[int], firstLen: int, secondLen: int) -> int:
        prefix = [0]
        for num in nums:
            prefix.append(prefix[-1] + num)

        def best_with_order(left_len: int, right_len: int) -> int:
            best_left = 0
            answer = 0

            for right_end in range(left_len + right_len, len(nums) + 1):
                left_end = right_end - right_len
                left_sum = prefix[left_end] - prefix[left_end - left_len]
                best_left = max(best_left, left_sum)

                right_sum = prefix[right_end] - prefix[right_end - right_len]
                answer = max(answer, best_left + right_sum)

            return answer

        return max(
            best_with_order(firstLen, secondLen),
            best_with_order(secondLen, firstLen),
        )
# @lc code=end

"""
Interview Explanation

Core idea:
The two subarrays can appear in either order. If we fix the order, say L-length
before M-length, then while scanning the M subarray's end position we only need
the best L subarray seen completely to its left.

Algorithm:
1. Build prefix sums so every fixed-length subarray sum is O(1).
2. Define a helper for the order left_len before right_len.
3. Sweep the end of the right subarray from left to right.
4. Maintain best_left, the maximum left_len subarray sum ending before the
   right subarray starts.
5. Combine best_left with the current right subarray.
6. Run the helper for both orders and take the maximum.

Data structure choice:
Prefix sums are the right structure for repeated range-sum queries. They avoid
recomputing subarray sums inside the scan.

Correctness:
For a fixed right subarray position, any valid left subarray must end before
the right subarray starts. best_left is exactly the maximum among all such
choices, so combining it with the current right subarray gives the best pair
ending there. Scanning all right positions covers every pair in that order, and
checking both orders covers all non-overlapping arrangements.

Complexity:
Prefix construction and both sweeps are O(n). Prefix space is O(n).

Tests and edge cases:
- firstLen and secondLen equal: both helper calls are equivalent and safe.
- The two subarrays exactly fill the array.
- Arrays with zeros: best_left starts at 0, valid because nums are nonnegative.
- Best firstLen subarray can appear after secondLen; the second helper handles
  that order.
"""
