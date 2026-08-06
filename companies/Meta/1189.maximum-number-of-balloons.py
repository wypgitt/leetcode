#
# @lc app=leetcode id=1189 lang=python3
#
# [1189] Maximum Number of Balloons
#
# https://leetcode.com/problems/maximum-number-of-balloons/description/
#
# algorithms
# Easy (64.24%)
# Likes:    2157
# Dislikes: 128
# Total Accepted:    502K
# Total Submissions: 781K
# Testcase Example:  "\"nlaebolko\""
#
# Given a string text, you want to use the characters of text to form as many
# instances of the word "balloon" as possible.
#
# You can use each character in text at most once. Return the maximum number of
# instances that can be formed.
#
# Example 1:
#
# Input: text = "nlaebolko"
# Output: 1
#
# Example 2:
#
# Input: text = "loonbalxballpoon"
# Output: 2
#
# Example 3:
#
# Input: text = "leetcode"
# Output: 0
#
# Constraints:
#
# 1 <= text.length <= 10^4
#
# text consists of lower case English letters only.
#
# Note: This question is the same as 2287: Rearrange Characters to Make Target
# String.
#

# @lc code=start

from collections import Counter


class Solution:
    def maxNumberOfBalloons(self, text: str) -> int:
        """
        Interview explanation:
        "balloon" needs b,a,l,l,o,o,n — so l and o are needed twice. Count
        letters in text; answer is limited by the scarcest required letter
        (halve counts for l and o).

        Algorithm:
        - cnt = Counter(text)
        - return min(cnt['b'], cnt['a'], cnt['l']//2, cnt['o']//2, cnt['n'])

        Complexity: O(n) time, O(1) space (26 letters).
        """
        cnt = Counter(text)
        return min(cnt['b'], cnt['a'], cnt['l'] // 2, cnt['o'] // 2, cnt['n'])
# @lc code=end
