#
# @lc app=leetcode id=3346 lang=python3
#
# [3346] Maximum Frequency of an Element After Performing Operations I
#
# https://leetcode.com/problems/maximum-frequency-of-an-element-after-performing-operations-i/description/
#
# algorithms
# Medium (40.22%)
# Likes:    655
# Dislikes: 108
# Total Accepted:    91.7K
# Total Submissions: 227.9K
# Testcase Example:  "[1,4,5]\n1\n2"
#
#
# You are given an integer array nums and two integers k and
# numOperations.
#
# You must perform an operation numOperations times on nums, where in each
# operation you:
#
# Select an index i that was not selected in any previous operations.
#
# Add an integer in the range [-k, k] to nums[i].
#
# Return the maximum possible frequency of any element in nums after
# performing the operations.
#
# Example 1:
#
# Input: nums = [1,4,5], k = 1, numOperations = 2
#
# Output: 2
#
# Explanation:
#
# We can achieve a maximum frequency of two by:
#
# Adding 0 to nums[1]. nums becomes [1, 4, 5].
#
# Adding -1 to nums[2]. nums becomes [1, 4, 4].
#
# Example 2:
#
# Input: nums = [5,11,20,20], k = 5, numOperations = 1
#
# Output: 2
#
# Explanation:
#
# We can achieve a maximum frequency of two by:
#
# Adding 0 to nums[1].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 0 <= k <= 10^5
#
# 0 <= numOperations <= nums.length
#

# @lc code=start

from typing import List


class Solution:
    def maxFrequency(self, nums: List[int], k: int, numOperations: int) -> int:
        """
        Interview explanation:
        Each index may be shifted by at most k at most once. Maximize frequency
        of some target T. Values ≤ 1e5 → difference array over possible T.

        Algorithm:
        - For each nums[i]=x, add +1 on target range [x-k, x+k] (clipped).
        - For each T, reachable count = prefix of diff; answer
          min(reachable, freq[T] + numOperations).

        Complexity: O(U + n) time, O(U) space where U = max(nums).
        """
        mx = max(nums)
        freq = [0] * (mx + 1)
        diff = [0] * (mx + 2)
        for x in nums:
            freq[x] += 1
            L = max(0, x - k)
            R = min(mx, x + k)
            diff[L] += 1
            diff[R + 1] -= 1
        ans = cur = 0
        for t in range(mx + 1):
            cur += diff[t]
            ans = max(ans, min(cur, freq[t] + numOperations))
        return ans
# @lc code=end
