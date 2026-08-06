#
# @lc app=leetcode id=1717 lang=python3
#
# [1717] Maximum Score From Removing Substrings
#
# https://leetcode.com/problems/maximum-score-from-removing-substrings/description/
#
# algorithms
# Medium (66.4%)
# Likes:    1938
# Dislikes: 137
# Total Accepted:    245K
# Total Submissions: 369K
# Testcase Example:  "\"cdbcbbaaabab\""
#
# You are given a string s and two integers x and y. You can perform two types
# of operations any number of times.
#
# Remove substring "ab" and gain x points.
#
# For example, when removing "ab" from "cabxbae" it becomes "cxbae".
#
# Remove substring "ba" and gain y points.
#
# For example, when removing "ba" from "cabxbae" it becomes "cabxe".
#
# Return the maximum points you can gain after applying the above operations on
# s.
#
# Example 1:
#
# Input: s = "cdbcbbaaabab", x = 4, y = 5
# Output: 19
# Explanation:
# - Remove the "ba" underlined in "cdbcbbaaabab". Now, s = "cdbcbbaaab" and 5
# points are added to the score.
# - Remove the "ab" underlined in "cdbcbbaaab". Now, s = "cdbcbbaa" and 4
# points are added to the score.
# - Remove the "ba" underlined in "cdbcbbaa". Now, s = "cdbcba" and 5 points
# are added to the score.
# - Remove the "ba" underlined in "cdbcba". Now, s = "cdbc" and 5 points are
# added to the score.
# Total score = 5 + 4 + 5 + 5 = 19.
#
# Example 2:
#
# Input: s = "aabbaaxybbaabb", x = 5, y = 4
# Output: 20
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# 1 <= x, y <= 10^4
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def maximumGain(self, s: str, x: int, y: int) -> int:
        """
        Interview explanation:
        Remove "ab" for x points or "ba" for y. Always remove the higher-scoring
        pattern first (stack), then the other on the remainder.

        Algorithm:
        - If x < y: swap roles of a/b and x/y.
        - First remove "ab" with score x via stack; then remove "ba" with score y.

        Complexity: O(n) time, O(n) space.
        """
        def remove(s: str, a: str, b: str, pts: int):
            st = []
            score = 0
            for c in s:
                if st and st[-1] == a and c == b:
                    st.pop()
                    score += pts
                else:
                    st.append(c)
            return ''.join(st), score

        if x >= y:
            s, sc1 = remove(s, 'a', 'b', x)
            _, sc2 = remove(s, 'b', 'a', y)
        else:
            s, sc1 = remove(s, 'b', 'a', y)
            _, sc2 = remove(s, 'a', 'b', x)
        return sc1 + sc2
# @lc code=end
