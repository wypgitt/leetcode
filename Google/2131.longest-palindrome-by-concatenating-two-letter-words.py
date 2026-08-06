#
# @lc app=leetcode id=2131 lang=python3
#
# [2131] Longest Palindrome by Concatenating Two Letter Words
#
# https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/description/
#
# algorithms
# Medium (53.46%)
# Likes:    2973
# Dislikes: 81
# Total Accepted:    247.8K
# Total Submissions: 463.6K
# Testcase Example:  "[\"lc\",\"cl\",\"gg\"]"
#
# You are given an array of strings words. Each element of words consists of two
# lowercase English letters.
#
# Create the longest possible palindrome by selecting some elements from words
# and concatenating them in any order. Each element can be selected at most
# once.
#
# Return the length of the longest palindrome that you can create. If it is
# impossible to create any palindrome, return 0.
#
# A palindrome is a string that reads the same forward and backward.
#
#
#
# Example 1:
#
# Input: words = ["lc","cl","gg"]
# Output: 6
# Explanation: One longest palindrome is "lc" + "gg" + "cl" = "lcggcl", of
# length 6.
# Note that "clgglc" is another longest palindrome that can be created.
#
# Example 2:
#
# Input: words = ["ab","ty","yt","lc","cl","ab"]
# Output: 8
# Explanation: One longest palindrome is "ty" + "lc" + "cl" + "yt" = "tylcclyt",
# of length 8.
# Note that "lcyttycl" is another longest palindrome that can be created.
#
# Example 3:
#
# Input: words = ["cc","ll","xx"]
# Output: 2
# Explanation: One longest palindrome is "cc", of length 2.
# Note that "ll" is another longest palindrome that can be created, and so is
# "xx".
#
#
#
# Constraints:
#
#
# 1 <= words.length <= 10^5
#
#
# words[i].length == 2
#
#
# words[i] consists of lowercase English letters.
#


# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def longestPalindrome(self, words: List[str]) -> int:
        """
        Interview explanation:
        Concatenate 2-letter words to form a palindrome; return max length.

        Algorithm:
        - Count words. For ab with a!=b, pair with ba: 4*min(cnt[ab],cnt[ba]).
          For aa, use pairs 4*(cnt//2); at most one leftover aa in center (+2).

        Complexity: O(n) time, O(1)/O(n) space (26^2 keys).
        """
        cnt = Counter(words)
        ans = 0
        center = False
        seen = set()
        for w, c in cnt.items():
            if w[0] == w[1]:
                ans += (c // 2) * 4
                if c % 2:
                    center = True
            else:
                rev = w[1] + w[0]
                if w < rev:  # handle pair once
                    ans += 4 * min(c, cnt[rev])
        if center:
            ans += 2
        return ans
# @lc code=end

