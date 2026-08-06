#
# @lc app=leetcode id=1402 lang=python3
#
# [1402] Reducing Dishes
#
# https://leetcode.com/problems/reducing-dishes/description/
#
# algorithms
# Hard (76.8%)
# Likes:    3546
# Dislikes: 321
# Total Accepted:    192K
# Total Submissions: 249K
# Testcase Example:  "[-1,-8,0,5,-7]"
#
# A chef has collected data on the satisfaction level of his n dishes. Chef can
# cook any dish in 1 unit of time.
#
# Like-time coefficient of a dish is defined as the time taken to cook that
# dish including previous dishes multiplied by its satisfaction level i.e.
# time[i] * satisfaction[i].
#
# Return the maximum sum of like-time coefficient that the chef can obtain
# after preparing some amount of dishes.
#
# Dishes can be prepared in any order and the chef can discard some dishes to
# get this maximum value.
#
# Example 1:
#
# Input: satisfaction = [-1,-8,0,5,-9]
# Output: 14
# Explanation: After Removing the second and last dish, the maximum total
# like-time coefficient will be equal to (-1*1 + 0*2 + 5*3 = 14).
# Each dish is prepared in one unit of time.
#
# Example 2:
#
# Input: satisfaction = [4,3,2]
# Output: 20
# Explanation: Dishes can be prepared in any order, (2*1 + 3*2 + 4*3 = 20)
#
# Example 3:
#
# Input: satisfaction = [-1,-4,-5]
# Output: 0
# Explanation: People do not like the dishes. No dish is prepared.
#
# Constraints:
#
# n == satisfaction.length
#
# 1 <= n <= 500
#
# -1000 <= satisfaction[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def maxSatisfaction(self, satisfaction: List[int]) -> int:
        """
        Interview explanation:
        Cooking order multiplies satisfaction by time. Optimal: cook highest
        satisfaction last. Sort descending; greedily add dishes while running
        suffix sum stays positive (each new dish adds its value to every prior
        time multiplier contribution).

        Algorithm:
        (greedy sort)
        - Sort desc; ans=0, prefix=0; for v in arr: prefix+=v; if prefix>0: ans+=prefix else break
        - Return ans

        Complexity: O(n log n) time, O(1)/O(n) space depending on sort.
        """
        satisfaction.sort(reverse=True)
        ans = prefix = 0
        for v in satisfaction:
            prefix += v
            if prefix <= 0:
                break
            ans += prefix
        return ans

    def maxSatisfaction_dp(self, satisfaction: List[int]) -> int:
        """
        Interview explanation:
        Alternate DP: sort ascending; dp[j] = max like-time after cooking j dishes
        as a suffix of the sorted array (or iterate dishes and update knapsack-style).

        Algorithm:
        - Sort asc; dp[0]=0; for each dish update dp from high count down.
        - Track max over all dp values.

        Complexity: O(n^2) time, O(n) space.
        """
        satisfaction.sort()
        n = len(satisfaction)
        # dp[t] = max sum with time coefficients using some subset cooked in order
        # Use: after sorting, choosing a contiguous suffix is optimal.
        best = 0
        for i in range(n):
            cur = 0
            t = 1
            for j in range(i, n):
                cur += satisfaction[j] * t
                t += 1
            best = max(best, cur)
        return best
# @lc code=end
