#
# @lc app=leetcode id=77 lang=python3
#
# [77] Combinations
#
# https://leetcode.com/problems/combinations/description/
#
# algorithms
# Medium (74.54%)
# Likes:    8938
# Dislikes: 256
# Total Accepted:    1.3M
# Total Submissions: 1.8M
# Testcase Example:  '4\n2'
#
# Given two integers n and k, return all possible combinations of k numbers
# chosen from the range [1, n].
# 
# You may return the answer in any order.
# 
# 
# Example 1:
# 
# 
# Input: n = 4, k = 2
# Output: [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
# Explanation: There are 4 choose 2 = 6 total combinations.
# Note that combinations are unordered, i.e., [1,2] and [2,1] are considered to
# be the same combination.
# 
# 
# Example 2:
# 
# 
# Input: n = 1, k = 1
# Output: [[1]]
# Explanation: There is 1 choose 1 = 1 total combination.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 20
# 1 <= k <= n
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def combine(self, n: int, k: int) -> List[List[int]]:
        """
        Interview explanation:
        Build combinations in increasing order with backtracking. The start
        parameter prevents reusing earlier numbers and avoids duplicate orders.
        Pruning stops when there are not enough remaining numbers to fill k.

        Edge cases and tests:
        - k=1 returns each number alone.
        - k=n returns one combination containing all numbers.
        - Pruning keeps recursion focused on feasible prefixes.

        Complexity: O(C(n,k) * k) time for output copies, O(k) recursion space.
        """
        ans = []
        path = []

        def dfs(start: int) -> None:
            if len(path) == k:
                ans.append(path.copy())
                return
            need = k - len(path)
            for value in range(start, n - need + 2):
                path.append(value)
                dfs(value + 1)
                path.pop()

        dfs(1)
        return ans
# @lc code=end


