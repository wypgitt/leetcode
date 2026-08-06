#
# @lc app=leetcode id=1324 lang=python3
#
# [1324] Print Words Vertically
#
# https://leetcode.com/problems/print-words-vertically/description/
#
# algorithms
# Medium (67.96%)
# Likes:    831
# Dislikes: 121
# Total Accepted:    54.1K
# Total Submissions: 79.6K
# Testcase Example:  "\"HOW ARE YOU\""
#
# Given a string s. Return all the words vertically in the same order in which
# they appear in s.
#
# Words are returned as a list of strings, complete with spaces when is
# necessary. (Trailing spaces are not allowed).
#
# Each word would be put on only one column and that in one column there will
# be only one word.
#
# Example 1:
#
# Input: s = "HOW ARE YOU"
# Output: ["HAY","ORO","WEU"]
# Explanation: Each word is printed vertically.
# "HAY"
# "ORO"
# "WEU"
#
# Example 2:
#
# Input: s = "TO BE OR NOT TO BE"
# Output: ["TBONTB","OEROOE"," T"]
# Explanation: Trailing spaces is not allowed.
# "TBONTB"
# "OEROOE"
# " T"
#
# Example 3:
#
# Input: s = "CONTEST IS COMING"
# Output: ["CIC","OSO","N M","T I","E N","S G","T"]
#
# Constraints:
#
# 1 <= s.length <= 200
#
# s contains only upper case English letters.
#
# It's guaranteed that there is only one space between 2 words.
#

# @lc code=start
from typing import List


class Solution:
    def printVertically(self, s: str) -> List[str]:
        """
        Interview explanation:
        Write words column-wise: result[i] is i-th character of each word
        (space if missing), rstrip trailing spaces.

        Algorithm:
        - Split words; for col in 0..max_len-1 build string; rstrip.

        Complexity: O(total chars) time/space.
        """
        words = s.split()
        m = max(len(w) for w in words)
        ans = []
        for i in range(m):
            col = []
            for w in words:
                col.append(w[i] if i < len(w) else " ")
            ans.append("".join(col).rstrip())
        return ans
# @lc code=end

