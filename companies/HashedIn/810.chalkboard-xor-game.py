#
# @lc app=leetcode id=810 lang=python3
#
# [810] Chalkboard XOR Game
#
# https://leetcode.com/problems/chalkboard-xor-game/description/
#
# algorithms
# Hard (66.78%)
# Likes:    255
# Dislikes: 288
# Total Accepted:    21.1K
# Total Submissions: 31.7K
# Testcase Example:  "[1,1,2]"
#
# You are given an array of integers nums represents the numbers written on a
# chalkboard.
#
# Alice and Bob take turns erasing exactly one number from the chalkboard, with
# Alice starting first. If erasing a number causes the bitwise XOR of all the
# elements of the chalkboard to become 0, then that player loses. The bitwise
# XOR of one element is that element itself, and the bitwise XOR of no elements
# is 0.
#
# Also, if any player starts their turn with the bitwise XOR of all the
# elements of the chalkboard equal to 0, then that player wins.
#
# Return true if and only if Alice wins the game, assuming both players play
# optimally.
#
# Example 1:
#
# Input: nums = [1,1,2]
# Output: false
# Explanation:
# Alice has two choices: erase 1 or erase 2.
# If she erases 1, the nums array becomes [1, 2]. The bitwise XOR of all the
# elements of the chalkboard is 1 XOR 2 = 3. Now Bob can remove any element he
# wants, because Alice will be the one to erase the last element and she will
# lose.
# If Alice erases 2 first, now nums become [1, 1]. The bitwise XOR of all the
# elements of the chalkboard is 1 XOR 1 = 0. Alice will lose.
#
# Example 2:
#
# Input: nums = [0,1]
# Output: true
#
# Example 3:
#
# Input: nums = [1,2,3]
# Output: true
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 0 <= nums[i] < 2^16
#

# @lc code=start

from typing import List
from functools import reduce
import operator


class Solution:
    def xorGame(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Players erase a number so the XOR of remaining numbers ≠ 0. A player
        loses when every erase would make XOR 0 (equivalently current XOR is 0).
        Classic result: first player wins iff total XOR ≠ 0 or n is even
        (pairing argument / math on XOR).

        Algorithm:
        - Let x = XOR of all nums. Return x == 0 is False for first if n odd
          wait: return True if x == 0 is false OR len even → x!=0 or n%2==0.

        Complexity: O(n) time, O(1) space.
        """
        x = 0
        for v in nums:
            x ^= v
        return x == 0 or len(nums) % 2 == 0

    def xorGame_reduce(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Same math theorem using functools.reduce for the aggregate XOR.

        Algorithm:
        - x = reduce(xor, nums, 0); return x==0 or n even.

        Complexity: O(n) time, O(1) space.
        """
        x = reduce(operator.xor, nums, 0)
        return x == 0 or len(nums) % 2 == 0
# @lc code=end
