#
# @lc app=leetcode id=1726 lang=python3
#
# [1726] Tuple with Same Product
#
# https://leetcode.com/problems/tuple-with-same-product/description/
#
# algorithms
# Medium (70.06%)
# Likes:    1377
# Dislikes: 59
# Total Accepted:    201K
# Total Submissions: 286K
# Testcase Example:  "[2,3,4,6]"
#
# Given an array nums of distinct positive integers, return the number of
# tuples (a, b, c, d) such that a * b = c * d where a, b, c, and d are elements
# of nums, and a != b != c != d.
#
# Example 1:
#
# Input: nums = [2,3,4,6]
# Output: 8
# Explanation: There are 8 valid tuples:
# (2,6,3,4) , (2,6,4,3) , (6,2,3,4) , (6,2,4,3)
# (3,4,2,6) , (4,3,2,6) , (3,4,6,2) , (4,3,6,2)
#
# Example 2:
#
# Input: nums = [1,2,4,5,10]
# Output: 16
# Explanation: There are 16 valid tuples:
# (1,10,2,5) , (1,10,5,2) , (10,1,2,5) , (10,1,5,2)
# (2,5,1,10) , (2,5,10,1) , (5,2,1,10) , (5,2,10,1)
# (2,10,4,5) , (2,10,5,4) , (10,2,4,5) , (10,2,5,4)
# (4,5,2,10) , (4,5,10,2) , (5,4,2,10) , (5,4,10,2)
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^4
#
# All elements in nums are distinct.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def tupleSameProduct(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count tuples (a,b,c,d) distinct with a*b == c*d. For each product of pairs,
        if f pairs share a product, they form C(f,2)*8 tuples (8 permutations).

        Algorithm:
        - Count products of all unordered pairs i<j; ans += 8 * C(freq,2) for each.

        Complexity: O(n^2) time, O(n^2) space.
        """
        n = len(nums)
        freq: Counter = Counter()
        for i in range(n):
            for j in range(i + 1, n):
                freq[nums[i] * nums[j]] += 1
        ans = 0
        for f in freq.values():
            ans += f * (f - 1) // 2 * 8
        return ans
# @lc code=end
