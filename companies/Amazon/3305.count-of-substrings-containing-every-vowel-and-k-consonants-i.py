#
# @lc app=leetcode id=3305 lang=python3
#
# [3305] Count of Substrings Containing Every Vowel and K Consonants I
#
# https://leetcode.com/problems/count-of-substrings-containing-every-vowel-and-k-consonants-i/description/
#
# algorithms
# Medium (42.20%)
# Likes:    149
# Dislikes: 14
# Total Accepted:    34K
# Total Submissions: 80.6K
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
# 5 <= word.length <= 250
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
        Count substrings with all five vowels and exactly k consonants.
        Small n (<= 250) still uses the linear two-pointer reduction.

        Algorithm:
        - f(t) = #substrings with all vowels and >= t consonants.
        - Shrink left while valid; each right endpoint contributes `left` starts.
        - Answer = f(k) - f(k + 1).

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

    def countOfSubstrings_brute(self, word: str, k: int) -> int:
        """
        Interview explanation:
        Brute-force all O(n^2) substrings; fine for n <= 250.

        Algorithm:
        - Expand right; track vowel coverage and consonant count; stop early if
          consonants exceed k.

        Complexity: O(n^2) time, O(1) space.
        """
        vowels = set("aeiou")
        n = len(word)
        ans = 0
        for i in range(n):
            seen: set[str] = set()
            cons = 0
            for j in range(i, n):
                ch = word[j]
                if ch in vowels:
                    seen.add(ch)
                else:
                    cons += 1
                    if cons > k:
                        break
                if cons == k and len(seen) == 5:
                    ans += 1
        return ans
# @lc code=end
