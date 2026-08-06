#
# @lc app=leetcode id=3618 lang=python3
#
# [3618] Split Array by Prime Indices
#
# https://leetcode.com/problems/split-array-by-prime-indices/description/
#
# algorithms
# Medium (49.68%)
# Likes:    57
# Dislikes: 3
# Total Accepted:    38.8K
# Total Submissions: 78.1K
# Testcase Example:  "[2,3,4]"
#
#
# You are given an integer array nums.
#
# Split nums into two arrays A and B using the following rule:
#
# Elements at prime indices in nums must go into array A.
#
# All other elements must go into array B.
#
# Return the absolute difference between the sums of the two arrays:
# |sum(A) - sum(B)|.
#
# Note: An empty array has a sum of 0.
#
# Example 1:
#
# Input: nums = [2,3,4]
#
# Output: 1
#
# Explanation:
#
# The only prime index in the array is 2, so nums[2] = 4 is placed in
# array A.
#
# The remaining elements, nums[0] = 2 and nums[1] = 3 are placed in array
# B.
#
# sum(A) = 4, sum(B) = 2 + 3 = 5.
#
# The absolute difference is |4 - 5| = 1.
#
# Example 2:
#
# Input: nums = [-1,5,7,0]
#
# Output: 3
#
# Explanation:
#
# The prime indices in the array are 2 and 3, so nums[2] = 7 and nums[3] =
# 0 are placed in array A.
#
# The remaining elements, nums[0] = -1 and nums[1] = 5 are placed in array
# B.
#
# sum(A) = 7 + 0 = 7, sum(B) = -1 + 5 = 4.
#
# The absolute difference is |7 - 4| = 3.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def splitArray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sum elements at prime indices into A, others into B; return |sumA-sumB|.

        Algorithm:
        - Sieve primes up to n-1; accumulate signed sum (prime index +, else -).

        Complexity: O(n log log n) time, O(n) space.
        """
        n = len(nums)
        is_prime = [True] * n
        if n:
            is_prime[0] = False
        if n > 1:
            is_prime[1] = False
        p = 2
        while p * p < n:
            if is_prime[p]:
                for j in range(p * p, n, p):
                    is_prime[j] = False
            p += 1

        total = 0
        for i, x in enumerate(nums):
            total += x if is_prime[i] else -x
        return abs(total)

    def splitArray_trial(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: test each index for primality by trial division.

        Algorithm:
        - For each index, trial-divide; accumulate |sumA - sumB| the same way.

        Complexity: O(n √n) time, O(1) extra space.
        """
        def is_prime(x: int) -> bool:
            if x < 2:
                return False
            d = 2
            while d * d <= x:
                if x % d == 0:
                    return False
                d += 1
            return True

        total = 0
        for i, x in enumerate(nums):
            total += x if is_prime(i) else -x
        return abs(total)
# @lc code=end
