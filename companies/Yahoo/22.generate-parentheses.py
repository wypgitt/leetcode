#
# @lc app=leetcode id=22 lang=python3
#
# [22] Generate Parentheses
#
# https://leetcode.com/problems/generate-parentheses/description/
#
# algorithms
# Medium (78.62%)
# Likes:    23315
# Dislikes: 1087
# Total Accepted:    2.9M
# Total Submissions: 3.7M
# Testcase Example:  '3'
#
# Given n pairs of parentheses, write a function to generate all combinations
# of well-formed parentheses.
# 
# 
# Example 1:
# Input: n = 3
# Output: ["((()))","(()())","(())()","()(())","()()()"]
# Example 2:
# Input: n = 1
# Output: ["()"]
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 8
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        """
        Interview explanation:
        Generate only valid prefixes instead of all 2^(2n) strings. A prefix is
        valid when it never uses more than n opens and never has more closes
        than opens. Backtracking naturally models these constrained choices.

        Edge cases and tests:
        - n=1 returns ["()"].
        - For n=3, all five Catalan combinations are generated.
        - The close count guard prevents invalid prefixes like ")(".

        Complexity: O(C_n * n) time and O(n) recursion space, where C_n is the
        nth Catalan number and output size is unavoidable.
        """
        ans = []
        path = []

        def backtrack(opened: int, closed: int) -> None:
            if len(path) == 2 * n:
                ans.append(''.join(path))
                return
            if opened < n:
                path.append('(')
                backtrack(opened + 1, closed)
                path.pop()
            if closed < opened:
                path.append(')')
                backtrack(opened, closed + 1)
                path.pop()

        backtrack(0, 0)
        return ans
# @lc code=end


