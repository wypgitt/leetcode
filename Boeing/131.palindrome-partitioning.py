"""
Approach: Backtracking over cut positions with a precomputed palindrome table.
Data structure: pal[i][j] stores whether s[i:j+1] is a palindrome, turning repeated checks into O(1) lookups.
Interview logic: every answer is a sequence of cuts. DFS enumerates those cuts left to right and only recurses through palindromic pieces.
Complexity: O(n^2 + n*2^n) time including output size, O(n^2) space.
Tests and edge cases: single characters are always valid; repeated characters produce many partitions; reaching index n emits one complete partition.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def partition(self, s: str) -> List[List[str]]:
        n = len(s)
        pal = [[False] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])
        ans, path = [], []
        def dfs(start: int) -> None:
            if start == n:
                ans.append(path[:])
                return
            for end in range(start, n):
                if pal[start][end]:
                    path.append(s[start:end + 1])
                    dfs(end + 1)
                    path.pop()
        dfs(0)
        return ans
# @lc code=end
