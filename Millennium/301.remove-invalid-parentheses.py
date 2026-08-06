#
# @lc app=leetcode id=301 lang=python3
#
# [301] Remove Invalid Parentheses
#
# https://leetcode.com/problems/remove-invalid-parentheses/description/
#
# algorithms
# Hard (50.07%)
# Likes:    6091
# Dislikes: 303
# Total Accepted:    513K
# Total Submissions: 1.0M
# Testcase Example:  "\"()())()\""
#
# Given a string s that contains parentheses and letters, remove the minimum
# number of invalid parentheses to make the input string valid.
#
# Return a list of unique strings that are valid with the minimum number of
# removals. You may return the answer in any order.
#
# Example 1:
#
# Input: s = "()())()"
# Output: ["(())()","()()()"]
#
# Example 2:
#
# Input: s = "(a)())()"
# Output: ["(a())()","(a)()()"]
#
# Example 3:
#
# Input: s = ")("
# Output: [""]
#
# Constraints:
#
# 1 <= s.length <= 25
#
# s consists of lowercase English letters and parentheses '(' and ')'.
#
# There will be at most 20 parentheses in s.
#

# @lc code=start
from collections import deque
from typing import List, Set


class Solution:
    def removeInvalidParentheses(self, s: str) -> List[str]:
        """
        Interview explanation:
        Remove the minimum number of parentheses to make s valid; return all
        unique valid results. BFS by deleting one char at a time finds the
        minimum removals first.

        Algorithm (BFS — primary):
        - Level = strings after the same number of deletions.
        - At each level, if any string is valid, collect all valid and stop.
        - Generate neighbors by deleting one '(' or ')' at each position.

        Complexity: O(n * 2^n) worst case, O(n * 2^n) space.
        """
        def valid(t: str) -> bool:
            bal = 0
            for ch in t:
                if ch == "(":
                    bal += 1
                elif ch == ")":
                    bal -= 1
                    if bal < 0:
                        return False
            return bal == 0

        q = deque([s])
        seen: Set[str] = {s}
        ans: List[str] = []
        while q:
            found = False
            for _ in range(len(q)):
                cur = q.popleft()
                if valid(cur):
                    ans.append(cur)
                    found = True
                if found:
                    continue
                for i, ch in enumerate(cur):
                    if ch not in "()":
                        continue
                    nxt = cur[:i] + cur[i + 1 :]
                    if nxt not in seen:
                        seen.add(nxt)
                        q.append(nxt)
            if found:
                break
        return ans

    def removeInvalidParenthesesDFS(self, s: str) -> List[str]:
        """
        Interview explanation:
        Alternate: compute minimum removals of '(' and ')', then DFS prune
        when remaining removals or balance go invalid; collect unique results.

        Complexity: O(2^n) with pruning, O(n) recursion depth.
        """
        left_rem = right_rem = 0
        for ch in s:
            if ch == "(":
                left_rem += 1
            elif ch == ")":
                if left_rem:
                    left_rem -= 1
                else:
                    right_rem += 1

        ans: Set[str] = set()

        def dfs(i: int, left_r: int, right_r: int, bal: int, path: List[str]) -> None:
            if i == len(s):
                if left_r == 0 and right_r == 0 and bal == 0:
                    ans.add("".join(path))
                return
            ch = s[i]
            if ch == "(" and left_r > 0:
                dfs(i + 1, left_r - 1, right_r, bal, path)
            if ch == ")" and right_r > 0:
                dfs(i + 1, left_r, right_r - 1, bal, path)
            path.append(ch)
            if ch != "(" and ch != ")":
                dfs(i + 1, left_r, right_r, bal, path)
            elif ch == "(":
                dfs(i + 1, left_r, right_r, bal + 1, path)
            elif bal > 0:
                dfs(i + 1, left_r, right_r, bal - 1, path)
            path.pop()

        dfs(0, left_rem, right_rem, 0, [])
        return list(ans)
# @lc code=end

