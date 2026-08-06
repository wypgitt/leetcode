#
# @lc app=leetcode id=3082 lang=python3
#
# [3082] Find the Sum of the Power of All Subsequences
#
# https://leetcode.com/problems/find-the-sum-of-the-power-of-all-subsequences/description/
#
# algorithms
# Hard (38.10%)
# Likes:    171
# Dislikes: 4
# Total Accepted:    10.6K
# Total Submissions: 27.7K
# Testcase Example:  "[1,2,3]\n3"
#
#
# You are given an integer array nums of length n and a positive integer
# k.
#
# The power of an array of integers is defined as the number of
# subsequences with their sum equal to k.
#
# Return the sum of power of all subsequences of nums.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input:   nums = [1,2,3], k = 3
#
# Output:   6
#
# Explanation:
#
# There are 5 subsequences of nums with non-zero power:
#
# The subsequence [1,2,3] has 2 subsequences with sum == 3: [1,2,3] and
# [1,2,3].
#
# The subsequence [1,2,3] has 1 subsequence with sum == 3: [1,2,3].
#
# The subsequence [1,2,3] has 1 subsequence with sum == 3: [1,2,3].
#
# The subsequence [1,2,3] has 1 subsequence with sum == 3: [1,2,3].
#
# The subsequence [1,2,3] has 1 subsequence with sum == 3: [1,2,3].
#
# Hence the answer is 2 + 1 + 1 + 1 + 1 = 6.
#
# Example 2:
#
# Input:   nums = [2,3,3], k = 5
#
# Output:   4
#
# Explanation:
#
# There are 3 subsequences of nums with non-zero power:
#
# The subsequence [2,3,3] has 2 subsequences with sum == 5: [2,3,3] and
# [2,3,3].
#
# The subsequence [2,3,3] has 1 subsequence with sum == 5: [2,3,3].
#
# The subsequence [2,3,3] has 1 subsequence with sum == 5: [2,3,3].
#
# Hence the answer is 2 + 1 + 1 = 4.
#
# Example 3:
#
# Input:   nums = [1,2,3], k = 7
#
# Output:   0
#
# Explanation: There exists no subsequence with sum 7. Hence all
# subsequences of nums have power = 0.
#
# Constraints:
#
# 1 <= n <= 100
#
# 1 <= nums[i] <= 10^4
#
# 1 <= k <= 100
#

# @lc code=start
from typing import List


class Solution:
    def sumOfPower(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Power of a subsequence S is how many of its subsequences sum to k.
        Summing power over all subsequences of nums: each sum-k subsequence T
        of nums contributes 2^(n - |T|) (free include/exclude of unused elems).

        Algorithm:
        - dp[s] = sum of 2^(unused among processed) over subsequences with sum s.
        - On value x: skip it in the k-sum subseq (multiply ways by 2), or take it.

        Complexity: O(n * k) time, O(k) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (k + 1)
        dp[0] = 1
        for x in nums:
            ndp = [0] * (k + 1)
            for s in range(k + 1):
                if not dp[s]:
                    continue
                ndp[s] = (ndp[s] + dp[s] * 2) % MOD
                if s + x <= k:
                    ndp[s + x] = (ndp[s + x] + dp[s]) % MOD
            dp = ndp
        return dp[k]
# @lc code=end
