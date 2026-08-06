#
# @lc app=leetcode id=2954 lang=python3
#
# [2954] Count the Number of Infection Sequences
#
# https://leetcode.com/problems/count-the-number-of-infection-sequences/description/
#
# algorithms
# Hard (38.27%)
# Likes:    156
# Dislikes: 33
# Total Accepted:    6.8K
# Total Submissions: 17.9K
# Testcase Example:  "5\n[0,4]"
#
#
# You are given an integer n and an array sick sorted in increasing order,
# representing positions of infected people in a line of n people.
#
# At each step, one uninfected person adjacent to an infected person gets
# infected. This process continues until everyone is infected.
#
# An infection sequence is the order in which uninfected people become
# infected, excluding those initially infected.
#
# Return the number of different infection sequences possible, modulo
# 10^9+7.
#
# Example 1:
#
# Input: n = 5, sick = [0,4]
#
# Output: 4
#
# Explanation:
#
# There is a total of 6 different sequences overall.
#
# Valid infection sequences are [1,2,3], [1,3,2], [3,2,1] and [3,1,2].
#
# [2,3,1] and [2,1,3] are not valid infection sequences because the person
# at index 2 cannot be infected at the first step.
#
# Example 2:
#
# Input: n = 4, sick = [1]
#
# Output: 3
#
# Explanation:
#
# There is a total of 6 different sequences overall.
#
# Valid infection sequences are [0,2,3], [2,0,3] and [2,3,0].
#
# [3,2,0], [3,0,2], and [0,3,2] are not valid infection sequences because
# the infection starts at the person at index 1, then the order of
# infection is 2, then 3, and hence 3 cannot be infected earlier than 2.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# 1 <= sick.length <= n - 1
#
# 0 <= sick[i] <= n - 1
#
# sick is sorted in increasing order.
#

# @lc code=start
from typing import List
from itertools import pairwise


class Solution:
    def numberOfSequence(self, n: int, sick: List[int]) -> int:
        """
        Interview explanation:
        Gaps of healthy people between initially sick; sequences interleave
        infecting those gaps. Ends have 1 infection source; interior gaps of
        length L contribute 2^(L-1) local orders.

        Algorithm:
        - Gap lengths including ends via sentinel -1 and n.
        - ans = (total!) / prod(gap!) * prod(2^(L-1) for interior L>0) mod 1e9+7.

        Complexity: O(n) time for factorials, O(n) space.
        """
        MOD = 10**9 + 7
        gaps = [b - a - 1 for a, b in pairwise([-1] + sick + [n])]
        total = sum(gaps)
        fac = [1] * (total + 1)
        for i in range(2, total + 1):
            fac[i] = fac[i - 1] * i % MOD
        ans = fac[total]
        for g in gaps:
            if g:
                ans = ans * pow(fac[g], MOD - 2, MOD) % MOD
        for g in gaps[1:-1]:
            if g > 1:
                ans = ans * pow(2, g - 1, MOD) % MOD
        return ans
# @lc code=end

