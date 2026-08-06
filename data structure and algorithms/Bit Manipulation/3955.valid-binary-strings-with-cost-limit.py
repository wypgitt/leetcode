#
# @lc app=leetcode id=3955 lang=python3
#
# [3955] Valid Binary Strings With Cost Limit
#
# https://leetcode.com/problems/valid-binary-strings-with-cost-limit/description/
#
# algorithms
# Medium (78.90%)
# Likes:    57
# Dislikes: 1
# Total Accepted:    36.6K
# Total Submissions: 46.4K
# Testcase Example:  "3\n1"
#
#
# You are given two integers n and k.
#
# The cost of a binary string s is defined as the sum of all indices i
# (0-based) such that s[i] == '1'.
#
# A binary string is considered valid if:
#
# It does not contain two consecutive '1' characters.
#
# Its cost is less than or equal to k.
#
# Return a list of all valid binary strings of length n in any order.
#
# Example 1:
#
# Input: n = 3, k = 1
#
# Output: ["000","010","100"]
#
# Explanation:
#
# The binary strings of length 3 without consecutive '1' characters are:
#
# "000" : cost = 0
#
# "100" : cost = 0
#
# "010" : cost = 1
#
# "001" : cost = 2
#
# "101" : cost = 0 + 2 = 2
#
# Among these, the strings with cost less than or equal to k = 1 are
# "000", "010" and "100".
#
# Thus, the valid strings are ["000", "010", "100"].
#
# Example 2:
#
# Input: n = 1, k = 0
#
# Output: ["0","1"]
#
# Explanation:
#
# The valid binary strings of length 1 are "0" and "1".
#
# Thus the answer is ["0", "1"].
#
# Constraints:
#
# 1 <= n <= 12
#
# 0 <= k <= n * (n - 1) / 2
#

# @lc code=start
class Solution:
    def generateValidStrings(self, n: int, k: int) -> list[str]:
        """
        Interview explanation:
        Enumerate binary strings of length n with no "11" and cost ≤ k.

        Algorithm:
        - DFS/backtrack placing '0'/'1' (no consecutive 1s), track cost.
        - Collect every string that finishes with cost ≤ k.

        Complexity: O(F_n · n) time (Fibonacci many strings), O(n) space.
        """
        ans = []

        def dfs(i: int, cost: int, last_one: bool, path: list[str]) -> None:
            if cost > k:
                return
            if i == n:
                ans.append(''.join(path))
                return
            path.append('0')
            dfs(i + 1, cost, False, path)
            path.pop()
            if not last_one:
                path.append('1')
                dfs(i + 1, cost + i, True, path)
                path.pop()

        dfs(0, 0, False, [])
        return ans
# @lc code=end
