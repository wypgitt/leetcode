#
# @lc app=leetcode id=2176 lang=python3
#
# [2176] Count Equal and Divisible Pairs in an Array
#
# https://leetcode.com/problems/count-equal-and-divisible-pairs-in-an-array/description/
#
# algorithms
# Easy (83.77%)
# Likes:    1050
# Dislikes: 69
# Total Accepted:    241.7K
# Total Submissions: 288.6K
# Testcase Example:  "[3,1,2,2,2,1,3]\n2"
#
# Given a 0-indexed integer array nums of length n and an integer k, return the
# number of pairs (i, j) where 0 <= i < j < n, such that nums[i] == nums[j] and
# (i * j) is divisible by k.
#
#
#
# Example 1:
#
# Input: nums = [3,1,2,2,2,1,3], k = 2
# Output: 4
# Explanation:
# There are 4 pairs that meet all the requirements:
# - nums[0] == nums[6], and 0 * 6 == 0, which is divisible by 2.
# - nums[2] == nums[3], and 2 * 3 == 6, which is divisible by 2.
# - nums[2] == nums[4], and 2 * 4 == 8, which is divisible by 2.
# - nums[3] == nums[4], and 3 * 4 == 12, which is divisible by 2.
#
# Example 2:
#
# Input: nums = [1,2,3,4], k = 1
# Output: 0
# Explanation: Since no value in nums is repeated, there are no pairs (i,j) that
# meet all the requirements.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 100
#
#
# 1 <= nums[i], k <= 100
#

# @lc code=start
from typing import List


class Solution:
    def countPairs(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count pairs (i,j) with i < j, nums[i] == nums[j], and (i * j) % k == 0.

        Algorithm:
        (brute for n<=100 / group by value)
        - Constraints usually small (n<=100): O(n^2) check equal values and index product.
        - Or group indices by value; for each group count pairs with (i*j)%k==0.

        Complexity: O(n^2) time fine for n<=100, O(1) extra.
        """
        n = len(nums)
        ans = 0
        for i in range(n):
            for j in range(i + 1, n):
                if nums[i] == nums[j] and (i * j) % k == 0:
                    ans += 1
        return ans
# @lc code=end
