#
# @lc app=leetcode id=1553 lang=python3
#
# [1553] Minimum Number of Days to Eat N Oranges
#
# https://leetcode.com/problems/minimum-number-of-days-to-eat-n-oranges/description/
#
# algorithms
# Hard (36.36%)
# Likes:    1039
# Dislikes: 65
# Total Accepted:    45.6K
# Total Submissions: 125K
# Testcase Example:  "10"
#
# There are n oranges in the kitchen and you decided to eat some of these
# oranges every day as follows:
#
# Eat one orange.
#
# If the number of remaining oranges n is divisible by 2 then you can eat n / 2
# oranges.
#
# If the number of remaining oranges n is divisible by 3 then you can eat 2 *
# (n / 3) oranges.
#
# You can only choose one of the actions per day.
#
# Given the integer n, return the minimum number of days to eat n oranges.
#
# Example 1:
#
# Input: n = 10
# Output: 4
# Explanation: You have 10 oranges.
# Day 1: Eat 1 orange, 10 - 1 = 9.
# Day 2: Eat 6 oranges, 9 - 2*(9/3) = 9 - 6 = 3. (Since 9 is divisible by 3)
# Day 3: Eat 2 oranges, 3 - 2*(3/3) = 3 - 2 = 1.
# Day 4: Eat the last orange 1 - 1 = 0.
# You need at least 4 days to eat the 10 oranges.
#
# Example 2:
#
# Input: n = 6
# Output: 3
# Explanation: You have 6 oranges.
# Day 1: Eat 3 oranges, 6 - 6/2 = 6 - 3 = 3. (Since 6 is divisible by 2).
# Day 2: Eat 2 oranges, 3 - 2*(3/3) = 3 - 2 = 1. (Since 3 is divisible by 3)
# Day 3: Eat the last orange 1 - 1 = 0.
# You need at least 3 days to eat the 6 oranges.
#
# Constraints:
#
# 1 <= n <= 2 * 10^9
#

# @lc code=start
from functools import lru_cache


class Solution:
    def minDays(self, n: int) -> int:
        """
        Interview explanation:
        Each day eat 1, or n/2 if even, or 2n/3 if divisible by 3. Optimal path
        rarely eats many 1s: jump toward nearest multiple of 2/3 via eating 1s,
        then divide. Memoized recursion / BFS from n.

        Algorithm (memo DFS):
        - dp(0)=0, dp(1)=1.
        - dp(x)=1+min(x%2+dp(x//2), x%3+dp(x//3)) — eat leftovers then divide.

        Complexity: O(log^2 n) states typical; each O(1). Space O(#states).
        """
        @lru_cache(None)
        def dp(x: int) -> int:
            if x <= 1:
                return x
            return 1 + min(x % 2 + dp(x // 2), x % 3 + dp(x // 3))

        return dp(n)

    def minDays_bfs(self, n: int) -> int:
        """
        Interview explanation:
        Alternate BFS from n toward 0 applying reverse-friendly moves: -1,
        /2 if even, /3 if %3==0. First time reaching 0 is min days.

        Algorithm (BFS):
        - Queue from n; visit set; level-order until 0.

        Complexity: O(n) worst-case states, usually much smaller.
        """
        from collections import deque
        if n <= 1:
            return n
        q = deque([n])
        seen = {n}
        days = 0
        while q:
            for _ in range(len(q)):
                x = q.popleft()
                if x == 0:
                    return days
                for y in (x - 1,):
                    if y not in seen and y >= 0:
                        seen.add(y)
                        q.append(y)
                if x % 2 == 0 and x // 2 not in seen:
                    seen.add(x // 2)
                    q.append(x // 2)
                if x % 3 == 0 and x // 3 not in seen:
                    seen.add(x // 3)
                    q.append(x // 3)
            days += 1
        return days
# @lc code=end

