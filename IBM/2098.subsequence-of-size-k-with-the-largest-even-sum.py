#
# @lc app=leetcode id=2098 lang=python3
#
# [2098] Subsequence of Size K With the Largest Even Sum
#
# https://leetcode.com/problems/subsequence-of-size-k-with-the-largest-even-sum/description/
#
# algorithms
# Medium (35.65%)
# Likes:    99
# Dislikes: 8
# Total Accepted:    5K
# Total Submissions: 14.1K
# Testcase Example:  "[4,1,5,3,1]\n3"
#
#
# You are given an integer array nums and an integer k. Find the largest
# even sum of any subsequence of nums that has a length of k.
#
# Return this sum, or -1 if such a sum does not exist.
#
# A subsequence is an array that can be derived from another array by
# deleting some or no elements without changing the order of the remaining
# elements.
#
# Example 1:
#
# Input: nums = [4,1,5,3,1], k = 3
# Output: 12
# Explanation:
# The subsequence with the largest possible even sum is [4,5,3]. It has a
# sum of 4 + 5 + 3 = 12.
#
# Example 2:
#
# Input: nums = [4,6,2], k = 3
# Output: 12
# Explanation:
# The subsequence with the largest possible even sum is [4,6,2]. It has a
# sum of 4 + 6 + 2 = 12.
#
# Example 3:
#
# Input: nums = [1,3,5], k = 1
# Output: -1
# Explanation:
# No subsequence of nums with length 1 has an even sum.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#
# 1 <= k <= nums.length
#
# @lc code=start
from typing import List


class Solution:
    def largestEvenSum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Premium. Choose a subsequence of size exactly k with maximum even sum;
        return that sum or -1 if impossible.

        Algorithm:
        - Take k largest; if sum even, done. Else try replace: swap out smallest
          odd (even) in the pick for largest unused even (odd) to flip parity
          with minimal loss; pick best valid swap.

        Complexity: O(n log n) time, O(n) space.
        """
        nums.sort(reverse=True)
        s = sum(nums[:k])
        if s % 2 == 0:
            return s
        # need to flip parity by swapping
        # smallest odd in top-k vs largest even outside, or smallest even in top-k vs largest odd outside
        ans = -1
        # find candidates in top-k
        min_odd = min_even = None
        for x in nums[:k]:
            if x % 2:
                if min_odd is None or x < min_odd:
                    min_odd = x
            else:
                if min_even is None or x < min_even:
                    min_even = x
        max_odd = max_even = None
        for x in nums[k:]:
            if x % 2:
                if max_odd is None or x > max_odd:
                    max_odd = x
            else:
                if max_even is None or x > max_even:
                    max_even = x
        if min_odd is not None and max_even is not None:
            ans = max(ans, s - min_odd + max_even)
        if min_even is not None and max_odd is not None:
            ans = max(ans, s - min_even + max_odd)
        return ans
# @lc code=end
