#
# @lc app=leetcode id=3441 lang=python3
#
# [3441] Minimum Cost Good Caption
#
# https://leetcode.com/problems/minimum-cost-good-caption/description/
#
# algorithms
# Hard (21.22%)
# Likes:    43
# Dislikes: 7
# Total Accepted:    4K
# Total Submissions: 18.9K
# Testcase Example:  "\"cdcd\""
#
#
# You are given a string caption of length n. A good caption is a string
# where every character appears in groups of at least 3 consecutive
# occurrences.
#
# For example:
#
# "aaabbb" and "aaaaccc" are good captions.
#
# "aabbb" and "ccccd" are not good captions.
#
# You can perform the following operation any number of times:
#
# Choose an index i (where 0 <= i < n) and change the character at that
# index to either:
#
# The character immediately before it in the alphabet (if caption[i] !=
# 'a').
#
# The character immediately after it in the alphabet (if caption[i] !=
# 'z').
#
# Your task is to convert the given caption into a good caption using the
# minimum number of operations, and return it. If there are multiple
# possible good captions, return the lexicographically smallest one among
# them. If it is impossible to create a good caption, return an empty
# string "".
#
# Example 1:
#
# Input: caption = "cdcd"
#
# Output: "cccc"
#
# Explanation:
#
# It can be shown that the given caption cannot be transformed into a good
# caption with fewer than 2 operations. The possible good captions that
# can be created using exactly 2 operations are:
#
# "dddd": Change caption[0] and caption[2] to their next character 'd'.
#
# "cccc": Change caption[1] and caption[3] to their previous character
# 'c'.
#
# Since "cccc" is lexicographically smaller than "dddd", return "cccc".
#
# Example 2:
#
# Input: caption = "aca"
#
# Output: "aaa"
#
# Explanation:
#
# It can be proven that the given caption requires at least 2 operations
# to be transformed into a good caption. The only good caption that can be
# obtained with exactly 2 operations is as follows:
#
# Operation 1: Change caption[1] to 'b'. caption = "aba".
#
# Operation 2: Change caption[1] to 'a'. caption = "aaa".
#
# Thus, return "aaa".
#
# Example 3:
#
# Input: caption = "bc"
#
# Output: ""
#
# Explanation:
#
# It can be shown that the given caption cannot be converted to a good
# caption by using any number of operations.
#
# Constraints:
#
# 1 <= caption.length <= 5 * 10^4
#
# caption consists only of lowercase English letters.
#

# @lc code=start

class Solution:
    def minCostGoodCaption(self, caption: str) -> str:
        """
        Interview explanation:
        A good caption is a concatenation of runs of length >= 3. Each change costs
        |ord delta|, so choose letters to minimize total cost and break ties
        lexicographically.

        Algorithm:
        - DP backward: dp[i][c][k] = min cost for caption[i..] ending a run of letter
          c with consecutive count encoded as k in {0,1,2+} (need k==2 at start).
        - Reconstruct greedily: start with cheapest lex-smallest letter for a length-3
          run, then either extend that letter or open a new length-3 run when cheaper
          / lexicographically better.

        Complexity: O(n) time and space (26*3 states per index).
        """
        n = len(caption)
        if n < 3:
            return ""

        MAX = 10**9
        # dp[i][c][0/1/2]: min cost of suffix starting at i with run-progress of c
        dp = [[[MAX] * 3 for _ in range(26)] for _ in range(n)]
        caps = [ord(ch) - 97 for ch in caption]

        for c in range(26):
            dp[n - 1][c][0] = abs(caps[n - 1] - c)

        min_cost = MAX
        for i in range(n - 2, -1, -1):
            new_min = MAX
            for c in range(26):
                change = abs(caps[i] - c)
                # start a new run of c (previous suffix already valid)
                dp[i][c][0] = change + min_cost
                # second char of a run of c
                dp[i][c][1] = change + dp[i + 1][c][0]
                # third+ char of a run of c (suffix must be valid for same c)
                dp[i][c][2] = change + min(dp[i + 1][c][1], dp[i + 1][c][2])
                new_min = min(new_min, dp[i][c][2])
            min_cost = new_min

        ans: list[str] = []
        cost = MAX
        letter = -1
        for c in range(25, -1, -1):
            if dp[0][c][2] <= cost:
                letter = c
                cost = dp[0][c][2]

        def append_letter(i: int, let: int) -> int:
            ans.append(chr(97 + let))
            return abs(caps[i] - let)

        cost -= append_letter(0, letter)
        cost -= append_letter(1, letter)
        cost -= append_letter(2, letter)

        i = 3
        while i < n:
            next_letter = 26
            for c in range(25, -1, -1):
                if cost == dp[i][c][2]:
                    next_letter = c
            # Switch if a smaller letter opens a valid new run, or current letter
            # cannot continue at this remaining cost.
            if next_letter < letter or min(dp[i][letter]) > cost:
                letter = next_letter
                cost -= append_letter(i, letter)
                cost -= append_letter(i + 1, letter)
                cost -= append_letter(i + 2, letter)
                i += 3
            else:
                cost -= append_letter(i, letter)
                i += 1

        return "".join(ans)
# @lc code=end
