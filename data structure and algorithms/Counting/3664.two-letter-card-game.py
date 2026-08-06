#
# @lc app=leetcode id=3664 lang=python3
#
# [3664] Two-Letter Card Game
#
# https://leetcode.com/problems/two-letter-card-game/description/
#
# algorithms
# Medium (13.14%)
# Likes:    131
# Dislikes: 60
# Total Accepted:    11.8K
# Total Submissions: 90.2K
# Testcase Example:  "[\"aa\",\"ab\",\"ba\",\"ac\"]\n\"a\""
#
#
# You are given a deck of cards represented by a string array cards, and
# each card displays two lowercase letters.
#
# You are also given a letter x. You play a game with the following rules:
#
# Start with 0 points.
#
# On each turn, you must find two compatible cards from the deck that both
# contain the letter x in any position.
#
# Remove the pair of cards and earn 1 point.
#
# The game ends when you can no longer find a pair of compatible cards.
#
# Return the maximum number of points you can gain with optimal play.
#
# Two cards are compatible if the strings differ in exactly 1 position.
#
# Example 1:
#
# Input: cards = ["aa","ab","ba","ac"], x = "a"
#
# Output: 2
#
# Explanation:
#
# On the first turn, select and remove cards "ab" and "ac", which are
# compatible because they differ at only index 1.
#
# On the second turn, select and remove cards "aa" and "ba", which are
# compatible because they differ at only index 0.
#
# Because there are no more compatible pairs, the total score is 2.
#
# Example 2:
#
# Input: cards = ["aa","ab","ba"], x = "a"
#
# Output: 1
#
# Explanation:
#
# On the first turn, select and remove cards "aa" and "ba".
#
# Because there are no more compatible pairs, the total score is 1.
#
# Example 3:
#
# Input: cards = ["aa","ab","ba","ac"], x = "b"
#
# Output: 0
#
# Explanation:
#
# The only cards that contain the character 'b' are "ab" and "ba".
# However, they differ in both indices, so they are not compatible. Thus,
# the output is 0.
#
# Constraints:
#
# 2 <= cards.length <= 10^5
#
# cards[i].length == 2
#
# Each cards[i] is composed of only lowercase English letters between 'a'
# and 'j'.
#
# x is a lowercase English letter between 'a' and 'j'.
#

# @lc code=start
from typing import List


class Solution:
    def score(self, cards: List[str], x: str) -> int:
        """
        Interview explanation:
        Only cards containing x matter. Compatible pairs differ in exactly one
        position, so they live inside the "x?" family or the "?x" family; "xx"
        can be assigned to either family.

        Algorithm:
        - Bucket counts: cnt1[c] for "xc", cnt2[c] for "cx", and both for "xx".
        - Max pairs in one family with extra "xx" cards is
          min(total // 2, total - maxBucket).
        - Try every split of `both` between the two families; take the max sum.

        Complexity: O(n + |alphabet|^2) time with |alphabet| <= 10, O(1) space.
        """
        cnt1 = [0] * 10
        cnt2 = [0] * 10
        both = 0
        for s in cards:
            a, b = s[0], s[1]
            if a == x and b == x:
                both += 1
            elif a == x:
                cnt1[ord(b) - 97] += 1
            elif b == x:
                cnt2[ord(a) - 97] += 1

        def pairs(cnt: List[int], have: int) -> int:
            total = have
            mx = have
            for v in cnt:
                total += v
                if v > mx:
                    mx = v
            return min(total // 2, total - mx)

        ans = 0
        for give in range(both + 1):
            ans = max(ans, pairs(cnt1, give) + pairs(cnt2, both - give))
        return ans
# @lc code=end
