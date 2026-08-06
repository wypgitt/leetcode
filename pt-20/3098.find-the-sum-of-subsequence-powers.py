#
# @lc app=leetcode id=3098 lang=python3
#
# [3098] Find the Sum of Subsequence Powers
#
# https://leetcode.com/problems/find-the-sum-of-subsequence-powers/description/
#
# algorithms
# Hard (25.13%)
# Likes:    150
# Dislikes: 6
# Total Accepted:    7.5K
# Total Submissions: 29.7K
# Testcase Example:  "[1,2,3,4]\n3"
#
#
# You are given an integer array nums of length n, and a positive integer
# k.
#
# The power of a subsequence is defined as the minimum absolute difference
# between any two elements in the subsequence.
#
# Return the sum of powers of all subsequences of nums which have length
# equal to k.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,2,3,4], k = 3
#
# Output: 4
#
# Explanation:
#
# There are 4 subsequences in nums which have length 3: [1,2,3], [1,3,4],
# [1,2,4], and [2,3,4]. The sum of powers is |2 - 3| + |3 - 4| + |2 - 1| +
# |3 - 4| = 4.
#
# Example 2:
#
# Input: nums = [2,2], k = 2
#
# Output: 0
#
# Explanation:
#
# The only subsequence in nums which has length 2 is [2,2]. The sum of
# powers is |2 - 2| = 0.
#
# Example 3:
#
# Input: nums = [4,3,-1], k = 2
#
# Output: 10
#
# Explanation:
#
# There are 3 subsequences in nums which have length 2: [4,3], [4,-1], and
# [3,-1]. The sum of powers is |4 - 3| + |4 - (-1)| + |3 - (-1)| = 10.
#
# Constraints:
#
# 2 <= n == nums.length <= 50
#
# -10^8 <= nums[i] <= 10^8
#
# 2 <= k <= n
#

# @lc code=start
from typing import List
from functools import cache
from math import inf


class Solution:
    def sumOfPowers(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Power of a length-k subsequence = min absolute difference of any two of
        its elements. Sum powers over all length-k subsequences mod 1e9+7.

        Algorithm:
        - Sort so min pairwise diff is min of consecutive picks in the subsequence.
        - Memoized DFS(i, last, rem, mi): skip/take nums[i], update mi with
          nums[i]-nums[last]; when rem==0 contribute mi.

        Complexity: O(n^4 * k) time/space states (n <= 50).
        """
        MOD = 10**9 + 7
        n = len(nums)
        nums.sort()

        @cache
        def dfs(i: int, j: int, rem: int, mi: int) -> int:
            if rem == 0:
                return mi
            if i >= n or n - i < rem:
                return 0
            ans = dfs(i + 1, j, rem, mi)
            if j == n:
                ans += dfs(i + 1, i, rem - 1, mi)
            else:
                ans += dfs(i + 1, i, rem - 1, min(mi, nums[i] - nums[j]))
            return ans % MOD

        return dfs(0, n, k, inf)
# @lc code=end
