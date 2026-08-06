#
# @lc app=leetcode id=2518 lang=python3
#
# [2518] Number of Great Partitions
#
# https://leetcode.com/problems/number-of-great-partitions/description/
#
# algorithms
# Hard (33.78%)
# Likes:    500
# Dislikes: 12
# Total Accepted:    14.4K
# Total Submissions: 42.7K
# Testcase Example:  "[1,2,3,4]\n4"
#
# You are given an array nums consisting of positive integers and an integer k.
#
# Partition the array into two ordered groups such that each element is in
# exactly one group. A partition is called great if the sum of elements of each
# group is greater than or equal to k.
#
# Return the number of distinct great partitions. Since the answer may be too
# large, return it modulo 10^9 + 7.
#
# Two partitions are considered distinct if some element nums[i] is in different
# groups in the two partitions.
#
#
#
# Example 1:
#
# Input: nums = [1,2,3,4], k = 4
# Output: 6
# Explanation: The great partitions are: ([1,2,3], [4]), ([1,3], [2,4]), ([1,4],
# [2,3]), ([2,3], [1,4]), ([2,4], [1,3]) and ([4], [1,2,3]).
#
# Example 2:
#
# Input: nums = [3,3,3], k = 4
# Output: 0
# Explanation: There are no great partitions for this array.
#
# Example 3:
#
# Input: nums = [6,6], k = 2
# Output: 2
# Explanation: We can either put nums[0] in the first partition or in the second
# partition.
# The great partitions will be ([6], [6]) and ([6], [6]).
#
#
#
# Constraints:
#
#
# 1 <= nums.length, k <= 1000
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def countPartitions(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count ways to bipartition nums so both groups have sum >= k (mod 10^9+7).

        Algorithm:
        (DP subset sum)
        - If total < 2k return 0.
        - Total assignments 2^n; subtract those with a group sum < k:
          2 * (count of subsets with sum in [0, k)).

        Complexity: O(n * k) time, O(k) space.
        """
        MOD = 10**9 + 7
        total = sum(nums)
        if total < 2 * k:
            return 0
        n = len(nums)
        dp = [0] * k
        dp[0] = 1
        for x in nums:
            if x >= k:
                continue
            for s in range(k - 1, x - 1, -1):
                dp[s] = (dp[s] + dp[s - x]) % MOD
        bad = sum(dp) % MOD
        return (pow(2, n, MOD) - 2 * bad) % MOD
# @lc code=end
