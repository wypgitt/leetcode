#
# @lc app=leetcode id=1589 lang=python3
#
# [1589] Maximum Sum Obtained of Any Permutation
#
# https://leetcode.com/problems/maximum-sum-obtained-of-any-permutation/description/
#
# algorithms
# Medium (41.24%)
# Likes:    844
# Dislikes: 41
# Total Accepted:    31.3K
# Total Submissions: 75.9K
# Testcase Example:  "[1,2,3,4,5]"
#
# We have an array of integers, nums, and an array of requests where
# requests[i] = [start_i, end_i]. The i^th request asks for the sum of
# nums[start_i] + nums[start_i + 1] + ... + nums[end_i - 1] + nums[end_i]. Both
# start_i and end_i are 0-indexed.
#
# Return the maximum total sum of all requests among all permutations of nums.
#
# Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5], requests = [[1,3],[0,1]]
# Output: 19
# Explanation: One permutation of nums is [2,1,3,4,5] with the following
# result:
# requests[0] -> nums[1] + nums[2] + nums[3] = 1 + 3 + 4 = 8
# requests[1] -> nums[0] + nums[1] = 2 + 1 = 3
# Total sum: 8 + 3 = 11.
# A permutation with a higher total sum is [3,5,4,2,1] with the following
# result:
# requests[0] -> nums[1] + nums[2] + nums[3] = 5 + 4 + 2 = 11
# requests[1] -> nums[0] + nums[1] = 3 + 5 = 8
# Total sum: 11 + 8 = 19, which is the best that you can do.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5,6], requests = [[0,1]]
# Output: 11
# Explanation: A permutation with the max total sum is [6,5,4,3,2,1] with
# request sums [11].
#
# Example 3:
#
# Input: nums = [1,2,3,4,5,10], requests = [[0,2],[1,3],[1,1]]
# Output: 47
# Explanation: A permutation with the max total sum is [4,10,5,3,2,1] with
# request sums [19,18,10].
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^5
#
# 0 <= nums[i] <= 10^5
#
# 1 <= requests.length <= 10^5
#
# requests[i].length == 2
#
# 0 <= start_i <= end_i < n
#

# @lc code=start
from typing import List


class Solution:
    def maxSumRangeQuery(self, nums: List[int], requests: List[List[int]]) -> int:
        """
        Interview explanation:
        Assign permutation of nums to maximize sum of range-sum queries.
        Frequency of how often each index is requested via diff array; sort
        freqs and nums; pair largest nums with most frequent indices. Mod 1e9+7.

        Algorithm (diff + sort):
        - diff[l]+=1; diff[r+1]-=1; prefix → freq; sort freq & nums; dot product.

        Complexity: O(n log n + R) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        diff = [0] * (n + 1)
        for l, r in requests:
            diff[l] += 1
            diff[r + 1] -= 1
        freq = [0] * n
        cur = 0
        for i in range(n):
            cur += diff[i]
            freq[i] = cur
        freq.sort()
        nums.sort()
        return sum(a * b for a, b in zip(freq, nums)) % MOD
# @lc code=end

