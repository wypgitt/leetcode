#
# @lc app=leetcode id=3712 lang=python3
#
# [3712] Sum of Elements With Frequency Divisible by K
#
# https://leetcode.com/problems/sum-of-elements-with-frequency-divisible-by-k/description/
#
# algorithms
# Easy (78.39%)
# Likes:    61
# Dislikes: 4
# Total Accepted:    55.8K
# Total Submissions: 71.1K
# Testcase Example:  "[1,2,2,3,3,3,3,4]\n2"
#
#
# You are given an integer array nums and an integer k.
#
# Return an integer denoting the sum of all elements in nums whose
# frequency is divisible by k, or 0 if there are no such elements.
#
# Note: An element is included in the sum exactly as many times as it
# appears in the array if its total frequency is divisible by k.
#
# Example 1:
#
# Input: nums = [1,2,2,3,3,3,3,4], k = 2
#
# Output: 16
#
# Explanation:
#
# The number 1 appears once (odd frequency).
#
# The number 2 appears twice (even frequency).
#
# The number 3 appears four times (even frequency).
#
# The number 4 appears once (odd frequency).
#
# So, the total sum is 2 + 2 + 3 + 3 + 3 + 3 = 16.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5], k = 2
#
# Output: 0
#
# Explanation:
#
# There are no elements that appear an even number of times, so the total
# sum is 0.
#
# Example 3:
#
# Input: nums = [4,4,4,1,2,3], k = 3
#
# Output: 12
#
# Explanation:
#
# The number 1 appears once.
#
# The number 2 appears once.
#
# The number 3 appears once.
#
# The number 4 appears three times.
#
# So, the total sum is 4 + 4 + 4 = 12.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#
# 1 <= k <= 100
#

# @lc code=start

from collections import Counter
from typing import List


class Solution:
    def sumDivisibleByK(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Sum every occurrence of values whose frequency is divisible by k.

        Algorithm:
        - Count frequencies; for each value with freq % k == 0, add value * freq.

        Complexity: O(n) time, O(n) space.
        """
        return sum(v * c for v, c in Counter(nums).items() if c % k == 0)

    def sumDivisibleByK_manual(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: frequency array (values are small).

        Algorithm:
        - Bucket counts in an array of size 101; same aggregation.

        Complexity: O(n + U) time, O(U) space (U = 100).
        """
        freq = [0] * 101
        for x in nums:
            freq[x] += 1
        return sum(v * freq[v] for v in range(101) if freq[v] and freq[v] % k == 0)
# @lc code=end
