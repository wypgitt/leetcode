#
# @lc app=leetcode id=2001 lang=python3
#
# [2001] Number of Pairs of Interchangeable Rectangles
#
# https://leetcode.com/problems/number-of-pairs-of-interchangeable-rectangles/description/
#
# algorithms
# Medium (52.92%)
# Likes:    587
# Dislikes: 49
# Total Accepted:    62.7K
# Total Submissions: 118.6K
# Testcase Example:  "[[4,8],[3,6],[10,20],[15,30]]"
#
# You are given n rectangles represented by a 0-indexed 2D integer array
# rectangles, where rectangles[i] = [width_i, height_i] denotes the width and
# height of the i^th rectangle.
#
# Two rectangles i and j (i < j) are considered interchangeable if they have the
# same width-to-height ratio. More formally, two rectangles are interchangeable
# if width_i/height_i == width_j/height_j (using decimal division, not integer
# division).
#
# Return the number of pairs of interchangeable rectangles in rectangles.
#
#
#
# Example 1:
#
# Input: rectangles = [[4,8],[3,6],[10,20],[15,30]]
# Output: 6
# Explanation: The following are the interchangeable pairs of rectangles by
# index (0-indexed):
# - Rectangle 0 with rectangle 1: 4/8 == 3/6.
# - Rectangle 0 with rectangle 2: 4/8 == 10/20.
# - Rectangle 0 with rectangle 3: 4/8 == 15/30.
# - Rectangle 1 with rectangle 2: 3/6 == 10/20.
# - Rectangle 1 with rectangle 3: 3/6 == 15/30.
# - Rectangle 2 with rectangle 3: 10/20 == 15/30.
#
# Example 2:
#
# Input: rectangles = [[4,5],[7,8]]
# Output: 0
# Explanation: There are no interchangeable pairs of rectangles.
#
#
#
# Constraints:
#
#
# n == rectangles.length
#
#
# 1 <= n <= 10^5
#
#
# rectangles[i].length == 2
#
#
# 1 <= width_i, height_i <= 10^5
#

# @lc code=start
from typing import List
from collections import Counter
from math import gcd


class Solution:
    def interchangeableRectangles(self, rectangles: List[List[int]]) -> int:
        """
        Interview explanation:
        Two rectangles are interchangeable if they share the same width/height
        ratio. Count pairs among rectangles with equal reduced ratios.

        Algorithm:
        - For each [w,h], reduce by gcd and count frequency of (w/g, h/g).
        - For each count c, add C(c,2) = c*(c-1)//2.

        Complexity: O(n) time, O(n) space.
        """
        freq = Counter()
        for w, h in rectangles:
            g = gcd(w, h)
            freq[(w // g, h // g)] += 1
        return sum(c * (c - 1) // 2 for c in freq.values())
# @lc code=end
