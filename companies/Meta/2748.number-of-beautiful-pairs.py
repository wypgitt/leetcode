#
# @lc app=leetcode id=2748 lang=python3
#
# [2748] Number of Beautiful Pairs
#
# https://leetcode.com/problems/number-of-beautiful-pairs/description/
#
# algorithms
# Easy (52.84%)
# Likes:    249
# Dislikes: 43
# Total Accepted:    49.9K
# Total Submissions: 94.5K
# Testcase Example:  "[2,5,1,4]"
#
# You are given a 0-indexed integer array nums. A pair of indices i, j where 0
# <= i < j < nums.length is called beautiful if the first digit of nums[i] and
# the last digit of nums[j] are coprime.
#
# Return the total number of beautiful pairs in nums.
#
# Two integers x and y are coprime if there is no integer greater than 1 that
# divides both of them. In other words, x and y are coprime if gcd(x, y) == 1,
# where gcd(x, y) is the greatest common divisor of x and y.
#
#
#
# Example 1:
#
# Input: nums = [2,5,1,4]
# Output: 5
# Explanation: There are 5 beautiful pairs in nums:
# When i = 0 and j = 1: the first digit of nums[0] is 2, and the last digit of
# nums[1] is 5. We can confirm that 2 and 5 are coprime, since gcd(2,5) == 1.
# When i = 0 and j = 2: the first digit of nums[0] is 2, and the last digit of
# nums[2] is 1. Indeed, gcd(2,1) == 1.
# When i = 1 and j = 2: the first digit of nums[1] is 5, and the last digit of
# nums[2] is 1. Indeed, gcd(5,1) == 1.
# When i = 1 and j = 3: the first digit of nums[1] is 5, and the last digit of
# nums[3] is 4. Indeed, gcd(5,4) == 1.
# When i = 2 and j = 3: the first digit of nums[2] is 1, and the last digit of
# nums[3] is 4. Indeed, gcd(1,4) == 1.
# Thus, we return 5.
#
# Example 2:
#
# Input: nums = [11,21,12]
# Output: 2
# Explanation: There are 2 beautiful pairs:
# When i = 0 and j = 1: the first digit of nums[0] is 1, and the last digit of
# nums[1] is 1. Indeed, gcd(1,1) == 1.
# When i = 0 and j = 2: the first digit of nums[0] is 1, and the last digit of
# nums[2] is 2. Indeed, gcd(1,2) == 1.
# Thus, we return 2.
#
#
#
# Constraints:
#
#
# 2 <= nums.length <= 100
#
#
# 1 <= nums[i] <= 9999
#
#
# nums[i] % 10 != 0
#

# @lc code=start
from math import gcd
from typing import List


class Solution:
    def countBeautifulPairs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count pairs i<j where gcd(first digit of nums[i], last digit of nums[j]) == 1.

        Algorithm:
        - Maintain counts of first digits seen; for each new number use its last digit
          against prior first-digit counts.

        Complexity: O(n * 10) time, O(1) space.
        """
        cnt = [0] * 10
        ans = 0
        for x in nums:
            last = x % 10
            for d in range(1, 10):
                if cnt[d] and gcd(d, last) == 1:
                    ans += cnt[d]
            first = x
            while first >= 10:
                first //= 10
            cnt[first] += 1
        return ans
# @lc code=end
