#
# @lc app=leetcode id=2558 lang=python3
#
# [2558] Take Gifts From the Richest Pile
#
# https://leetcode.com/problems/take-gifts-from-the-richest-pile/description/
#
# algorithms
# Easy (75.45%)
# Likes:    868
# Dislikes: 83
# Total Accepted:    205.8K
# Total Submissions: 272.8K
# Testcase Example:  "[25,64,9,4,100]\n4"
#
# You are given an integer array gifts denoting the number of gifts in various
# piles. Every second, you do the following:
#
#
# Choose the pile with the maximum number of gifts.
#
#
# If there is more than one pile with the maximum number of gifts, choose any.
#
#
# Reduce the number of gifts in the pile to the floor of the square root of the
# original number of gifts in the pile.
#
# Return the number of gifts remaining after k seconds.
#
#
#
# Example 1:
#
# Input: gifts = [25,64,9,4,100], k = 4
# Output: 29
# Explanation:
# The gifts are taken in the following way:
# - In the first second, the last pile is chosen and 10 gifts are left behind.
# - Then the second pile is chosen and 8 gifts are left behind.
# - After that the first pile is chosen and 5 gifts are left behind.
# - Finally, the last pile is chosen again and 3 gifts are left behind.
# The final remaining gifts are [5,8,9,4,3], so the total number of gifts
# remaining is 29.
#
# Example 2:
#
# Input: gifts = [1,1,1,1], k = 4
# Output: 4
# Explanation:
# In this case, regardless which pile you choose, you have to leave behind 1
# gift in each pile.
# That is, you can't take any pile with you.
# So, the total gifts remaining are 4.
#
#
#
# Constraints:
#
#
# 1 <= gifts.length <= 10^3
#
#
# 1 <= gifts[i] <= 10^9
#
#
# 1 <= k <= 10^3
#

# @lc code=start
from typing import List
import heapq
import math


class Solution:
    def pickGifts(self, gifts: List[int], k: int) -> int:
        """
        Interview explanation:
        For k seconds, always take the richest pile and leave floor(sqrt(gifts)).

        Algorithm:
        - Max-heap of piles; k times pop max, push floor(sqrt).

        Complexity: O((n+k) log n) time, O(n) space.
        """
        h = [-g for g in gifts]
        heapq.heapify(h)
        for _ in range(k):
            g = -heapq.heappop(h)
            heapq.heappush(h, -int(math.isqrt(g)))
        return -sum(h)
# @lc code=end
