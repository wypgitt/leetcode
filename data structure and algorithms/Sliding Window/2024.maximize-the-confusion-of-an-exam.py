#
# @lc app=leetcode id=2024 lang=python3
#
# [2024] Maximize the Confusion of an Exam
#
# https://leetcode.com/problems/maximize-the-confusion-of-an-exam/description/
#
# algorithms
# Medium (70.37%)
# Likes:    3129
# Dislikes: 56
# Total Accepted:    153.2K
# Total Submissions: 217.7K
# Testcase Example:  "\"TTFF\"\n2"
#
# A teacher is writing a test with n true/false questions, with 'T' denoting
# true and 'F' denoting false. He wants to confuse the students by maximizing
# the number of consecutive questions with the same answer (multiple trues or
# multiple falses in a row).
#
# You are given a string answerKey, where answerKey[i] is the original answer to
# the i^th question. In addition, you are given an integer k, the maximum number
# of times you may perform the following operation:
#
#
# Change the answer key for any question to 'T' or 'F' (i.e., set answerKey[i]
# to 'T' or 'F').
#
# Return the maximum number of consecutive 'T's or 'F's in the answer key after
# performing the operation at most k times.
#
#
#
# Example 1:
#
# Input: answerKey = "TTFF", k = 2
# Output: 4
# Explanation: We can replace both the 'F's with 'T's to make answerKey =
# "TTTT".
# There are four consecutive 'T's.
#
# Example 2:
#
# Input: answerKey = "TFFT", k = 1
# Output: 3
# Explanation: We can replace the first 'T' with an 'F' to make answerKey =
# "FFFT".
# Alternatively, we can replace the second 'T' with an 'F' to make answerKey =
# "TFFF".
# In both cases, there are three consecutive 'F's.
#
# Example 3:
#
# Input: answerKey = "TTFTTFTT", k = 1
# Output: 5
# Explanation: We can replace the first 'F' to make answerKey = "TTTTTFTT"
# Alternatively, we can replace the second 'F' to make answerKey = "TTFTTTTT".
# In both cases, there are five consecutive 'T's.
#
#
#
# Constraints:
#
#
# n == answerKey.length
#
#
# 1 <= n <= 5 * 10^4
#
#
# answerKey[i] is either 'T' or 'F'
#
#
# 1 <= k <= n
#

# @lc code=start
from collections import Counter


class Solution:
    def maxConsecutiveAnswers(self, answerKey: str, k: int) -> int:
        """
        Interview explanation:
        Change at most k answers; maximize longest consecutive T or F.

        Algorithm:
        - Sliding window for all-T and all-F allowing <=k flips.

        Complexity: O(n) time, O(1) space.
        """
        def longest(ch: str) -> int:
            left = other = best = 0
            for right, c in enumerate(answerKey):
                if c != ch:
                    other += 1
                while other > k:
                    if answerKey[left] != ch:
                        other -= 1
                    left += 1
                best = max(best, right - left + 1)
            return best

        return max(longest('T'), longest('F'))

    def maxConsecutiveAnswers_two_pointers(self, answerKey: str, k: int) -> int:
        """
        Interview explanation:
        Single window: shrink while replacements needed (window - majority) > k.

        Algorithm:
        - Expand; while len - max(count) > k shrink left.

        Complexity: O(n) time, O(1) space.
        """
        cnt = Counter()
        left = best = 0
        for right, c in enumerate(answerKey):
            cnt[c] += 1
            while (right - left + 1) - max(cnt.values()) > k:
                cnt[answerKey[left]] -= 1
                left += 1
            best = max(best, right - left + 1)
        return best
# @lc code=end
