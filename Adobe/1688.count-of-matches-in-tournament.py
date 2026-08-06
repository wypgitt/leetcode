#
# @lc app=leetcode id=1688 lang=python3
#
# [1688] Count of Matches in Tournament
#
# https://leetcode.com/problems/count-of-matches-in-tournament/description/
#
# algorithms
# Easy (86.52%)
# Likes:    1900
# Dislikes: 248
# Total Accepted:    339K
# Total Submissions: 392K
# Testcase Example:  "7"
#
# You are given an integer n, the number of teams in a tournament that has
# strange rules:
#
# If the current number of teams is even, each team gets paired with another
# team. A total of n / 2 matches are played, and n / 2 teams advance to the
# next round.
#
# If the current number of teams is odd, one team randomly advances in the
# tournament, and the rest gets paired. A total of (n - 1) / 2 matches are
# played, and (n - 1) / 2 + 1 teams advance to the next round.
#
# Return the number of matches played in the tournament until a winner is
# decided.
#
# Example 1:
#
# Input: n = 7
# Output: 6
# Explanation: Details of the tournament:
# - 1st Round: Teams = 7, Matches = 3, and 4 teams advance.
# - 2nd Round: Teams = 4, Matches = 2, and 2 teams advance.
# - 3rd Round: Teams = 2, Matches = 1, and 1 team is declared the winner.
# Total number of matches = 3 + 2 + 1 = 6.
#
# Example 2:
#
# Input: n = 14
# Output: 13
# Explanation: Details of the tournament:
# - 1st Round: Teams = 14, Matches = 7, and 7 teams advance.
# - 2nd Round: Teams = 7, Matches = 3, and 4 teams advance.
# - 3rd Round: Teams = 4, Matches = 2, and 2 teams advance.
# - 4th Round: Teams = 2, Matches = 1, and 1 team is declared the winner.
# Total number of matches = 7 + 3 + 2 + 1 = 13.
#
# Constraints:
#
# 1 <= n <= 200
#

# @lc code=start
class Solution:
    def numberOfMatches(self, n: int) -> int:
        """
        Interview explanation:
        Tournament: each match eliminates one team; need n-1 eliminations for
        one winner. So answer is always n-1.

        Algorithm:
        - return n - 1

        Complexity: O(1).
        """
        return n - 1

    def numberOfMatches_simulate(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: simulate rounds — even: n/2 matches, n/2 advance; odd:
        (n-1)/2 matches, (n-1)/2+1 advance.

        Algorithm:
        - ans=0; while n>1: ans+=n//2; n=(n+1)//2

        Complexity: O(log n) time.
        """
        ans = 0
        while n > 1:
            ans += n // 2
            n = (n + 1) // 2
        return ans
# @lc code=end
