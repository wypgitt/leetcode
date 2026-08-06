#
# @lc app=leetcode id=506 lang=python3
#
# [506] Relative Ranks
#
# https://leetcode.com/problems/relative-ranks/description/
#
# algorithms
# Easy (75.03%)
# Likes:    2210
# Dislikes: 153
# Total Accepted:    435K
# Total Submissions: 580K
# Testcase Example:  "[5,4,3,2,1]"
#
# You are given an integer array score of size n, where score[i] is the score
# of the i^th athlete in a competition. All the scores are guaranteed to be
# unique.
#
# The athletes are placed based on their scores, where the 1^st place athlete
# has the highest score, the 2^nd place athlete has the 2^nd highest score, and
# so on. The placement of each athlete determines their rank:
#
# The 1^st place athlete's rank is "Gold Medal".
#
# The 2^nd place athlete's rank is "Silver Medal".
#
# The 3^rd place athlete's rank is "Bronze Medal".
#
# For the 4^th place to the n^th place athlete, their rank is their placement
# number (i.e., the x^th place athlete's rank is "x").
#
# Return an array answer of size n where answer[i] is the rank of the i^th
# athlete.
#
# Example 1:
#
# Input: score = [5,4,3,2,1]
# Output: ["Gold Medal","Silver Medal","Bronze Medal","4","5"]
# Explanation: The placements are [1^st, 2^nd, 3^rd, 4^th, 5^th].
#
# Example 2:
#
# Input: score = [10,3,8,9,4]
# Output: ["Gold Medal","5","Bronze Medal","Silver Medal","4"]
# Explanation: The placements are [1^st, 5^th, 3^rd, 2^nd, 4^th].
#
# Constraints:
#
# n == score.length
#
# 1 <= n <= 10^4
#
# 0 <= score[i] <= 10^6
#
# All the values in score are unique.
#

# @lc code=start
from typing import List


class Solution:
    def findRelativeRanks(self, score: List[int]) -> List[str]:
        """
        Interview explanation:
        Rank athletes by score descending: 1st/2nd/3rd get medals, others get
        rank number as string. Sort indices by score; assign labels.

        Algorithm:
        - idx = sorted(range(n), key=lambda i: -score[i])
        - medals = ["Gold Medal","Silver Medal","Bronze Medal"]
        - Place labels into ans at original indices.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(score)
        order = sorted(range(n), key=lambda i: -score[i])
        ans = [""] * n
        medals = ["Gold Medal", "Silver Medal", "Bronze Medal"]
        for rank, i in enumerate(order):
            if rank < 3:
                ans[i] = medals[rank]
            else:
                ans[i] = str(rank + 1)
        return ans
# @lc code=end
