#
# @lc app=leetcode id=502 lang=python3
#
# [502] IPO
#
# https://leetcode.com/problems/ipo/description/
#
# algorithms
# Hard (53.7%)
# Likes:    4243
# Dislikes: 286
# Total Accepted:    332K
# Total Submissions: 618K
# Testcase Example:  "2"
#
# Suppose LeetCode will start its IPO soon. In order to sell a good price of
# its shares to Venture Capital, LeetCode would like to work on some projects
# to increase its capital before the IPO. Since it has limited resources, it
# can only finish at most k distinct projects before the IPO. Help LeetCode
# design the best way to maximize its total capital after finishing at most k
# distinct projects.
#
# You are given n projects where the i^th project has a pure profit profits[i]
# and a minimum capital of capital[i] is needed to start it.
#
# Initially, you have w capital. When you finish a project, you will obtain its
# pure profit and the profit will be added to your total capital.
#
# Pick a list of at most k distinct projects from given projects to maximize
# your final capital, and return the final maximized capital.
#
# The answer is guaranteed to fit in a 32-bit signed integer.
#
# Example 1:
#
# Input: k = 2, w = 0, profits = [1,2,3], capital = [0,1,1]
# Output: 4
# Explanation: Since your initial capital is 0, you can only start the project
# indexed 0.
# After finishing it you will obtain profit 1 and your capital becomes 1.
# With capital 1, you can either start the project indexed 1 or the project
# indexed 2.
# Since you can choose at most 2 projects, you need to finish the project
# indexed 2 to get the maximum capital.
# Therefore, output the final maximized capital, which is 0 + 1 + 3 = 4.
#
# Example 2:
#
# Input: k = 3, w = 0, profits = [1,2,3], capital = [0,1,2]
# Output: 6
#
# Constraints:
#
# 1 <= k <= 10^5
#
# 0 <= w <= 10^9
#
# n == profits.length
#
# n == capital.length
#
# 1 <= n <= 10^5
#
# 0 <= profits[i] <= 10^4
#
# 0 <= capital[i] <= 10^9
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def findMaximizedCapital(
        self, k: int, w: int, profits: List[int], capital: List[int]
    ) -> int:
        """
        Interview explanation:
        Greedy with two heaps: projects sorted by capital requirement; a max-heap
        of profits for currently affordable projects. Each of k rounds: unlock
        all projects with capital ≤ w into the profit heap; take the best profit.

        Algorithm:
        - Sort projects by capital; i = 0; max-heap of profits.
        - Repeat k times: while i < n and capital[i] <= w: push profit; i++.
          If heap empty: break; else w += -heappop.

        Complexity: O(n log n) time, O(n) space.
        """
        projects = sorted(zip(capital, profits))
        i = 0
        n = len(projects)
        max_profit: List[int] = []
        for _ in range(k):
            while i < n and projects[i][0] <= w:
                heapq.heappush(max_profit, -projects[i][1])
                i += 1
            if not max_profit:
                break
            w += -heapq.heappop(max_profit)
        return w
# @lc code=end
