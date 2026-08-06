#
# @lc app=leetcode id=3900 lang=python3
#
# [3900] Longest Balanced Substring After One Swap
#
# https://leetcode.com/problems/longest-balanced-substring-after-one-swap/description/
#
# algorithms
# Medium (14.04%)
# Likes:    131
# Dislikes: 10
# Total Accepted:    10.6K
# Total Submissions: 75.5K
# Testcase Example:  "\"100001\""
#
#
# You are given a binary string s consisting only of characters '0' and
# '1'.
#
# A string is balanced if it contains an equal number of '0's and '1's.
#
# You can perform at most one swap between any two characters in s. Then,
# you select a balanced substring from s.
#
# Return an integer representing the maximum length of the balanced
# substring you can select.
#
# Example 1:
#
# Input: s = "100001"
#
# Output: 4
#
# Explanation:
#
# Swap "100001". The string becomes "101000".
#
# Select the substring "101000", which is balanced because it has two '0's
# and two '1's.
#
# Example 2:
#
# Input: s = "111"
#
# Output: 0
#
# Explanation:
#
# Choose not to perform any swaps.
#
# Select the empty substring, which is balanced because it has zero '0's
# and zero '1's.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of the characters '0' and '1'.
#

# @lc code=start
from bisect import bisect_left
from collections import defaultdict


class Solution:
    def longestBalanced(self, s: str) -> int:
        """
        Interview explanation:
        Maximize length of a balanced (equal 0/1) substring after at most one
        swap of any two characters in s.

        Algorithm:
        - Prefix balance ( +1 for '1', -1 for '0'); no-swap answer is classic
          longest equal-balance span.
        - One useful swap flips substring balance by ±2 (swap across boundary).
        - For each right end, look up left ends with balance±2, capped by global
          zero/one counts so the needed outside char exists.

        Complexity: O(n log n) time, O(n) space.
        """
        total_zeros = s.count("0")
        total_ones = len(s) - total_zeros

        prefix = [0]
        positions = defaultdict(list)
        positions[0].append(0)

        balance = 0
        for index, ch in enumerate(s, 1):
            balance += 1 if ch == "1" else -1
            prefix.append(balance)
            positions[balance].append(index)

        answer = 0
        earliest = {}
        for index, balance in enumerate(prefix):
            if balance in earliest:
                answer = max(answer, index - earliest[balance])
            else:
                earliest[balance] = index

        cap_too_many_ones = 2 * total_zeros
        cap_too_many_zeros = 2 * total_ones

        for right, balance in enumerate(prefix):
            if right == 0:
                continue

            # Original balance is +2: swap an inside '1' with an outside '0'.
            answer = max(
                answer,
                self._best_with_cap(
                    positions[balance - 2],
                    right,
                    cap_too_many_ones,
                ),
            )

            # Original balance is -2: swap an inside '0' with an outside '1'.
            answer = max(
                answer,
                self._best_with_cap(
                    positions[balance + 2],
                    right,
                    cap_too_many_zeros,
                ),
            )

        return answer

    def _best_with_cap(self, starts: list[int], right: int, cap: int) -> int:
        if cap <= 0:
            return 0

        index = bisect_left(starts, right - cap)
        if index < len(starts) and starts[index] < right:
            return right - starts[index]
        return 0
# @lc code=end
