#
# @lc app=leetcode id=605 lang=python3
#
# [605] Can Place Flowers
#
# https://leetcode.com/problems/can-place-flowers/description/
#
# algorithms
# Easy (29.26%)
# Likes:    7492
# Dislikes: 1333
# Total Accepted:    1.5M
# Total Submissions: 5.0M
# Testcase Example:  "[1,0,0,0,1]"
#
# You have a long flowerbed in which some of the plots are planted, and some
# are not. However, flowers cannot be planted in adjacent plots.
#
# Given an integer array flowerbed containing 0's and 1's, where 0 means empty
# and 1 means not empty, and an integer n, return true if n new flowers can be
# planted in the flowerbed without violating the no-adjacent-flowers rule and
# false otherwise.
#
# Example 1:
#
# Input: flowerbed = [1,0,0,0,1], n = 1
# Output: true
#
# Example 2:
#
# Input: flowerbed = [1,0,0,0,1], n = 2
# Output: false
#
# Constraints:
#
# 1 <= flowerbed.length <= 2 * 10^4
#
# flowerbed[i] is 0 or 1.
#
# There are no two adjacent flowers in flowerbed.
#
# 0 <= n <= flowerbed.length
#

# @lc code=start

from typing import List


class Solution:
    def canPlaceFlowers(self, flowerbed: List[int], n: int) -> bool:
        """
        Interview explanation:
        Greedily plant a flower in every empty plot whose neighbors are empty
        (treat ends as bordered by empty). Count how many we can place.

        Algorithm:
        - Scan left to right; at index i if flowerbed[i]==0 and neighbors empty,
          plant (set 1) and decrement n.
        - Early return True if n reaches 0.

        Complexity: O(N) time, O(1) extra space.
        """
        if n <= 0:
            return True
        bed = flowerbed
        m = len(bed)
        for i in range(m):
            if bed[i] == 0 and (i == 0 or bed[i - 1] == 0) and (i == m - 1 or bed[i + 1] == 0):
                bed[i] = 1
                n -= 1
                if n == 0:
                    return True
        return n <= 0
# @lc code=end
