#
# @lc app=leetcode id=1215 lang=python3
#
# [1215] Stepping Numbers
#
# https://leetcode.com/problems/stepping-numbers/description/
#
# algorithms
# Medium (48.62%)
# Likes:    188
# Dislikes: 21
# Total Accepted:    11.5K
# Total Submissions: 23.6K
# Testcase Example:  "0\n21"
#
#
# A stepping number is an integer such that all of its adjacent digits
# have an absolute difference of exactly 1.
#
# For example, 321 is a stepping number while 421 is not.
#
# Given two integers low and high, return a sorted list of all the
# stepping numbers in the inclusive range [low, high].
#
# Example 1:
#
# Input: low = 0, high = 21
# Output: [0,1,2,3,4,5,6,7,8,9,10,12,21]
#
# Example 2:
#
# Input: low = 10, high = 15
# Output: [10,12]
#
# Constraints:
#
# 0 <= low <= high <= 2 * 10^9
#
# @lc code=start
from typing import List
from collections import deque

class Solution:
    def countSteppingNumbers(self, low: int, high: int) -> List[int]:
        """
        Interview explanation:
        Premium. Stepping number: adjacent digits differ by 1. BFS from 1..9
        appending last±1 digits; collect numbers in [low, high]. Include 0 if
        in range.

        Algorithm:
        - Queue seed 1..9 (and 0 separately); while queue: if in range append;
          append next = cur*10 + d for d in {last-1,last+1} if valid and <=high

        Complexity: O(#stepping <= high) ~ O(high digits).
        """
        ans = []
        if low == 0:
            ans.append(0)
        q = deque(range(1, 10))
        while q:
            cur = q.popleft()
            if cur > high:
                continue
            if cur >= low:
                ans.append(cur)
            last = cur % 10
            for d in (last - 1, last + 1):
                if 0 <= d <= 9:
                    nxt = cur * 10 + d
                    if nxt <= high:
                        q.append(nxt)
        return ans

    def countSteppingNumbers_dfs(self, low: int, high: int) -> List[int]:
        """
        Interview explanation:
        Alternate DFS from each seed digit building stepping numbers.

        Algorithm:
        - DFS(cur): if in [low,high] collect; recurse cur*10+last±1 if <=high

        Complexity: Same order as BFS.
        """
        ans = []
        if low == 0:
            ans.append(0)

        def dfs(cur: int) -> None:
            if cur > high:
                return
            if cur >= low:
                ans.append(cur)
            last = cur % 10
            for d in (last - 1, last + 1):
                if 0 <= d <= 9:
                    dfs(cur * 10 + d)

        for i in range(1, 10):
            dfs(i)
        ans.sort()
        return ans
# @lc code=end
