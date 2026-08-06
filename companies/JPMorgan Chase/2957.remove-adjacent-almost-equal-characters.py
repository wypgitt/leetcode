#
# @lc app=leetcode id=2957 lang=python3
#
# [2957] Remove Adjacent Almost-Equal Characters
#
# https://leetcode.com/problems/remove-adjacent-almost-equal-characters/description/
#
# algorithms
# Medium (53.95%)
# Likes:    210
# Dislikes: 25
# Total Accepted:    31.5K
# Total Submissions: 58.3K
# Testcase Example:  "\"aaaaa\""
#
#
# You are given a 0-indexed string word.
#
# In one operation, you can pick any index i of word and change word[i] to
# any lowercase English letter.
#
# Return the minimum number of operations needed to remove all adjacent
# almost-equal characters from word.
#
# Two characters a and b are almost-equal if a == b or a and b are
# adjacent in the alphabet.
#
# Example 1:
#
# Input: word = "aaaaa"
# Output: 2
# Explanation: We can change word into "acaca" which does not have any
# adjacent almost-equal characters.
# It can be shown that the minimum number of operations needed to remove
# all adjacent almost-equal characters from word is 2.
#
# Example 2:
#
# Input: word = "abddez"
# Output: 2
# Explanation: We can change word into "ybdoez" which does not have any
# adjacent almost-equal characters.
# It can be shown that the minimum number of operations needed to remove
# all adjacent almost-equal characters from word is 2.
#
# Example 3:
#
# Input: word = "zyxyxyz"
# Output: 3
# Explanation: We can change word into "zaxaxaz" which does not have any
# adjacent almost-equal characters.
# It can be shown that the minimum number of operations needed to remove
# all adjacent almost-equal characters from word is 3.
#
# Constraints:
#
# 1 <= word.length <= 100
#
# word consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def removeAlmostEqualCharacters(self, word: str) -> int:
        """
        Interview explanation:
        Almost-equal = same or alphabet-adjacent. Minimize changes so no
        adjacent pair is almost-equal.

        Algorithm:
        - Greedy: scan left to right; when word[i] almost-equals word[i-1],
          change word[i] (count++) and skip pairing with i+1 by advancing.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        i = 1
        n = len(word)
        while i < n:
            if abs(ord(word[i]) - ord(word[i - 1])) <= 1:
                ans += 1
                i += 2  # changed word[i]; word[i+1] vs new char unconstrained optimally
            else:
                i += 1
        return ans
# @lc code=end

