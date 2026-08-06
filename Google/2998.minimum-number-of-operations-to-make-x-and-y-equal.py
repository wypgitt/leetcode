#
# @lc app=leetcode id=2998 lang=python3
#
# [2998] Minimum Number of Operations to Make X and Y Equal
#
# https://leetcode.com/problems/minimum-number-of-operations-to-make-x-and-y-equal/description/
#
# algorithms
# Medium (48.95%)
# Likes:    292
# Dislikes: 23
# Total Accepted:    29.8K
# Total Submissions: 60.8K
# Testcase Example:  "26\n1"
#
#
# You are given two positive integers x and y.
#
# In one operation, you can do one of the four following operations:
#
# Divide x by 11 if x is a multiple of 11.
#
# Divide x by 5 if x is a multiple of 5.
#
# Decrement x by 1.
#
# Increment x by 1.
#
# Return the minimum number of operations required to make  x and y equal.
#
# Example 1:
#
# Input: x = 26, y = 1
# Output: 3
# Explanation: We can make 26 equal to 1 by applying the following
# operations:
# 1. Decrement x by 1
# 2. Divide x by 5
# 3. Divide x by 5
# It can be shown that 3 is the minimum number of operations required to
# make 26 equal to 1.
#
# Example 2:
#
# Input: x = 54, y = 2
# Output: 4
# Explanation: We can make 54 equal to 2 by applying the following
# operations:
# 1. Increment x by 1
# 2. Divide x by 11
# 3. Divide x by 5
# 4. Increment x by 1
# It can be shown that 4 is the minimum number of operations required to
# make 54 equal to 2.
#
# Example 3:
#
# Input: x = 25, y = 30
# Output: 5
# Explanation: We can make 25 equal to 30 by applying the following
# operations:
# 1. Increment x by 1
# 2. Increment x by 1
# 3. Increment x by 1
# 4. Increment x by 1
# 5. Increment x by 1
# It can be shown that 5 is the minimum number of operations required to
# make 25 equal to 30.
#
# Constraints:
#
# 1 <= x, y <= 10^4
#

# @lc code=start

from collections import deque
from functools import cache


class Solution:
    def minimumOperationsToMakeEqual(self, x: int, y: int) -> int:
        """
        Interview explanation:
        From x reach y with: /11 if divisible, /5 if divisible, +1, -1.
        Divisions shrink toward smaller values; BFS on a bounded range.

        Algorithm:
        - BFS from x; enqueue x±1 and x/5, x/11 when divisible; stop at y.
          Bound search to a modest window above max(x,y).

        Complexity: O(R) time/space for search radius R ~ O(max(x,y)).
        """
        if x == y:
            return 0
        if y > x:
            return y - x
        limit = x + 11
        dist = {x: 0}
        q = deque([x])
        while q:
            cur = q.popleft()
            d = dist[cur]
            if cur == y:
                return d
            for nxt in (cur + 1, cur - 1):
                if 1 <= nxt <= limit and nxt not in dist:
                    dist[nxt] = d + 1
                    q.append(nxt)
            if cur % 5 == 0:
                nxt = cur // 5
                if nxt not in dist:
                    dist[nxt] = d + 1
                    q.append(nxt)
            if cur % 11 == 0:
                nxt = cur // 11
                if nxt not in dist:
                    dist[nxt] = d + 1
                    q.append(nxt)
        return abs(x - y)

    def minimumOperationsToMakeEqual_memo(self, x: int, y: int) -> int:
        """
        Interview explanation:
        Alternate memo DFS: either walk down to y by -1, or adjust to nearest
        multiple of 5/11 then divide and recurse.

        Algorithm:
        - dfs(x): if y>=x return y-x; else min of (x-y) and four
          adjust-then-divide branches for 5 and 11.

        Complexity: O(x) states with caching.
        """

        @cache
        def dfs(v: int) -> int:
            if y >= v:
                return y - v
            ans = v - y
            ans = min(ans, v % 5 + 1 + dfs(v // 5))
            ans = min(ans, 5 - v % 5 + 1 + dfs(v // 5 + 1))
            ans = min(ans, v % 11 + 1 + dfs(v // 11))
            ans = min(ans, 11 - v % 11 + 1 + dfs(v // 11 + 1))
            return ans

        return dfs(x)
# @lc code=end
