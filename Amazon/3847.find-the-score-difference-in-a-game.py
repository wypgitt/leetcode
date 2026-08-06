#
# @lc app=leetcode id=3847 lang=python3
#
# [3847] Find the Score Difference in a Game
#
# https://leetcode.com/problems/find-the-score-difference-in-a-game/description/
#
# algorithms
# Medium (72.61%)
# Likes:    47
# Dislikes: 4
# Total Accepted:    53.9K
# Total Submissions: 74.2K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums, where nums[i] represents the points
# scored in the i^th game.
#
# There are exactly two players. Initially, the first player is active and
# the second player is inactive.
#
# The following rules apply sequentially for each game i:
#
# If nums[i] is odd, the active and inactive players swap roles.
#
# In every 6th game (that is, game indices 5, 11, 17, ...), the active and
# inactive players swap roles.
#
# The active player plays the i^th game and gains nums[i] points.
#
# Return the score difference, defined as the first player's total score
# minus the second player's total score.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 0
#
# Explanation:​​​​​​​
#
# Game 0: Since the points are odd, the second player becomes active and
# gains nums[0] = 1 point.
#
# Game 1: No swap occurs. The second player gains nums[1] = 2 points.
#
# Game 2: Since the points are odd, the first player becomes active and
# gains nums[2] = 3 points.
#
# The score difference is 3 - 3 = 0.
#
# Example 2:
#
# Input: nums = [2,4,2,1,2,1]
#
# Output: 4
#
# Explanation:
#
# Games 0 to 2: The first player gains 2 + 4 + 2 = 8 points.
#
# Game 3: Since the points are odd, the second player is now active and
# gains nums[3] = 1 point.
#
# Game 4: The second player gains nums[4] = 2 points.
#
# Game 5: Since the points are odd, the players swap roles. Then, because
# this is the 6th game, the players swap again. The second player gains
# nums[5] = 1 point.
#
# The score difference is 8 - 4 = 4.
#
# Example 3:
#
# Input: nums = [1]
#
# Output: -1
#
# Explanation:
#
# Game 0: Since the points are odd, the second player is now active and
# gains nums[0] = 1 point.
#
# The score difference is 0 - 1 = -1.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def scoreDifference(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Two players alternate an active role. Before scoring game i: swap if
        points are odd; also swap on every 6th game (indices 5,11,...). Active
        player gains nums[i]. Return first - second score.

        Algorithm:
        - Track active index in {0,1}; apply both swap rules in order; add points.

        Complexity: O(n) time, O(1) space.
        """
        scores = [0, 0]
        active = 0
        for i, x in enumerate(nums):
            if x % 2:
                active ^= 1
            if i % 6 == 5:
                active ^= 1
            scores[active] += x
        return scores[0] - scores[1]
# @lc code=end
