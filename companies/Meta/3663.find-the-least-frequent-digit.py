#
# @lc app=leetcode id=3663 lang=python3
#
# [3663] Find The Least Frequent Digit
#
# https://leetcode.com/problems/find-the-least-frequent-digit/description/
#
# algorithms
# Easy (69.72%)
# Likes:    57
# Dislikes: 2
# Total Accepted:    47.2K
# Total Submissions: 67.7K
# Testcase Example:  "1553322"
#
#
# Given an integer n, find the digit that occurs least frequently in its
# decimal representation. If multiple digits have the same frequency,
# choose the smallest digit.
#
# Return the chosen digit as an integer.
#
# The frequency of a digit x is the number of times it appears in the
# decimal representation of n.
#
# Example 1:
#
# Input: n = 1553322
#
# Output: 1
#
# Explanation:
#
# The least frequent digit in n is 1, which appears only once. All other
# digits appear twice.
#
# Example 2:
#
# Input: n = 723344511
#
# Output: 2
#
# Explanation:
#
# The least frequent digits in n are 7, 2, and 5; each appears only once.
#
# Constraints:
#
# 1 <= n <= 2^31​​​​​​​ - 1
#

# @lc code=start
import collections


class Solution:
    def getLeastFrequentDigit(self, n: int) -> int:
        """
        Interview explanation:
        Among digits that appear in n, pick the rarest; break ties by smallest digit.

        Algorithm:
        - Count digit frequencies from the decimal string.
        - Return argmin by (frequency, digit value).

        Complexity: O(log n) time, O(1) space.
        """
        freq = collections.Counter(str(n))
        return int(min(freq, key=lambda d: (freq[d], d)))

    def getLeastFrequentDigit_array(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: fixed-size digit array without hashing.

        Algorithm:
        - While n > 0, increment digit counts; handle n becoming 0 carefully
          by counting from the string or a do-while style loop on digits.
        - Scan digits 0..9 for the best (freq, digit).

        Complexity: O(log n) time, O(1) space.
        """
        s = str(n)
        cnt = [0] * 10
        for ch in s:
            cnt[ord(ch) - 48] += 1
        best_d, best_f = -1, 10**9
        for d in range(10):
            if cnt[d] and cnt[d] < best_f:
                best_f, best_d = cnt[d], d
        return best_d
# @lc code=end
