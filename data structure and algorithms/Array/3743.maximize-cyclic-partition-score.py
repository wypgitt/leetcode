#
# @lc app=leetcode id=3743 lang=python3
#
# [3743] Maximize Cyclic Partition Score
#
# https://leetcode.com/problems/maximize-cyclic-partition-score/description/
#
# algorithms
# Hard (14.37%)
# Likes:    55
# Dislikes: 7
# Total Accepted:    3.6K
# Total Submissions: 25K
# Testcase Example:  "[1,3,4]\n2"
#
#
# You are given a cyclic array nums and an integer k.
#
# Partition nums into at most k subarrays. As nums is cyclic, these
# subarrays may wrap around from the end of the array back to the
# beginning.
#
# The range of a subarray is the difference between its maximum and
# minimum values. The score of a partition is the sum of subarray ranges.
#
# Return the maximum possible score among all cyclic partitions.
#
# Example 1:
#
# Input: nums = [1,2,3,3], k = 2
#
# Output: 3
#
# Explanation:
#
# Partition nums into [2, 3] and [3, 1] (wrapped around).
#
# The range of [2, 3] is max(2, 3) - min(2, 3) = 3 - 2 = 1.
#
# The range of [3, 1] is max(3, 1) - min(3, 1) = 3 - 1 = 2.
#
# The score is 1 + 2 = 3.
#
# Example 2:
#
# Input: nums = [1,2,3,3], k = 1
#
# Output: 2
#
# Explanation:
#
# Partition nums into [1, 2, 3, 3].
#
# The range of [1, 2, 3, 3] is max(1, 2, 3, 3) - min(1, 2, 3, 3) = 3 - 1 =
# 2.
#
# The score is 2.
#
# Example 3:
#
# Input: nums = [1,2,3,3], k = 4
#
# Output: 3
#
# Explanation:
#
# Identical to Example 1, we partition nums into [2, 3] and [3, 1]. Note
# that nums may be partitioned into fewer than k subarrays.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= nums.length
#

# @lc code=start
from typing import List


class Solution:
    def maximumScore(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Each part's range (max - min) is one "transaction". On a cycle, break at a
        global minimum and solve the linear at-most-k range-sum maximization twice.

        Algorithm:
        - Stock-V style DP on a rotation: close a part by pairing +value (as max)
          with -value (as min); at most k parts.
        - Take the better of starting at the min index or min index + 1.

        Complexity: O(n k) time, O(n) space.
        """
        n = len(nums)

        def linear_score(base: int) -> int:
            dp = [0] * (n + 1)
            result = 0
            for t in range(k):
                x = y = float("-inf")
                new_dp = [float("-inf")] * (n + 1)
                for j in range(t, n):
                    v = nums[(base + j) % n]
                    x = max(x, dp[j] - v)
                    y = max(y, dp[j] + v)
                    new_dp[j + 1] = max(new_dp[j], x + v, y - v)
                dp = new_dp
                result = max(result, dp[-1])
            return result

        i = min(range(n), key=lambda idx: nums[idx])
        return max(linear_score(i), linear_score(i + 1))
# @lc code=end
