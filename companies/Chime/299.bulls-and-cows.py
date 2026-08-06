#
# @lc app=leetcode id=299 lang=python3
#
# [299] Bulls and Cows
#
# https://leetcode.com/problems/bulls-and-cows/description/
#
# algorithms
# Medium (52.82%)
# Likes:    2649
# Dislikes: 1821
# Total Accepted:    461K
# Total Submissions: 873K
# Testcase Example:  "\"1807\""
#
# You are playing the Bulls and Cows game with your friend.
#
# You write down a secret number and ask your friend to guess what the number
# is. When your friend makes a guess, you provide a hint with the following
# info:
#
# The number of "bulls", which are digits in the guess that are in the correct
# position.
#
# The number of "cows", which are digits in the guess that are in your secret
# number but are located in the wrong position. Specifically, the non-bull
# digits in the guess that could be rearranged such that they become bulls.
#
# Given the secret number secret and your friend's guess guess, return the hint
# for your friend's guess.
#
# The hint should be formatted as "xAyB", where x is the number of bulls and y
# is the number of cows. Note that both secret and guess may contain duplicate
# digits.
#
# Example 1:
#
# Input: secret = "1807", guess = "7810"
# Output: "1A3B"
# Explanation: Bulls are connected with a '|' and cows are underlined:
# "1807"
# |
# "7810"
#
# Example 2:
#
# Input: secret = "1123", guess = "0111"
# Output: "1A1B"
# Explanation: Bulls are connected with a '|' and cows are underlined:
# "1123" "1123"
# | or |
# "0111" "0111"
# Note that only one of the two unmatched 1s is counted as a cow since the
# non-bull digits can only be rearranged to allow one 1 to be a bull.
#
# Constraints:
#
# 1 <= secret.length, guess.length <= 1000
#
# secret.length == guess.length
#
# secret and guess consist of digits only.
#

# @lc code=start
from collections import Counter


class Solution:
    def getHint(self, secret: str, guess: str) -> str:
        """
        Interview explanation:
        Bulls = exact position matches. Cows = digit matches in wrong positions.
        One pass: count bulls; for non-bulls track digit frequency differences.

        Algorithm:
        - For each index: if equal, bull++; else count[secret]++, count[guess]--
          (or two counters then sum min).
        - cows = sum of min frequencies for mismatched digits.

        Complexity: O(n) time, O(1) space (10 digits).
        """
        bulls = 0
        s_cnt = Counter()
        g_cnt = Counter()
        for a, b in zip(secret, guess):
            if a == b:
                bulls += 1
            else:
                s_cnt[a] += 1
                g_cnt[b] += 1
        cows = sum(min(s_cnt[d], g_cnt[d]) for d in s_cnt)
        return f"{bulls}A{cows}B"
# @lc code=end

