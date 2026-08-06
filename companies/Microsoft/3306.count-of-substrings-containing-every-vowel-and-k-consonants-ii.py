#
# @lc app=leetcode id=3306 lang=python3
#
# [3306] Count of Substrings Containing Every Vowel and K Consonants II
#
# https://leetcode.com/problems/count-of-substrings-containing-every-vowel-and-k-consonants-ii/description/
#
# algorithms
# Medium (40.74%)
# Likes:    1019
# Dislikes: 151
# Total Accepted:    116.3K
# Total Submissions: 285.4K
# Testcase Example:  "\"aeioqq\"\n1"
#
#
# You are given a string word and a non-negative integer k.
#
# Return the total number of substrings of word that contain every vowel
# ('a', 'e', 'i', 'o', and 'u') at least once and exactly k consonants.
#
# Example 1:
#
# Input: word = "aeioqq", k = 1
#
# Output: 0
#
# Explanation:
#
# There is no substring with every vowel.
#
# Example 2:
#
# Input: word = "aeiou", k = 0
#
# Output: 1
#
# Explanation:
#
# The only substring with every vowel and zero consonants is word[0..4],
# which is "aeiou".
#
# Example 3:
#
# Input: word = "ieaouqqieaouqq", k = 1
#
# Output: 3
#
# Explanation:
#
# The substrings with every vowel and one consonant are:
#
# word[0..5], which is "ieaouq".
#
# word[6..11], which is "qieaou".
#
# word[7..12], which is "ieaouq".
#
# Constraints:
#
# 5 <= word.length <= 2 * 10^5
#
# word consists only of lowercase English letters.
#
# 0 <= k <= word.length - 5
#

# @lc code=start
class Solution:
    def countOfSubstrings(self, word: str, k: int) -> int:
        """
        Interview explanation:
        Same as I, but n <= 2e5 so we need linear sliding windows: count
        substrings with every vowel and exactly k consonants.

        Algorithm:
        - f(t) = substrings with all vowels and at least t consonants.
        - Two-pointer: shrink while valid; add `left` per right endpoint.
        - Answer f(k) - f(k + 1).

        Complexity: O(n) time, O(1) space.
        """
        vowels = set("aeiou")

        def at_least(need: int) -> int:
            cnt: dict[str, int] = {}
            cons = 0
            left = 0
            res = 0
            for right, ch in enumerate(word):
                if ch in vowels:
                    cnt[ch] = cnt.get(ch, 0) + 1
                else:
                    cons += 1
                while len(cnt) == 5 and cons >= need:
                    c = word[left]
                    if c in vowels:
                        cnt[c] -= 1
                        if cnt[c] == 0:
                            del cnt[c]
                    else:
                        cons -= 1
                    left += 1
                res += left
            return res

        return at_least(k) - at_least(k + 1)
# @lc code=end
