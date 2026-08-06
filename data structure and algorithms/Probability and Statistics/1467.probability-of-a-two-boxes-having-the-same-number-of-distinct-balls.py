#
# @lc app=leetcode id=1467 lang=python3
#
# [1467] Probability of a Two Boxes Having The Same Number of Distinct Balls
#
# https://leetcode.com/problems/probability-of-a-two-boxes-having-the-same-number-of-distinct-balls/description/
#
# algorithms
# Hard (61.51%)
# Likes:    300
# Dislikes: 178
# Total Accepted:    12.4K
# Total Submissions: 20.2K
# Testcase Example:  "[1,1]"
#
# Given 2n balls of k distinct colors. You will be given an integer array balls
# of size k where balls[i] is the number of balls of color i.
#
# All the balls will be shuffled uniformly at random, then we will distribute
# the first n balls to the first box and the remaining n balls to the other box
# (Please read the explanation of the second example carefully).
#
# Please note that the two boxes are considered different. For example, if we
# have two balls of colors a and b, and two boxes [] and (), then the
# distribution [a] (b) is considered different than the distribution [b] (a)
# (Please read the explanation of the first example carefully).
#
# Return the probability that the two boxes have the same number of distinct
# balls. Answers within 10^-5 of the actual value will be accepted as correct.
#
# Example 1:
#
# Input: balls = [1,1]
# Output: 1.00000
# Explanation: Only 2 ways to divide the balls equally:
# - A ball of color 1 to box 1 and a ball of color 2 to box 2
# - A ball of color 2 to box 1 and a ball of color 1 to box 2
# In both ways, the number of distinct colors in each box is equal. The
# probability is 2/2 = 1
#
# Example 2:
#
# Input: balls = [2,1,1]
# Output: 0.66667
# Explanation: We have the set of balls [1, 1, 2, 3]
# This set of balls will be shuffled randomly and we may have one of the 12
# distinct shuffles with equal probability (i.e. 1/12):
# [1,1 / 2,3], [1,1 / 3,2], [1,2 / 1,3], [1,2 / 3,1], [1,3 / 1,2], [1,3 / 2,1],
# [2,1 / 1,3], [2,1 / 3,1], [2,3 / 1,1], [3,1 / 1,2], [3,1 / 2,1], [3,2 / 1,1]
# After that, we add the first two balls to the first box and the second two
# balls to the second box.
# We can see that 8 of these 12 possible random distributions have the same
# number of distinct colors of balls in each box.
# Probability is 8/12 = 0.66667
#
# Example 3:
#
# Input: balls = [1,2,1,2]
# Output: 0.60000
# Explanation: The set of balls is [1, 2, 2, 3, 4, 4]. It is hard to display
# all the 180 possible random shuffles of this set but it is easy to check that
# 108 of them will have the same number of distinct colors in each box.
# Probability = 108 / 180 = 0.6
#
# Constraints:
#
# 1 <= balls.length <= 8
#
# 1 <= balls[i] <= 6
#
# sum(balls) is even.
#

# @lc code=start
from typing import List
from math import comb


class Solution:
    def getProbability(self, balls: List[int]) -> float:
        """
        Interview explanation:
        Distribute balls of each color into two boxes with equal total balls;
        probability both boxes have the same number of distinct colors.
        Enumerate distributions via DFS/backtracking; weight by multinomial
        coefficients.

        Algorithm:
        - total = sum(balls)//2; DFS over colors choosing k for box1 (0..cnt);
          track remaining slots and distinct counts; accumulate favorable / total ways.

        Complexity: exponential in #colors (small, ≤8); O(#colors) stack space.
        """
        n = len(balls)
        half = sum(balls) // 2
        total_ways = 0
        good = 0

        def go(i, rem, dist1, dist2, ways):
            nonlocal total_ways, good
            if rem < 0:
                return
            if i == n:
                if rem == 0:
                    total_ways += ways
                    if dist1 == dist2:
                        good += ways
                return
            c = balls[i]
            for take in range(c + 1):
                if take > rem:
                    break
                nd1 = dist1 + (1 if take > 0 else 0)
                nd2 = dist2 + (1 if c - take > 0 else 0)
                go(i + 1, rem - take, nd1, nd2, ways * comb(c, take))

        go(0, half, 0, 0, 1)
        return good / total_ways if total_ways else 0.0
# @lc code=end
