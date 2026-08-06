#
# @lc app=leetcode id=1593 lang=python3
#
# [1593] Split a String Into the Max Number of Unique Substrings
#
# https://leetcode.com/problems/split-a-string-into-the-max-number-of-unique-substrings/description/
#
# algorithms
# Medium (68.73%)
# Likes:    1523
# Dislikes: 73
# Total Accepted:    152K
# Total Submissions: 222K
# Testcase Example:  "\"ababccc\""
#
# Given a string s, return the maximum number of unique substrings that the
# given string can be split into.
#
# You can split string s into any list of non-empty substrings, where the
# concatenation of the substrings forms the original string. However, you must
# split the substrings such that all of them are unique.
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: s = "ababccc"
# Output: 5
# Explanation: One way to split maximally is ['a', 'b', 'ab', 'c', 'cc'].
# Splitting like ['a', 'b', 'a', 'b', 'c', 'cc'] is not valid as you have 'a'
# and 'b' multiple times.
#
# Example 2:
#
# Input: s = "aba"
# Output: 2
# Explanation: One way to split maximally is ['a', 'ba'].
#
# Example 3:
#
# Input: s = "aa"
# Output: 1
# Explanation: It is impossible to split the string any further.
#
# Constraints:
#
# 1 <= s.length <= 16
#
# s contains only lower case English letters.
#

# @lc code=start
class Solution:
    def maxUniqueSplit(self, s: str) -> int:
        """
        Interview explanation:
        Maximize number of unique contiguous pieces covering s. Backtracking:
        at each index try every end cut; skip if substring already used; track
        max depth.

        Algorithm (DFS + set):
        - dfs(i): if i==n update ans; for j in i+1..n: sub=s[i:j]; if new:
          add, recurse, remove.

        Complexity: O(n * 2^n) worst; n<=16 so fine.
        """
        n = len(s)
        ans = 0
        used = set()

        def dfs(i: int) -> None:
            nonlocal ans
            if i == n:
                ans = max(ans, len(used))
                return
            # prune
            if len(used) + (n - i) <= ans:
                return
            for j in range(i + 1, n + 1):
                sub = s[i:j]
                if sub in used:
                    continue
                used.add(sub)
                dfs(j)
                used.remove(sub)

        dfs(0)
        return ans
# @lc code=end

