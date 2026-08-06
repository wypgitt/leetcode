#
# @lc app=leetcode id=3320 lang=python3
#
# [3320] Count The Number of Winning Sequences
#
# https://leetcode.com/problems/count-the-number-of-winning-sequences/description/
#
# algorithms
# Hard (32.65%)
# Likes:    105
# Dislikes: 5
# Total Accepted:    11.2K
# Total Submissions: 34.3K
# Testcase Example:  "\"FFF\""
#
#
# Alice and Bob are playing a fantasy battle game consisting of n rounds
# where they summon one of three magical creatures each round: a Fire
# Dragon, a Water Serpent, or an Earth Golem. In each round, players
# simultaneously summon their creature and are awarded points as follows:
#
# If one player summons a Fire Dragon and the other summons an Earth
# Golem, the player who summoned the Fire Dragon is awarded a point.
#
# If one player summons a Water Serpent and the other summons a Fire
# Dragon, the player who summoned the Water Serpent is awarded a point.
#
# If one player summons an Earth Golem and the other summons a Water
# Serpent, the player who summoned the Earth Golem is awarded a point.
#
# If both players summon the same creature, no player is awarded a point.
#
# You are given a string s consisting of n characters 'F', 'W', and 'E',
# representing the sequence of creatures Alice will summon in each round:
#
# If s[i] == 'F', Alice summons a Fire Dragon.
#
# If s[i] == 'W', Alice summons a Water Serpent.
#
# If s[i] == 'E', Alice summons an Earth Golem.
#
# Bob’s sequence of moves is unknown, but it is guaranteed that Bob will
# never summon the same creature in two consecutive rounds. Bob beats
# Alice if the total number of points awarded to Bob after n rounds is
# strictly greater than the points awarded to Alice.
#
# Return the number of distinct sequences Bob can use to beat Alice.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "FFF"
#
# Output: 3
#
# Explanation:
#
# Bob can beat Alice by making one of the following sequences of moves:
# "WFW", "FWF", or "WEW". Note that other winning sequences like "WWE" or
# "EWW" are invalid since Bob cannot make the same move twice in a row.
#
# Example 2:
#
# Input: s = "FWEFW"
#
# Output: 18
#
# Explanation:
#
# Bob can beat Alice by making one of the following sequences of moves:
# "FWFWF", "FWFWE", "FWEFE", "FWEWE", "FEFWF", "FEFWE", "FEFEW", "FEWFE",
# "WFEFE", "WFEWE", "WEFWF", "WEFWE", "WEFEF", "WEFEW", "WEWFW", "WEWFE",
# "EWFWE", or "EWEWE".
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s[i] is one of 'F', 'W', or 'E'.
#

# @lc code=start
class Solution:
    def countWinningSequences(self, s: str) -> int:
        """
        Interview explanation:
        RPS-style scoring (F>E, W>F, E>W). Alice's moves are fixed; Bob cannot
        repeat a creature twice in a row. Count Bob sequences with score_B > score_A.

        Algorithm:
        - Map F/W/E -> 0/1/2. Delta = +1 if (bob-alice)%3==1, -1 if ==2.
        - DP over (round, prev_move, score_offset); sum states with score > 0.

        Complexity: O(n^2) time and space (score in [-n, n]).
        """
        MOD = 10**9 + 7
        n = len(s)
        mp = {"F": 0, "W": 1, "E": 2}
        alice = [mp[c] for c in s]
        off = n
        # dp[prev+1][score+off]: prev in {-1,0,1,2}
        dp = [[0] * (2 * n + 1) for _ in range(4)]
        dp[0][off] = 1
        for i in range(n):
            ndp = [[0] * (2 * n + 1) for _ in range(4)]
            a = alice[i]
            for prev in range(-1, 3):
                row = dp[prev + 1]
                for sc, ways in enumerate(row):
                    if not ways:
                        continue
                    for move in range(3):
                        if move == prev:
                            continue
                        d = (move - a) % 3
                        delta = 1 if d == 1 else (-1 if d == 2 else 0)
                        nsc = sc + delta
                        ndp[move + 1][nsc] = (ndp[move + 1][nsc] + ways) % MOD
            dp = ndp
        ans = 0
        for prev in range(4):
            for sc in range(off + 1, 2 * n + 1):
                ans = (ans + dp[prev][sc]) % MOD
        return ans
# @lc code=end
