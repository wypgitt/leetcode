#
# @lc app=leetcode id=3581 lang=python3
#
# [3581] Count Odd Letters from Number
#
# https://leetcode.com/problems/count-odd-letters-from-number/description/
#
# algorithms
# Easy (84.65%)
# Likes:    8
# Dislikes: 2
# Total Accepted:    1.6K
# Total Submissions: 1.9K
# Testcase Example:  "41"
#
#
# You are given an integer n perform the following steps:
#
# Convert each digit of n into its lowercase English word (e.g., 4 →
# "four", 1 → "one").
#
# Concatenate those words in the original digit order to form a string s.
#
# Return the number of distinct characters in s that appear an odd number
# of times.
#
# Example 1:
#
# Input: n = 41
#
# Output: 5
#
# Explanation:
#
# 41 → "fourone"
#
# Characters with odd frequencies: 'f', 'u', 'r', 'n', 'e'. Thus, the
# answer is 5.
#
# Example 2:
#
# Input: n = 20
#
# Output: 5
#
# Explanation:
#
# 20 → "twozero"
#
# Characters with odd frequencies: 't', 'w', 'z', 'e', 'r'. Thus, the
# answer is 5.
#
# Constraints:
#
# 1 <= n <= 10^9
#

# @lc code=start

from collections import Counter


class Solution:
    def countOddLetters(self, n: int) -> int:
        """
        Interview explanation:
        Spell each digit in English, concatenate, and count characters whose
        frequency is odd.

        Algorithm:
        - Map digits to words; tally letter frequencies while extracting digits.
        - Return how many letters have an odd count.

        Complexity: O(log n) time, O(1) space.
        """
        words = [
            "zero", "one", "two", "three", "four",
            "five", "six", "seven", "eight", "nine",
        ]
        cnt: Counter[str] = Counter()
        if n == 0:
            cnt.update(words[0])
        while n:
            n, d = divmod(n, 10)
            cnt.update(words[d])
        return sum(v % 2 for v in cnt.values())

    def countOddLetters_array(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: fixed-size frequency array of 26 letters.

        Algorithm:
        - Same digit-word expansion; increment cnt[c-'a']; sum odd entries.

        Complexity: O(log n) time, O(1) space.
        """
        words = [
            "zero", "one", "two", "three", "four",
            "five", "six", "seven", "eight", "nine",
        ]
        freq = [0] * 26
        while True:
            d = n % 10
            for ch in words[d]:
                freq[ord(ch) - 97] += 1
            n //= 10
            if n == 0:
                break
        return sum(v % 2 for v in freq)
# @lc code=end
