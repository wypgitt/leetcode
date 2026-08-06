#
# @lc app=leetcode id=3237 lang=python3
#
# [3237] Alt and Tab Simulation
#
# https://leetcode.com/problems/alt-and-tab-simulation/description/
#
# algorithms
# Medium (53.75%)
# Likes:    15
# Dislikes: 6
# Total Accepted:    1.3K
# Total Submissions: 2.4K
# Testcase Example:  "[1,2,3]\n[3,3,2]"
#
#
# There are n windows open numbered from 1 to n, we want to simulate using
# alt + tab to navigate between the windows.
#
# You are given an array windows which contains the initial order of the
# windows (the first element is at the top and the last one is at the
# bottom).
#
# You are also given an array queries where for each query, the window
# queries[i] is brought to the top.
#
# Return the final state of the array windows.
#
# Example 1:
#
# Input: windows = [1,2,3], queries = [3,3,2]
#
# Output: [2,3,1]
#
# Explanation:
#
# Here is the window array after each query:
#
# Initial order: [1,2,3]
#
# After the first query: [3,1,2]
#
# After the second query: [3,1,2]
#
# After the last query: [2,3,1]
#
# Example 2:
#
# Input: windows = [1,4,2,3], queries = [4,1,3]
#
# Output: [3,1,4,2]
#
# Explanation:
#
# Here is the window array after each query:
#
# Initial order: [1,4,2,3]
#
# After the first query: [4,1,2,3]
#
# After the second query: [1,4,2,3]
#
# After the last query: [3,1,4,2]
#
# Constraints:
#
# 1 <= n == windows.length <= 10^5
#
# windows is a permutation of [1, n].
#
# 1 <= queries.length <= 10^5
#
# 1 <= queries[i] <= n
#

# @lc code=start
from typing import List


class Solution:
    def simulationResult(self, windows: List[int], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        Each query brings that window to the front. The final order is the unique
        queried windows in reverse-query order, then never-queried windows in
        their original relative order.

        Algorithm:
        - Walk queries from back to front; append each window the first time seen.
        - Append remaining windows from the original list in order.

        Complexity: O(n + q) time, O(n) space.
        Alternate: simulate with a linked list / deque (slower but direct).
        """
        seen = set()
        result: List[int] = []
        for q in reversed(queries):
            if q not in seen:
                seen.add(q)
                result.append(q)
        for w in windows:
            if w not in seen:
                result.append(w)
        return result

# @lc code=end
