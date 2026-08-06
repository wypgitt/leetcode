#
# @lc app=leetcode id=2031 lang=python3
#
# [2031] Count Subarrays With More Ones Than Zeros
#
# https://leetcode.com/problems/count-subarrays-with-more-ones-than-zeros/description/
#
# algorithms
# Medium (49.68%)
# Likes:    187
# Dislikes: 18
# Total Accepted:    5.7K
# Total Submissions: 11.4K
# Testcase Example:  "[0,1,1,0,1]"
#
#
# You are given a binary array nums containing only the integers 0 and 1.
# Return the number of subarrays in nums that have more 1's than 0's.
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# A subarray is a contiguous sequence of elements within an array.
#
# Example 1:
#
# Input: nums = [0,1,1,0,1]
# Output: 9
# Explanation:
# The subarrays of size 1 that have more ones than zeros are: [1], [1],
# [1]
# The subarrays of size 2 that have more ones than zeros are: [1,1]
# The subarrays of size 3 that have more ones than zeros are: [0,1,1],
# [1,1,0], [1,0,1]
# The subarrays of size 4 that have more ones than zeros are: [1,1,0,1]
# The subarrays of size 5 that have more ones than zeros are: [0,1,1,0,1]
#
# Example 2:
#
# Input: nums = [0]
# Output: 0
# Explanation:
# No subarrays have more ones than zeros.
#
# Example 3:
#
# Input: nums = [1]
# Output: 1
# Explanation:
# The subarrays of size 1 that have more ones than zeros are: [1]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 1
#
# @lc code=start
from typing import List


class Solution:
    def subarraysWithMoreOnesThanZeros(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium: count subarrays with strictly more 1s than 0s. Map 0->-1, 1->1;
        count subarrays with positive sum. MOD = 1e9+7.

        Algorithm:
        - Prefix sums; Fenwick/BIT counting previous prefixes < current
          (equivalently how many prev with cur-prev > 0).

        Complexity: O(n log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        # prefix in [-n, n] -> shift by n
        size = 2 * n + 2
        bit = [0] * (size + 1)

        def add(i, v):
            i += 1
            while i <= size:
                bit[i] += v
                i += i & -i

        def sum_to(i):
            i += 1
            s = 0
            while i > 0:
                s += bit[i]
                i -= i & -i
            return s

        # index of prefix value p is p + n
        add(n, 1)  # prefix 0
        pref = 0
        ans = 0
        for x in nums:
            pref += 1 if x == 1 else -1
            # count previous prefixes < pref
            ans = (ans + sum_to(pref + n - 1)) % MOD
            add(pref + n, 1)
        return ans
# @lc code=end
