#
# @lc app=leetcode id=1400 lang=python3
#
# [1400] Construct K Palindrome Strings
#
# https://leetcode.com/problems/construct-k-palindrome-strings/description/
#
# algorithms
# Medium (68.51%)
# Likes:    1800
# Dislikes: 160
# Total Accepted:    213K
# Total Submissions: 311K
# Testcase Example:  "\"annabelle\""
#
# Given a string s and an integer k, return true if you can use all the
# characters in s to construct non-empty k palindrome strings or false
# otherwise.
#
# Example 1:
#
# Input: s = "annabelle", k = 2
# Output: true
# Explanation: You can construct two palindromes using all characters in s.
# Some possible constructions "anna" + "elble", "anbna" + "elle", "anellena" +
# "b"
#
# Example 2:
#
# Input: s = "leetcode", k = 3
# Output: false
# Explanation: It is impossible to construct 3 palindromes using all the
# characters of s.
#
# Example 3:
#
# Input: s = "true", k = 4
# Output: true
# Explanation: The only possible solution is to put each character in a
# separate string.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters.
#
# 1 <= k <= 10^5
#

# @lc code=start

from collections import Counter


class Solution:
    def canConstruct(self, s: str, k: int) -> bool:
        """
        Interview explanation:
        Can rearrange s into k nonempty palindromes? Need k ≤ len(s), and at
        most k characters with odd count (each palindrome can absorb one odd).

        Algorithm:
        - odds = count of chars with odd frequency; return k<=n and odds<=k

        Complexity: O(n) time, O(1) alphabet space.
        """
        if k > len(s):
            return False
        cnt = Counter(s)
        odds = sum(v & 1 for v in cnt.values())
        return odds <= k
# @lc code=end
