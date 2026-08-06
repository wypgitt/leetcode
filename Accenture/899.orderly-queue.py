#
# @lc app=leetcode id=899 lang=python3
#
# [899] Orderly Queue
#
# https://leetcode.com/problems/orderly-queue/description/
#
# algorithms
# Hard (67.11%)
# Likes:    1845
# Dislikes: 622
# Total Accepted:    87.0K
# Total Submissions: 130K
# Testcase Example:  "\"cba\""
#
# You are given a string s and an integer k. You can choose one of the first k
# letters of s and append it at the end of the string.
#
# Return the lexicographically smallest string you could have after applying
# the mentioned step any number of moves.
#
# Example 1:
#
# Input: s = "cba", k = 1
# Output: "acb"
# Explanation:
# In the first move, we move the 1^st character 'c' to the end, obtaining the
# string "bac".
# In the second move, we move the 1^st character 'b' to the end, obtaining the
# final result "acb".
#
# Example 2:
#
# Input: s = "baaca", k = 3
# Output: "aaabc"
# Explanation:
# In the first move, we move the 1^st character 'b' to the end, obtaining the
# string "aacab".
# In the second move, we move the 3^rd character 'c' to the end, obtaining the
# final result "aaabc".
#
# Constraints:
#
# 1 <= k <= s.length <= 1000
#
# s consist of lowercase English letters.
#

# @lc code=start
class Solution:
    def orderlyQueue(self, s: str, k: int) -> str:
        """
        Interview explanation:
        If k==1 only rotations possible — take lexicographically smallest
        rotation. If k>=2, any permutation is achievable — return sorted(s).

        Algorithm:
        - k==1: min(s[i:]+s[:i] for i). Else: ''.join(sorted(s)).

        Complexity: O(n^2) for k==1 (or O(n) with Booth); O(n log n) for k>=2.
        """
        if k == 1:
            return min(s[i:] + s[:i] for i in range(len(s)))
        return "".join(sorted(s))
# @lc code=end

