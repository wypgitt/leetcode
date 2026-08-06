#
# @lc app=leetcode id=2212 lang=python3
#
# [2212] Maximum Points in an Archery Competition
#
# https://leetcode.com/problems/maximum-points-in-an-archery-competition/description/
#
# algorithms
# Medium (52.18%)
# Likes:    519
# Dislikes: 56
# Total Accepted:    20.9K
# Total Submissions: 40.1K
# Testcase Example:  "9\n[1,1,0,1,0,0,2,1,0,1,2,0]"
#
# Alice and Bob are opponents in an archery competition. The competition has set
# the following rules:
#
#
# Alice first shoots numArrows arrows and then Bob shoots numArrows arrows.
#
#
# The points are then calculated as follows:
#
#
#
# The target has integer scoring sections ranging from 0 to 11 inclusive.
#
#
# For each section of the target with score k (in between 0 to 11), say Alice
# and Bob have shot a_k and b_k arrows on that section respectively. If a_k >=
# b_k, then Alice takes k points. If a_k < b_k, then Bob takes k points.
#
#
# However, if a_k == b_k == 0, then nobody takes k points.
#
#
#
#
#
#
#
#
# For example, if Alice and Bob both shot 2 arrows on the section with score 11,
# then Alice takes 11 points. On the other hand, if Alice shot 0 arrows on the
# section with score 11 and Bob shot 2 arrows on that same section, then Bob
# takes 11 points.
#
#
#
# You are given the integer numArrows and an integer array aliceArrows of size
# 12, which represents the number of arrows Alice shot on each scoring section
# from 0 to 11. Now, Bob wants to maximize the total number of points he can
# obtain.
#
# Return the array bobArrows which represents the number of arrows Bob shot on
# each scoring section from 0 to 11. The sum of the values in bobArrows should
# equal numArrows.
#
# If there are multiple ways for Bob to earn the maximum total points, return
# any one of them.
#
#
#
# Example 1:
#
# Input: numArrows = 9, aliceArrows = [1,1,0,1,0,0,2,1,0,1,2,0]
# Output: [0,0,0,0,1,1,0,0,1,2,3,1]
# Explanation: The table above shows how the competition is scored.
# Bob earns a total point of 4 + 5 + 8 + 9 + 10 + 11 = 47.
# It can be shown that Bob cannot obtain a score higher than 47 points.
#
# Example 2:
#
# Input: numArrows = 3, aliceArrows = [0,0,1,0,0,0,0,0,0,0,0,2]
# Output: [0,0,0,0,0,0,0,0,1,1,1,0]
# Explanation: The table above shows how the competition is scored.
# Bob earns a total point of 8 + 9 + 10 = 27.
# It can be shown that Bob cannot obtain a score higher than 27 points.
#
#
#
# Constraints:
#
#
# 1 <= numArrows <= 10^5
#
#
# aliceArrows.length == bobArrows.length == 12
#
#
# 0 <= aliceArrows[i], bobArrows[i] <= numArrows
#
#
# sum(aliceArrows[i]) == numArrows
#

# @lc code=start
from typing import List


class Solution:
    def maximumBobPoints(self, numArrows: int, aliceArrows: List[int]) -> List[int]:
        """
        Interview explanation:
        12 sections; Bob scores k iff he shoots > aliceArrows[k] there. Distribute
        numArrows to maximize score; return any optimal arrow counts.

        Algorithm:
        - Enumerate 2^12 win-subsets; check arrow feasibility; track best score;
          put leftover arrows on section 0.

        Complexity: O(2^12 * 12) time, O(1) space.
        """
        best_score = -1
        best = [0] * 12
        for mask in range(1 << 12):
            need = [0] * 12
            used = score = 0
            ok = True
            for k in range(12):
                if mask >> k & 1:
                    need[k] = aliceArrows[k] + 1
                    used += need[k]
                    score += k
                    if used > numArrows:
                        ok = False
                        break
            if not ok:
                continue
            if score > best_score:
                best_score = score
                need[0] += numArrows - used
                best = need[:]
        return best
# @lc code=end
