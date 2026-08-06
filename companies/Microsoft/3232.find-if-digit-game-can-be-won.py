#
# @lc app=leetcode id=3232 lang=python3
#
# [3232] Find if Digit Game Can Be Won
#
# https://leetcode.com/problems/find-if-digit-game-can-be-won/description/
#
# algorithms
# Easy (81.72%)
# Likes:    215
# Dislikes: 14
# Total Accepted:    123.3K
# Total Submissions: 150.8K
# Testcase Example:  "[1,2,3,4,10]"
#
#
# You are given an array of positive integers nums.
#
# Alice and Bob are playing a game. In the game, Alice can choose either
# all single-digit numbers or all double-digit numbers from nums, and the
# rest of the numbers are given to Bob. Alice wins if the sum of her
# numbers is strictly greater than the sum of Bob's numbers.
#
# Return true if Alice can win this game, otherwise, return false.
#
# Example 1:
#
# Input: nums = [1,2,3,4,10]
#
# Output: false
#
# Explanation:
#
# Alice cannot win by choosing either single-digit or double-digit
# numbers.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5,14]
#
# Output: true
#
# Explanation:
#
# Alice can win by choosing single-digit numbers which have a sum equal to
# 15.
#
# Example 3:
#
# Input: nums = [5,5,5,25]
#
# Output: true
#
# Explanation:
#
# Alice can win by choosing double-digit numbers which have a sum equal to
# 25.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 99
#

# @lc code=start
from typing import List


class Solution:
    def canAliceWin(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alice picks either all single-digit or all double-digit numbers and needs
        a strictly larger sum than Bob's complement.

        Algorithm:
        - single = sum of nums[i] < 10; double = total - single.
        - Alice wins iff single != double.

        Complexity: O(n) time, O(1) space.
        Alternate: compare single vs double explicitly with two sums.
        """
        single = sum(x for x in nums if x < 10)
        double = sum(nums) - single
        return single != double

# @lc code=end
