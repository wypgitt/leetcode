#
# @lc app=leetcode id=2856 lang=python3
#
# [2856] Minimum Array Length After Pair Removals
#
# https://leetcode.com/problems/minimum-array-length-after-pair-removals/description/
#
# algorithms
# Medium (27.97%)
# Likes:    427
# Dislikes: 109
# Total Accepted:    33.8K
# Total Submissions: 121K
# Testcase Example:  "[1,2,3,4]"
#
#
# Given an integer array num sorted in non-decreasing order.
#
# You can perform the following operation any number of times:
#
# Choose two indices, i and j, where nums[i] < nums[j].
#
# Then, remove the elements at indices i and j from nums. The remaining
# elements retain their original order, and the array is re-indexed.
#
# Return the minimum length of nums after applying the operation zero or
# more times.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
#
# Output: 0
#
# Explanation:
#
# Example 2:
#
# Input: nums = [1,1,2,2,3,3]
#
# Output: 0
#
# Explanation:
#
# Example 3:
#
# Input: nums = [1000000000,1000000000]
#
# Output: 2
#
# Explanation:
#
# Since both numbers are equal, they cannot be removed.
#
# Example 4:
#
# Input: nums = [2,3,4,4,4]
#
# Output: 1
#
# Explanation:
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# nums is sorted in non-decreasing order.
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def minLengthAfterRemovals(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sorted nums; repeatedly remove a pair with nums[i] < nums[j]. Min remaining length.

        Algorithm:
        - Pairing can remove everything except leftover copies of the mode.
        - If max frequency f > n/2, remainder is 2f - n; else at most n % 2.

        Complexity: O(n) time, O(n) space (or O(1) via middle element of sorted array).
        """
        n = len(nums)
        f = Counter(nums).most_common(1)[0][1]
        return max(2 * f - n, n % 2)

    def minLengthAfterRemovals_two_pointers(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: greedily pair first half with second half via two pointers.

        Algorithm:
        - i from 0, j from (n+1)//2; whenever nums[i] < nums[j], pair and advance both.
        - Remaining = n - 2 * pairs.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        i, j = 0, (n + 1) // 2
        pairs = 0
        while i < (n + 1) // 2 and j < n:
            if nums[i] < nums[j]:
                pairs += 1
                i += 1
                j += 1
            else:
                j += 1
        return n - 2 * pairs
# @lc code=end
