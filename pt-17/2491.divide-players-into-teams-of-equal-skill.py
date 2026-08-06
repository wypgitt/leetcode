#
# @lc app=leetcode id=2491 lang=python3
#
# [2491] Divide Players Into Teams of Equal Skill
#
# https://leetcode.com/problems/divide-players-into-teams-of-equal-skill/description/
#
# algorithms
# Medium (68.92%)
# Likes:    1091
# Dislikes: 36
# Total Accepted:    207.2K
# Total Submissions: 300.6K
# Testcase Example:  "[3,2,5,1,3,4]"
#
# You are given a positive integer array skill of even length n where skill[i]
# denotes the skill of the i^th player. Divide the players into n / 2 teams of
# size 2 such that the total skill of each team is equal.
#
# The chemistry of a team is equal to the product of the skills of the players
# on that team.
#
# Return the sum of the chemistry of all the teams, or return -1 if there is no
# way to divide the players into teams such that the total skill of each team is
# equal.
#
#
#
# Example 1:
#
# Input: skill = [3,2,5,1,3,4]
# Output: 22
# Explanation:
# Divide the players into the following teams: (1, 5), (2, 4), (3, 3), where
# each team has a total skill of 6.
# The sum of the chemistry of all the teams is: 1 * 5 + 2 * 4 + 3 * 3 = 5 + 8 +
# 9 = 22.
#
# Example 2:
#
# Input: skill = [3,4]
# Output: 12
# Explanation:
# The two players form a team with a total skill of 7.
# The chemistry of the team is 3 * 4 = 12.
#
# Example 3:
#
# Input: skill = [1,1,2,3]
# Output: -1
# Explanation:
# There is no way to divide the players into teams such that the total skill of
# each team is equal.
#
#
#
# Constraints:
#
#
# 2 <= skill.length <= 10^5
#
#
# skill.length is even.
#
#
# 1 <= skill[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def dividePlayers(self, skill: List[int]) -> int:
        """
        Interview explanation:
        Pair into n/2 teams with equal skill sum; return total chemistry
        (product per team) or -1.

        Algorithm:
        - Sort; target = min+max; pair ends; accumulate products.

        Complexity: O(n log n) time, O(n) space.
        """
        a = sorted(skill)
        i, j = 0, len(a) - 1
        target = a[i] + a[j]
        chem = 0
        while i < j:
            if a[i] + a[j] != target:
                return -1
            chem += a[i] * a[j]
            i += 1
            j -= 1
        return chem

    def dividePlayers_two_pointers(self, skill: List[int]) -> int:
        """
        Interview explanation:
        Alternate frequency map: each value pairs with target-value.

        Algorithm:
        - Count frequencies; for each x, need matching target-x.

        Complexity: O(n) time, O(n) space.
        """
        from collections import Counter

        total = sum(skill)
        teams = len(skill) // 2
        if total % teams:
            return -1
        target = total // teams
        cnt = Counter(skill)
        chem = 0
        for x, c in list(cnt.items()):
            y = target - x
            if x == y:
                if c % 2:
                    return -1
                chem += (c // 2) * x * x
                cnt[x] = 0
            else:
                if cnt[y] != c:
                    return -1
                chem += c * x * y
                cnt[x] = cnt[y] = 0
        return chem
# @lc code=end

