#
# @lc app=leetcode id=822 lang=python3
#
# [822] Card Flipping Game
#
# https://leetcode.com/problems/card-flipping-game/description/
#
# algorithms
# Medium (50.31%)
# Likes:    192
# Dislikes: 797
# Total Accepted:    26.6K
# Total Submissions: 52.8K
# Testcase Example:  '[1,2,4,4,7]\n[1,3,4,1,3]'
#
# You are given two 0-indexed integer arrays fronts and backs of length n,
# where the i^th card has the positive integer fronts[i] printed on the front
# and backs[i] printed on the back. Initially, each card is placed on a table
# such that the front number is facing up and the other is facing down. You may
# flip over any number of cards (possibly zero).
# 
# After flipping the cards, an integer is considered good if it is facing down
# on some card and not facing up on any card.
# 
# Return the minimum possible good integer after flipping the cards. If there
# are no good integers, return 0.
# 
# 
# Example 1:
# 
# 
# Input: fronts = [1,2,4,4,7], backs = [1,3,4,1,3]
# Output: 2
# Explanation:
# If we flip the second card, the face up numbers are [1,3,4,4,7] and the face
# down are [1,2,4,1,3].
# 2 is the minimum good integer as it appears facing down but not facing up.
# It can be shown that 2 is the minimum possible good integer obtainable after
# flipping some cards.
# 
# 
# Example 2:
# 
# 
# Input: fronts = [1], backs = [1]
# Output: 0
# Explanation:
# There are no good integers no matter how we flip the cards, so we return
# 0.
# 
# 
# 
# Constraints:
# 
# 
# n == fronts.length == backs.length
# 1 <= n <= 1000
# 1 <= fronts[i], backs[i] <= 2000
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def flipgame(self, fronts: List[int], backs: List[int]) -> int:
        banned = {f for f, b in zip(fronts, backs) if f == b}
        candidates = [x for x in fronts + backs if x not in banned]
        return min(candidates) if candidates else 0
# @lc code=end

"""
Interview explanation:
A number is impossible to hide from all fronts if it appears on both sides of the same card; no flip can remove it from the front of that card. Every other number appearing anywhere can be made visible on some front while avoiding banned numbers. So choose the smallest non-banned value from all sides.

Data structure: a set stores banned values for O(1) filtering.

Edge cases: if every candidate is banned, return 0. Equal front/back values on multiple cards are handled once by the set.

Complexity: O(n) time and O(n) space.
"""
