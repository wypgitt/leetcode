#
# @lc app=leetcode id=3211 lang=python3
#
# [3211] Generate Binary Strings Without Adjacent Zeros
#
# https://leetcode.com/problems/generate-binary-strings-without-adjacent-zeros/description/
#
# algorithms
# Medium (88.63%)
# Likes:    327
# Dislikes: 54
# Total Accepted:    92.7K
# Total Submissions: 104.6K
# Testcase Example:  "3"
#
#
# You are given a positive integer n.
#
# A binary string x is valid if all substrings of x of length 2 contain at
# least one "1".
#
# Return all valid strings with length n, in any order.
#
# Example 1:
#
# Input: n = 3
#
# Output: ["010","011","101","110","111"]
#
# Explanation:
#
# The valid strings of length 3 are: "010", "011", "101", "110", and
# "111".
#
# Example 2:
#
# Input: n = 1
#
# Output: ["0","1"]
#
# Explanation:
#
# The valid strings of length 1 are: "0" and "1".
#
# Constraints:
#
# 1 <= n <= 18
#

# @lc code=start
from typing import List


class Solution:
    def validStrings(self, n: int) -> List[str]:
        """
        Interview explanation:
        Valid binary strings of length n have no adjacent "00" (every length-2
        substring contains a 1).

        Algorithm:
        - Backtracking: always may append '1'; append '0' only if the current
          path is empty or ends with '1'.

        Complexity: O(F_n * n) time to build Fibonacci-many strings, O(n) stack.
        """
        ans: List[str] = []

        def dfs(path: str) -> None:
            if len(path) == n:
                ans.append(path)
                return
            dfs(path + "1")
            if not path or path[-1] == "1":
                dfs(path + "0")

        dfs("")
        return ans

    def validStrings_iterative(self, n: int) -> List[str]:
        """
        Interview explanation:
        Alternate BFS / iterative growth of valid prefixes.

        Algorithm:
        - Start from ["0","1"] (or [""] then expand); append allowed bits level
          by level until length n.

        Complexity: O(F_n * n) time and space.
        """
        cur = [""]
        for _ in range(n):
            nxt: List[str] = []
            for s in cur:
                nxt.append(s + "1")
                if not s or s[-1] == "1":
                    nxt.append(s + "0")
            cur = nxt
        return cur
# @lc code=end
