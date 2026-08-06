#
# @lc app=leetcode id=2411 lang=python3
#
# [2411] Smallest Subarrays With Maximum Bitwise OR
#
# https://leetcode.com/problems/smallest-subarrays-with-maximum-bitwise-or/description/
#
# algorithms
# Medium (61.93%)
# Likes:    1058
# Dislikes: 73
# Total Accepted:    96.2K
# Total Submissions: 155.3K
# Testcase Example:  "[1,0,2,1,3]"
#
# You are given a 0-indexed array nums of length n, consisting of non-negative
# integers. For each index i from 0 to n - 1, you must determine the size of the
# minimum sized non-empty subarray of nums starting at i (inclusive) that has
# the maximum possible bitwise OR.
#
#
# In other words, let B_ij be the bitwise OR of the subarray nums[i...j]. You
# need to find the smallest subarray starting at i, such that bitwise OR of this
# subarray is equal to max(B_ik) where i <= k <= n - 1.
#
# The bitwise OR of an array is the bitwise OR of all the numbers in it.
#
# Return an integer array answer of size n where answer[i] is the length of the
# minimum sized subarray starting at i with maximum bitwise OR.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [1,0,2,1,3]
# Output: [3,3,2,2,1]
# Explanation:
# The maximum possible bitwise OR starting at any index is 3.
# - Starting at index 0, the shortest subarray that yields it is [1,0,2].
# - Starting at index 1, the shortest subarray that yields the maximum bitwise
# OR is [0,2,1].
# - Starting at index 2, the shortest subarray that yields the maximum bitwise
# OR is [2,1].
# - Starting at index 3, the shortest subarray that yields the maximum bitwise
# OR is [1,3].
# - Starting at index 4, the shortest subarray that yields the maximum bitwise
# OR is [3].
# Therefore, we return [3,3,2,2,1].
#
# Example 2:
#
# Input: nums = [1,2]
# Output: [2,1]
# Explanation:
# Starting at index 0, the shortest subarray that yields the maximum bitwise OR
# is of length 2.
# Starting at index 1, the shortest subarray that yields the maximum bitwise OR
# is of length 1.
# Therefore, we return [2,1].
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 1 <= n <= 10^5
#
#
# 0 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def smallestSubarrays(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        For each i, shortest subarray starting at i whose OR equals OR of nums[i:].

        Algorithm:
        - Track last index of each bit; for i from right, update bit positions;
          ans[i] = max(last bit index) - i + 1 (or 1).

        Complexity: O(n * 32) time, O(1) extra space.
        """
        n = len(nums)
        ans = [1] * n
        last = [-1] * 32
        for i in range(n - 1, -1, -1):
            for b in range(32):
                if nums[i] & (1 << b):
                    last[b] = i
            farthest = i
            for b in range(32):
                if last[b] != -1:
                    farthest = max(farthest, last[b])
            ans[i] = farthest - i + 1
        return ans
# @lc code=end
