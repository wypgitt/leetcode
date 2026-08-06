#
# @lc app=leetcode id=325 lang=python3
#
# [325] Maximum Size Subarray Sum Equals k
#
# https://leetcode.com/problems/maximum-size-subarray-sum-equals-k/description/
#
# algorithms
# Medium (50.92%)
# Likes:    2130
# Dislikes: 66
# Total Accepted:    223.4K
# Total Submissions: 438.7K
# Testcase Example:  "[1,-1,5,-2,3]\n3"
#
#
# Given an integer array nums and an integer k, return the maximum length
# of a subarray that sums to k. If there is not one, return 0 instead.
#
# Example 1:
#
# Input: nums = [1,-1,5,-2,3], k = 3
# Output: 4
# Explanation: The subarray [1, -1, 5, -2] sums to 3 and is the longest.
#
# Example 2:
#
# Input: nums = [-2,-1,2,1], k = 1
# Output: 2
# Explanation: The subarray [-1, 2] sums to 1 and is the longest.
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^5
#
# -10^4 <= nums[i] <= 10^4
#
# -10^9 <= k <= 10^9
#
# @lc code=start
from typing import List


class Solution:
    def maxSubArrayLen(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Prefix sums + hashmap: if prefix[j] - prefix[i] == k then subarray
        (i+1..j) sums to k. Store earliest index of each prefix for max length.

        Algorithm:
        - Scan with running sum; if sum == k update answer with i+1.
        - If sum - k seen before, length = i - first_index[sum-k].
        - Record first occurrence of each prefix only.

        Complexity: O(n) time and space.
        """
        first = {0: -1}
        prefix = 0
        best = 0
        for i, num in enumerate(nums):
            prefix += num
            need = prefix - k
            if need in first:
                best = max(best, i - first[need])
            if prefix not in first:
                first[prefix] = i
        return best
# @lc code=end
