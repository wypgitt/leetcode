#
# @lc app=leetcode id=1996 lang=python3
#
# [1996] The Number of Weak Characters in the Game
#
# https://leetcode.com/problems/the-number-of-weak-characters-in-the-game/description/
#
# algorithms
# Medium (44.63%)
# Likes:    3117
# Dislikes: 100
# Total Accepted:    120K
# Total Submissions: 270K
# Testcase Example:  "[[5,5],[6,3],[3,6]]"
#
# You are playing a game that contains multiple characters, and each of the
# characters has two main properties: attack and defense. You are given a 2D
# integer array properties where properties[i] = [attack_i, defense_i]
# represents the properties of the i^th character in the game.
#
# A character is said to be weak if any other character has both attack and
# defense levels strictly greater than this character's attack and defense
# levels. More formally, a character i is said to be weak if there exists
# another character j where attack_j > attack_i and defense_j > defense_i.
#
# Return the number of weak characters.
#
# Example 1:
#
# Input: properties = [[5,5],[6,3],[3,6]]
# Output: 0
# Explanation: No character has strictly greater attack and defense than the
# other.
#
# Example 2:
#
# Input: properties = [[2,2],[3,3]]
# Output: 1
# Explanation: The first character is weak because the second character has a
# strictly greater attack and defense.
#
# Example 3:
#
# Input: properties = [[1,5],[10,4],[4,3]]
# Output: 1
# Explanation: The third character is weak because the second character has a
# strictly greater attack and defense.
#
# Constraints:
#
# 2 <= properties.length <= 10^5
#
# properties[i].length == 2
#
# 1 <= attack_i, defense_i <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def numberOfWeakCharacters(self, properties: List[List[int]]) -> int:
        """
        Interview explanation:
        Weak if some other has both strictly greater attack and defense.
        Sort by attack descending, defense ascending; scan max defense seen.

        Algorithm:
        - Sort key=(-attack, defense); track max_def; if cur_def < max_def: weak++
          else update max_def.

        Complexity: O(n log n) time, O(n) space.
        """
        properties.sort(key=lambda x: (-x[0], x[1]))
        ans = 0
        max_def = 0
        for _, d in properties:
            if d < max_def:
                ans += 1
            else:
                max_def = d
        return ans

    def numberOfWeakCharacters_group(self, properties: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: sort attack ascending; from right keep max defense of
        strictly larger attacks.

        Algorithm:
        - Sort by attack asc, defense desc; scan left; compare to running max_def
          from processed higher attacks (process groups carefully).
        - Simpler equivalent: sort (-attack, defense) as primary.

        Complexity: O(n log n) time, O(n) space.
        """
        properties.sort()
        # process from highest attack
        ans = 0
        max_def = 0
        i = len(properties) - 1
        while i >= 0:
            # collect same attack group
            j = i
            cur_max = 0
            attack = properties[i][0]
            while j >= 0 and properties[j][0] == attack:
                if properties[j][1] < max_def:
                    ans += 1
                cur_max = max(cur_max, properties[j][1])
                j -= 1
            max_def = max(max_def, cur_max)
            i = j
        return ans
# @lc code=end

