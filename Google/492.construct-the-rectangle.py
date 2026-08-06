#
# @lc app=leetcode id=492 lang=python3
#
# [492] Construct the Rectangle
#
# https://leetcode.com/problems/construct-the-rectangle/description/
#
# algorithms
# Easy (64.71%)
# Likes:    808
# Dislikes: 394
# Total Accepted:    184K
# Total Submissions: 284K
# Testcase Example:  "4"
#
# A web developer needs to know how to design a web page's size. So, given a
# specific rectangular web page’s area, your job by now is to design a
# rectangular web page, whose length L and width W satisfy the following
# requirements:
#
# The area of the rectangular web page you designed must equal to the given
# target area.
#
# The width W should not be larger than the length L, which means L >= W.
#
# The difference between length L and width W should be as small as possible.
#
# Return an array [L, W] where L and W are the length and width of the web page
# you designed in sequence.
#
# Example 1:
#
# Input: area = 4
# Output: [2,2]
# Explanation: The target area is 4, and all the possible ways to construct it
# are [1,4], [2,2], [4,1].
# But according to requirement 2, [1,4] is illegal; according to requirement 3,
# [4,1] is not optimal compared to [2,2]. So the length L is 2, and the width W
# is 2.
#
# Example 2:
#
# Input: area = 37
# Output: [37,1]
#
# Example 3:
#
# Input: area = 122122
# Output: [427,286]
#
# Constraints:
#
# 1 <= area <= 10^7
#

# @lc code=start
from math import isqrt
from typing import List


class Solution:
    def constructRectangle(self, area: int) -> List[int]:
        """
        Interview explanation:
        Find L, W with L*W = area, L >= W, minimize L-W. Optimal W is the
        largest divisor ≤ sqrt(area); then L = area // W.

        Algorithm:
        - w = isqrt(area); while area % w: w -= 1; return [area//w, w].

        Complexity: O(sqrt(area)) time, O(1) space.
        """
        w = isqrt(area)
        while area % w:
            w -= 1
        return [area // w, w]
# @lc code=end
