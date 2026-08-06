#
# @lc app=leetcode id=3412 lang=python3
#
# [3412] Find Mirror Score of a String
#
# https://leetcode.com/problems/find-mirror-score-of-a-string/description/
#
# algorithms
# Medium (35.81%)
# Likes:    130
# Dislikes: 9
# Total Accepted:    26.2K
# Total Submissions: 73K
# Testcase Example:  "\"aczzx\""
#
#
# You are given a string s.
#
# We define the mirror of a letter in the English alphabet as its
# corresponding letter when the alphabet is reversed. For example, the
# mirror of 'a' is 'z', and the mirror of 'y' is 'b'.
#
# Initially, all characters in the string s are unmarked.
#
# You start with a score of 0, and you perform the following process on
# the string s:
#
# Iterate through the string from left to right.
#
# At each index i, find the closest unmarked index j such that j < i and
# s[j] is the mirror of s[i]. Then, mark both indices i and j, and add the
# value i - j to the total score.
#
# If no such index j exists for the index i, move on to the next index
# without making any changes.
#
# Return the total score at the end of the process.
#
# Example 1:
#
# Input: s = "aczzx"
#
# Output: 5
#
# Explanation:
#
# i = 0. There is no index j that satisfies the conditions, so we skip.
#
# i = 1. There is no index j that satisfies the conditions, so we skip.
#
# i = 2. The closest index j that satisfies the conditions is j = 0, so we
# mark both indices 0 and 2, and then add 2 - 0 = 2 to the score.
#
# i = 3. There is no index j that satisfies the conditions, so we skip.
#
# i = 4. The closest index j that satisfies the conditions is j = 1, so we
# mark both indices 1 and 4, and then add 4 - 1 = 3 to the score.
#
# Example 2:
#
# Input: s = "abcdef"
#
# Output: 0
#
# Explanation:
#
# For each index i, there is no index j that satisfies the conditions.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of lowercase English letters.
#

# @lc code=start
from collections import defaultdict
from typing import Dict, List


class Solution:
    def calculateScore(self, s: str) -> int:
        """
        Interview explanation:
        Mirror of a letter is its reverse-alphabet partner. Scan left to
        right; for each index, pair with the closest unmarked earlier
        mirror index and add (i-j).

        Algorithm:
        - Keep a stack of unmarked indices per character.
        - At i, look at mirror char's stack; if non-empty, pop closest j
          and add i-j.

        Complexity: O(n) time, O(n) space.
        """
        stacks: Dict[str, List[int]] = defaultdict(list)
        score = 0
        for i, ch in enumerate(s):
            mirror = chr(ord("a") + ord("z") - ord(ch))
            if stacks[mirror]:
                j = stacks[mirror].pop()
                score += i - j
            else:
                stacks[ch].append(i)
        return score
# @lc code=end
