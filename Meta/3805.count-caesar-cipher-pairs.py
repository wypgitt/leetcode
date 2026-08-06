#
# @lc app=leetcode id=3805 lang=python3
#
# [3805] Count Caesar Cipher Pairs
#
# https://leetcode.com/problems/count-caesar-cipher-pairs/description/
#
# algorithms
# Medium (51.54%)
# Likes:    113
# Dislikes: 2
# Total Accepted:    27.6K
# Total Submissions: 53.5K
# Testcase Example:  "[\"fusion\",\"layout\"]"
#
#
# You are given an array words of n strings. Each string has length m and
# contains only lowercase English letters.
#
# Two strings s and t are similar if we can apply the following operation
# any number of times (possibly zero times) so that s and t become equal.
#
# Choose either s or t.
#
# Replace every letter in the chosen string with the next letter in the
# alphabet cyclically. The next letter after 'z' is 'a'.
#
# Count the number of pairs of indices (i, j) such that:
#
# i < j
#
# words[i] and words[j] are similar.
#
# Return an integer denoting the number of such pairs.
#
# Example 1:
#
# Input: words = ["fusion","layout"]
#
# Output: 1
#
# Explanation:
#
# words[0] = "fusion" and words[1] = "layout" are similar because we can
# apply the operation to "fusion" 6 times. The string "fusion" changes as
# follows.
#
# "fusion"
#
# "gvtjpo"
#
# "hwukqp"
#
# "ixvlrq"
#
# "jywmsr"
#
# "kzxnts"
#
# "layout"
#
# Example 2:
#
# Input: words = ["ab","aa","za","aa"]
#
# Output: 2
#
# Explanation:
#
# words[0] = "ab" and words[2] = "za" are similar. words[1] = "aa" and
# words[3] = "aa" are similar.
#
# Constraints:
#
# 1 <= n == words.length <= 10^5
#
# 1 <= m == words[i].length <= 10^5
#
# 1 <= n * m <= 10^5
#
# words[i] consists only of lowercase English letters.
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def countPairs(self, words: List[str]) -> int:
        """
        Interview explanation:
        Two equal-length strings are similar iff one is a uniform Caesar shift
        of the other. Normalize each word by shifting so the first letter is
        'a', then count pairs sharing a key.

        Algorithm:
        - For each word, apply offset = ord(s[0]) - ord('a') to every char.
        - Count normalized forms; each key with v copies contributes v*(v-1)/2.

        Complexity: O(n*m) time and space for total characters.
        """
        cnt: dict[str, int] = defaultdict(int)
        for s in words:
            offset = ord(s[0]) - ord("a")
            key = "".join(
                chr((ord(c) - ord("a") - offset) % 26 + ord("a")) for c in s
            )
            cnt[key] += 1
        return sum(v * (v - 1) // 2 for v in cnt.values())
# @lc code=end
