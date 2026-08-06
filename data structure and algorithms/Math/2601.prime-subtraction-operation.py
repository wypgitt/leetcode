#
# @lc app=leetcode id=2601 lang=python3
#
# [2601] Prime Subtraction Operation
#
# https://leetcode.com/problems/prime-subtraction-operation/description/
#
# algorithms
# Medium (55.58%)
# Likes:    945
# Dislikes: 97
# Total Accepted:    121K
# Total Submissions: 217.7K
# Testcase Example:  "[4,9,6,10]"
#
# You are given a 0-indexed integer array nums of length n.
#
# You can perform the following operation as many times as you want:
#
#
# Pick an index i that you haven’t picked before, and pick a prime p strictly
# less than nums[i], then subtract p from nums[i].
#
# Return true if you can make nums a strictly increasing array using the above
# operation and false otherwise.
#
# A strictly increasing array is an array whose each element is strictly greater
# than its preceding element.
#
#
#
# Example 1:
#
# Input: nums = [4,9,6,10]
# Output: true
# Explanation: In the first operation: Pick i = 0 and p = 3, and then subtract 3
# from nums[0], so that nums becomes [1,9,6,10].
# In the second operation: i = 1, p = 7, subtract 7 from nums[1], so nums
# becomes equal to [1,2,6,10].
# After the second operation, nums is sorted in strictly increasing order, so
# the answer is true.
#
# Example 2:
#
# Input: nums = [6,8,11,12]
# Output: true
# Explanation: Initially nums is sorted in strictly increasing order, so we
# don't need to make any operations.
#
# Example 3:
#
# Input: nums = [5,8,3]
# Output: false
# Explanation: It can be proven that there is no way to perform operations to
# make nums sorted in strictly increasing order, so the answer is false.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= nums[i] <= 1000
#
#
# nums.length == n
#

# @lc code=start
from typing import List
from bisect import bisect_left


class Solution:
    def primeSubOperation(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        At most one prime subtraction per index; make the array strictly increasing
        by greedily shrinking each value just above the previous one.

        Algorithm:
        - Sieve primes up to 1000.
        - Left to right: for each nums[i], find the largest prime p < nums[i] such
          that nums[i] - p > prev; else keep nums[i] if > prev; else fail.

        Complexity: O(M log log M + n log π(M)) time, O(M) space (M=1000).
        """
        M = 1001
        is_prime = [True] * M
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(M**0.5) + 1):
            if is_prime[i]:
                for j in range(i * i, M, i):
                    is_prime[j] = False
        primes = [i for i in range(M) if is_prime[i]]

        prev = 0
        for x in nums:
            # need x - p > prev and p < x => p < x - prev
            limit = x - prev
            if limit <= 1:
                if x <= prev:
                    return False
                prev = x
                continue
            # largest prime strictly less than min(x, limit) = limit (since limit <= x)
            idx = bisect_left(primes, limit) - 1
            if idx >= 0:
                prev = x - primes[idx]
            else:
                if x <= prev:
                    return False
                prev = x
        return True
# @lc code=end
