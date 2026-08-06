#
# @lc app=leetcode id=1177 lang=python3
#
# [1177] Can Make Palindrome from Substring
#
# https://leetcode.com/problems/can-make-palindrome-from-substring/description/
#
# algorithms
# Medium (42.02%)
# Likes:    886
# Dislikes: 282
# Total Accepted:    37.6K
# Total Submissions: 89.5K
# Testcase Example:  "\"abcda\""
#
# You are given a string s and array queries where queries[i] = [left_i,
# right_i, k_i]. We may rearrange the substring s[left_i...right_i] for each
# query and then choose up to k_i of them to replace with any lowercase English
# letter.
#
# If the substring is possible to be a palindrome string after the operations
# above, the result of the query is true. Otherwise, the result is false.
#
# Return a boolean array answer where answer[i] is the result of the i^th query
# queries[i].
#
# Note that each letter is counted individually for replacement, so if, for
# example s[left_i...right_i] = "aaa", and k_i = 2, we can only replace two of
# the letters. Also, note that no query modifies the initial string s.
#
# Example :
#
# Input: s = "abcda", queries = [[3,3,0],[1,2,0],[0,3,1],[0,3,2],[0,4,1]]
# Output: [true,false,false,true,true]
# Explanation:
# queries[0]: substring = "d", is palidrome.
# queries[1]: substring = "bc", is not palidrome.
# queries[2]: substring = "abcd", is not palidrome after replacing only 1
# character.
# queries[3]: substring = "abcd", could be changed to "abba" which is
# palidrome. Also this can be changed to "baab" first rearrange it "bacd" then
# replace "cd" with "ab".
# queries[4]: substring = "abcda", could be changed to "abcba" which is
# palidrome.
#
# Example 2:
#
# Input: s = "lyb", queries = [[0,1,0],[2,2,1]]
# Output: [false,true]
#
# Constraints:
#
# 1 <= s.length, queries.length <= 10^5
#
# 0 <= left_i <= right_i < s.length
#
# 0 <= k_i <= s.length
#
# s consists of lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def canMakePaliQueries(self, s: str, queries: List[List[int]]) -> List[bool]:
        """
        Interview explanation:
        After rearranging, a string is a palindrome iff at most one character
        has odd count. With ≤ k replacements, we can fix floor(odd_count/2)
        odds (each replacement pairs two odds). Use prefix XOR bitmasks of
        char parities for O(1) range odd-count queries.

        Algorithm (prefix XOR / bits):
        - pref[0]=0; pref[i+1] = pref[i] XOR (1 << (s[i]-'a')).
        - For [L,R]: mask = pref[R+1] XOR pref[L]; odds = popcount(mask).
        - True iff odds // 2 <= k.

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(s)
        pref = [0] * (n + 1)
        for i, ch in enumerate(s):
            pref[i + 1] = pref[i] ^ (1 << (ord(ch) - ord('a')))

        ans = []
        for left, right, k in queries:
            mask = pref[right + 1] ^ pref[left]
            odds = mask.bit_count()
            ans.append(odds // 2 <= k)
        return ans
# @lc code=end
