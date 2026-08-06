#
# @lc app=leetcode id=781 lang=python3
#
# [781] Rabbits in Forest
#
# https://leetcode.com/problems/rabbits-in-forest/description/
#
# algorithms
# Medium (58.03%)
# Likes:    2180
# Dislikes: 996
# Total Accepted:    193K
# Total Submissions: 332K
# Testcase Example:  "[1,1,2]"
#
# There is a forest with an unknown number of rabbits. We asked n rabbits "How
# many other rabbits have the same color as you?" and collected the answers in
# an integer array answers where answers[i] is the answer of the i^th rabbit.
#
# Given the array answers, return the minimum number of rabbits that could be
# in the forest.
#
# Example 1:
#
# Input: answers = [1,1,2]
# Output: 5
# Explanation:
# The two rabbits that answered "1" could both be the same color, say red.
# The rabbit that answered "2" can't be red or the answers would be
# inconsistent.
# Say the rabbit that answered "2" was blue.
# Then there should be 2 other blue rabbits in the forest that didn't answer
# into the array.
# The smallest possible number of rabbits in the forest is therefore 5: 3 that
# answered plus 2 that didn't.
#
# Example 2:
#
# Input: answers = [10,10,10]
# Output: 11
#
# Constraints:
#
# 1 <= answers.length <= 1000
#
# 0 <= answers[i] < 1000
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def numRabbits(self, answers: List[int]) -> int:
        """
        Interview explanation:
        If a rabbit answers x, its color group has size x+1. Rabbits with the
        same answer can share groups of size x+1; for count c of answer x,
        need ceil(c / (x+1)) groups, each of size x+1.

        Algorithm:
        - Counter answers.
        - For each x, c: groups = ceil(c / (x+1)); ans += groups * (x+1)

        Complexity: O(n) time, O(n) space.
        """
        ans = 0
        for x, c in Counter(answers).items():
            size = x + 1
            groups = (c + size - 1) // size
            ans += groups * size
        return ans
# @lc code=end

