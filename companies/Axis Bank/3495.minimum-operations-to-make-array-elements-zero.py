#
# @lc app=leetcode id=3495 lang=python3
#
# [3495] Minimum Operations to Make Array Elements Zero
#
# https://leetcode.com/problems/minimum-operations-to-make-array-elements-zero/description/
#
# algorithms
# Hard (60.34%)
# Likes:    387
# Dislikes: 54
# Total Accepted:    79.7K
# Total Submissions: 132.1K
# Testcase Example:  "[[1,2],[2,4]]"
#
#
# You are given a 2D array queries, where queries[i] is of the form [l,
# r]. Each queries[i] defines an array of integers nums consisting of
# elements ranging from l to r, both inclusive.
#
# In one operation, you can:
#
# Select two integers a and b from the array.
#
# Replace them with floor(a / 4) and floor(b / 4).
#
# Your task is to determine the minimum number of operations required to
# reduce all elements of the array to zero for each query. Return the sum
# of the results for all queries.
#
# Example 1:
#
# Input: queries = [[1,2],[2,4]]
#
# Output: 3
#
# Explanation:
#
# For queries[0]:
#
# The initial array is nums = [1, 2].
#
# In the first operation, select nums[0] and nums[1]. The array becomes
# [0, 0].
#
# The minimum number of operations required is 1.
#
# For queries[1]:
#
# The initial array is nums = [2, 3, 4].
#
# In the first operation, select nums[0] and nums[2]. The array becomes
# [0, 3, 1].
#
# In the second operation, select nums[1] and nums[2]. The array becomes
# [0, 0, 0].
#
# The minimum number of operations required is 2.
#
# The output is 1 + 2 = 3.
#
# Example 2:
#
# Input: queries = [[2,6]]
#
# Output: 4
#
# Explanation:
#
# For queries[0]:
#
# The initial array is nums = [2, 3, 4, 5, 6].
#
# In the first operation, select nums[0] and nums[3]. The array becomes
# [0, 3, 4, 1, 6].
#
# In the second operation, select nums[2] and nums[4]. The array becomes
# [0, 3, 1, 1, 1].
#
# In the third operation, select nums[1] and nums[2]. The array becomes
# [0, 0, 0, 1, 1].
#
# In the fourth operation, select nums[3] and nums[4]. The array becomes
# [0, 0, 0, 0, 0].
#
# The minimum number of operations required is 4.
#
# The output is 4.
#
# Constraints:
#
# 1 <= queries.length <= 10^5
#
# queries[i].length == 2
#
# queries[i] == [l, r]
#
# 1 <= l < r <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, queries: List[List[int]]) -> int:
        """
        Interview explanation:
        An op replaces two numbers a,b with floor(a/4), floor(b/4). Number x
        needs p = floor(log4 x)+1 ops on itself. For a range, if total needed
        ops sum to S and max is M, answer is max(ceil(S/2), M) — pair ops, but
        cannot finish faster than the heaviest element.

        Algorithm:
        - f(x) = sum of op-needs over [1..x] via power-of-4 buckets.
        - For [l,r]: S = f(r)-f(l-1), M = f(r)-f(r-1); add max((S+1)//2, M).

        Complexity: O(q log R) time, O(1) space.
        """

        def f(x: int) -> int:
            if x <= 0:
                return 0
            res = 0
            p = 1
            i = 1
            while p <= x:
                cnt = min(p * 4 - 1, x) - p + 1
                res += cnt * i
                i += 1
                p *= 4
            return res

        ans = 0
        for l, r in queries:
            s = f(r) - f(l - 1)
            mx = f(r) - f(r - 1)
            ans += max((s + 1) // 2, mx)
        return ans
# @lc code=end
