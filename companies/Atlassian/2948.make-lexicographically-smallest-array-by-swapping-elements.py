#
# @lc app=leetcode id=2948 lang=python3
#
# [2948] Make Lexicographically Smallest Array by Swapping Elements
#
# https://leetcode.com/problems/make-lexicographically-smallest-array-by-swapping-elements/description/
#
# algorithms
# Medium (60.13%)
# Likes:    982
# Dislikes: 79
# Total Accepted:    103.3K
# Total Submissions: 171.8K
# Testcase Example:  "[1,5,3,9,8]\n2"
#
#
# You are given a 0-indexed array of positive integers nums and a positive
# integer limit.
#
# In one operation, you can choose any two indices i and j and swap
# nums[i] and nums[j] if |nums[i] - nums[j]| <= limit.
#
# Return the lexicographically smallest array that can be obtained by
# performing the operation any number of times.
#
# An array a is lexicographically smaller than an array b if in the first
# position where a and b differ, array a has an element that is less than
# the corresponding element in b. For example, the array [2,10,3] is
# lexicographically smaller than the array [10,2,3] because they differ at
# index 0 and 2 < 10.
#
# Example 1:
#
# Input: nums = [1,5,3,9,8], limit = 2
# Output: [1,3,5,8,9]
# Explanation: Apply the operation 2 times:
# - Swap nums[1] with nums[2]. The array becomes [1,3,5,9,8]
# - Swap nums[3] with nums[4]. The array becomes [1,3,5,8,9]
# We cannot obtain a lexicographically smaller array by applying any more
# operations.
# Note that it may be possible to get the same result by doing different
# operations.
#
# Example 2:
#
# Input: nums = [1,7,6,18,2,1], limit = 3
# Output: [1,6,7,18,1,2]
# Explanation: Apply the operation 3 times:
# - Swap nums[1] with nums[2]. The array becomes [1,6,7,18,2,1]
# - Swap nums[0] with nums[4]. The array becomes [2,6,7,18,1,1]
# - Swap nums[0] with nums[5]. The array becomes [1,6,7,18,1,2]
# We cannot obtain a lexicographically smaller array by applying any more
# operations.
#
# Example 3:
#
# Input: nums = [1,7,28,19,10], limit = 3
# Output: [1,7,28,19,10]
# Explanation: [1,7,28,19,10] is the lexicographically smallest array we
# can obtain because we cannot apply the operation on any two indices.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= limit <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def lexicographicallySmallestArray(self, nums: List[int], limit: int) -> List[int]:
        """
        Interview explanation:
        Swaps are allowed when |a-b|<=limit; transitively, values in a
        connected component (sorted by value with consecutive gaps <= limit)
        can be freely rearranged among their positions.

        Algorithm:
        - Sort (value, index). Split into groups where consecutive values
          differ by > limit. Within each group, sort indices and assign
          sorted values to those positions.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        order = sorted(range(n), key=lambda i: nums[i])
        ans = [0] * n
        i = 0
        while i < n:
            j = i + 1
            while j < n and nums[order[j]] - nums[order[j - 1]] <= limit:
                j += 1
            indices = sorted(order[i:j])
            values = sorted(nums[p] for p in order[i:j])
            for idx, val in zip(indices, values):
                ans[idx] = val
            i = j
        return ans
# @lc code=end

