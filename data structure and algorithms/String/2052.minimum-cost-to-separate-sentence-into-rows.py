#
# @lc app=leetcode id=2052 lang=python3
#
# [2052] Minimum Cost to Separate Sentence Into Rows
#
# https://leetcode.com/problems/minimum-cost-to-separate-sentence-into-rows/description/
#
# algorithms
# Medium (51.29%)
# Likes:    45
# Dislikes: 14
# Total Accepted:    2.5K
# Total Submissions: 5K
# Testcase Example:  "\"i love leetcode\"\n12"
#
#
# You are given a string sentence containing words separated by spaces,
# and an integer k. Your task is to separate sentence into rows where the
# number of characters in each row is at most k. You may assume that
# sentence does not begin or end with a space, and the words in sentence
# are separated by a single space.
#
# You can split sentence into rows by inserting line breaks between words
# in sentence. A word cannot be split between two rows. Each word must be
# used exactly once, and the word order cannot be rearranged. Adjacent
# words in a row should be separated by a single space, and rows should
# not begin or end with spaces.
#
# The cost of a row with length n is (k - n)^2, and the total cost is the
# sum of the costs for all rows except the last one.
#
# For example if sentence = "i love leetcode" and k = 12:
#
# Separating sentence into "i", "love", and "leetcode" has a cost of (12 -
# 1)^2 + (12 - 4)^2 = 185.
#
# Separating sentence into "i love", and "leetcode" has a cost of (12 -
# 6)^2 = 36.
#
# Separating sentence into "i", and "love leetcode" is not possible
# because the length of "love leetcode" is greater than k.
#
# Return the minimum possible total cost of separating sentence into rows.
#
# Example 1:
#
# Input: sentence = "i love leetcode", k = 12
# Output: 36
# Explanation:
# Separating sentence into "i", "love", and "leetcode" has a cost of (12 -
# 1)^2 + (12 - 4)^2 = 185.
# Separating sentence into "i love", and "leetcode" has a cost of (12 -
# 6)^2 = 36.
# Separating sentence into "i", "love leetcode" is not possible because
# "love leetcode" has length 13.
# 36 is the minimum possible total cost so return it.
#
# Example 2:
#
# Input: sentence = "apples and bananas taste great", k = 7
# Output: 21
# Explanation
# Separating sentence into "apples", "and", "bananas", "taste", and
# "great" has a cost of (7 - 6)^2 + (7 - 3)^2 + (7 - 7)^2 + (7 - 5)^2 =
# 21.
# 21 is the minimum possible total cost so return it.
#
# Example 3:
#
# Input: sentence = "a", k = 5
# Output: 0
# Explanation:
# The cost of the last row is not included in the total cost, and since
# there is only one row, return 0.
#
# Constraints:
#
# 1 <= sentence.length <= 5000
#
# 1 <= k <= 5000
#
# The length of each word in sentence is at most k.
#
# sentence consists of only lowercase English letters and spaces.
#
# sentence does not begin or end with a space.
#
# Words in sentence are separated by a single space.
#
# @lc code=start
from functools import lru_cache


class Solution:
    def minimumCost(self, sentence: str, k: int) -> int:
        """
        Interview explanation:
        Premium. Place words into rows of width at most k. Non-final rows of
        used length L cost (k-L)^2; the last row costs 0. Minimize total cost.

        Algorithm:
        - dp(i) = min cost for words[i:]. Try ending a row at j if fit; recurse.

        Complexity: O(n^2) time, O(n) space.
        """
        words = sentence.split()
        n = len(words)
        lens = [len(w) for w in words]

        @lru_cache(None)
        def dp(i: int) -> int:
            if i == n:
                return 0
            best = 10**18
            length = -1
            for j in range(i, n):
                length += 1 + lens[j]
                if length > k:
                    break
                if j == n - 1:
                    best = 0
                else:
                    best = min(best, (k - length) ** 2 + dp(j + 1))
            return best

        return dp(0)
# @lc code=end
