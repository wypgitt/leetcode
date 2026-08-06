#
# @lc app=leetcode id=2863 lang=python3
#
# [2863] Maximum Length of Semi-Decreasing Subarrays
#
# https://leetcode.com/problems/maximum-length-of-semi-decreasing-subarrays/description/
#
# algorithms
# Medium (70.03%)
# Likes:    137
# Dislikes: 17
# Total Accepted:    14.5K
# Total Submissions: 20.8K
# Testcase Example:  "[7,6,5,4,3,2,1,6,10,11]"
#
#
# You are given an integer array nums.
#
# Return the length of the longest semi-decreasing subarray of nums, and 0
# if there are no such subarrays.
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# A non-empty array is semi-decreasing if its first element is strictly
# greater than its last element.
#
# Example 1:
#
# Input: nums = [7,6,5,4,3,2,1,6,10,11]
# Output: 8
# Explanation: Take the subarray [7,6,5,4,3,2,1,6].
# The first element is 7 and the last one is 6 so the condition is met.
# Hence, the answer would be the length of the subarray or 8.
# It can be shown that there aren't any subarrays with the given condition
# with a length greater than 8.
#
# Example 2:
#
# Input: nums = [57,55,50,60,61,58,63,59,64,60,63]
# Output: 6
# Explanation: Take the subarray [61,58,63,59,64,60].
# The first element is 61 and the last one is 60 so the condition is met.
# Hence, the answer would be the length of the subarray or 6.
# It can be shown that there aren't any subarrays with the given condition
# with a length greater than 6.
#
# Example 3:
#
# Input: nums = [1,2,3,4]
# Output: 0
# Explanation: Since there are no semi-decreasing subarrays in the given
# array, the answer is 0.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#
# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def maxSubarrayLength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium: semi-decreasing subarray means first element > last. Longest length, or 0.

        Algorithm:
        - Build increasing stack of candidate left indices (left-to-right).
        - Scan j right-to-left; pop lefts with nums[i] > nums[j]; track max j-i+1.

        Complexity: O(n) time and space.
        """
        stack: List[int] = []
        for i, x in enumerate(nums):
            if not stack or nums[stack[-1]] < x:
                stack.append(i)
        ans = 0
        for j in range(len(nums) - 1, -1, -1):
            while stack and nums[stack[-1]] > nums[j]:
                ans = max(ans, j - stack.pop() + 1)
        return ans

    def maxSubarrayLength_sort(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: group indices by value; scan values descending, track min index seen.

        Algorithm:
        - For value x descending, max length ends at last index of x from earlier min index.

        Complexity: O(n log n) time, O(n) space.
        """
        d: dict[int, List[int]] = defaultdict(list)
        for i, x in enumerate(nums):
            d[x].append(i)
        ans = 0
        min_i = 10**18
        for x in sorted(d, reverse=True):
            ans = max(ans, d[x][-1] - min_i + 1)
            min_i = min(min_i, d[x][0])
        return ans
# @lc code=end
