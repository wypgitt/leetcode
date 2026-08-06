#
# @lc app=leetcode id=2300 lang=python3
#
# [2300] Successful Pairs of Spells and Potions
#
# https://leetcode.com/problems/successful-pairs-of-spells-and-potions/description/
#
# algorithms
# Medium (49.78%)
# Likes:    3243
# Dislikes: 106
# Total Accepted:    398.5K
# Total Submissions: 800.6K
# Testcase Example:  "[5,1,3]\n[1,2,3,4,5]\n7"
#
# You are given two positive integer arrays spells and potions, of length n and
# m respectively, where spells[i] represents the strength of the i^th spell and
# potions[j] represents the strength of the j^th potion.
#
# You are also given an integer success. A spell and potion pair is considered
# successful if the product of their strengths is at least success.
#
# Return an integer array pairs of length n where pairs[i] is the number of
# potions that will form a successful pair with the i^th spell.
#
#
#
# Example 1:
#
# Input: spells = [5,1,3], potions = [1,2,3,4,5], success = 7
# Output: [4,0,3]
# Explanation:
# - 0^th spell: 5 * [1,2,3,4,5] = [5,10,15,20,25]. 4 pairs are successful.
# - 1^st spell: 1 * [1,2,3,4,5] = [1,2,3,4,5]. 0 pairs are successful.
# - 2^nd spell: 3 * [1,2,3,4,5] = [3,6,9,12,15]. 3 pairs are successful.
# Thus, [4,0,3] is returned.
#
# Example 2:
#
# Input: spells = [3,1,2], potions = [8,5,8], success = 16
# Output: [2,0,2]
# Explanation:
# - 0^th spell: 3 * [8,5,8] = [24,15,24]. 2 pairs are successful.
# - 1^st spell: 1 * [8,5,8] = [8,5,8]. 0 pairs are successful.
# - 2^nd spell: 2 * [8,5,8] = [16,10,16]. 2 pairs are successful.
# Thus, [2,0,2] is returned.
#
#
#
# Constraints:
#
#
# n == spells.length
#
#
# m == potions.length
#
#
# 1 <= n, m <= 10^5
#
#
# 1 <= spells[i], potions[i] <= 10^5
#
#
# 1 <= success <= 10^10
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def successfulPairs(self, spells: List[int], potions: List[int], success: int) -> List[int]:
        """
        Interview explanation:
        Pair (spell, potion) succeeds if product >= success. Count per spell.

        Algorithm:
        - Sort potions; for spell s need potion >= ceil(success/s); bisect.

        Complexity: O((n+m) log m) time, O(m) space.
        """
        potions.sort()
        m = len(potions)
        ans = []
        for s in spells:
            need = (success + s - 1) // s
            ans.append(m - bisect.bisect_left(potions, need))
        return ans


    def successfulPairs_two_pointers(self, spells: List[int], potions: List[int], success: int) -> List[int]:
        """
        Interview explanation:
        Two-pointers alternate: sort both; walk spells ascending, shrink potion pointer.

        Algorithm:
        - Sort indexed spells; potions ascending; j from right; accumulate counts.

        Complexity: O(n log n + m log m) time, O(n+m) space.
        """
        potions = sorted(potions)
        m = len(potions)
        order = sorted(range(len(spells)), key=lambda i: spells[i])
        ans = [0] * len(spells)
        j = m - 1
        for i in order:
            s = spells[i]
            while j >= 0 and s * potions[j] >= success:
                j -= 1
            ans[i] = m - j - 1
        return ans
# @lc code=end
