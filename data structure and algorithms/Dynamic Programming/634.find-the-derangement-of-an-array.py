#
# @lc app=leetcode id=634 lang=python3
#
# [634] Find the Derangement of An Array
#
# https://leetcode.com/problems/find-the-derangement-of-an-array/description/
#
# algorithms
# Medium (41.67%)
# Likes:    223
# Dislikes: 167
# Total Accepted:    12.6K
# Total Submissions: 30.3K
# Testcase Example:  '3'
#
# In combinatorial mathematics, a derangement is a permutation of the elements
# of a set, such that no element appears in its original position.
# 
# You are given an integer n. There is originally an array consisting of n
# integers from 1 to n in ascending order, return the number of derangements it
# can generate. Since the answer may be huge, return it modulo 10^9 + 7.
# 
# 
# Example 1:
# 
# 
# Input: n = 3
# Output: 2
# Explanation: The original array is [1,2,3]. The two derangements are [2,3,1]
# and [3,1,2].
# 
# 
# Example 2:
# 
# 
# Input: n = 2
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^6
# 
# 
#

# @lc code=start
class Solution:
    def findDerangement(self, n: int) -> int:
        MOD = 10 ** 9 + 7
        if n == 1:
            return 0
        prev2, prev1 = 1, 0  # D(0), D(1)
        for i in range(2, n + 1):
            cur = (i - 1) * (prev1 + prev2) % MOD
            prev2, prev1 = prev1, cur
        return prev1
# @lc code=end

"""
Interview explanation:
For derangements, D(n) = (n-1) * (D(n-1) + D(n-2)). Consider where item 1 goes: choose one of n-1 positions. If the displaced item goes to position 1, the remaining n-2 items are deranged; otherwise the problem reduces to deranging n-1 items with a paired constraint.

Data structure: only the previous two DP values are needed.

Edge cases: D(1)=0 and D(0)=1 is the recurrence base.

Complexity: O(n) time and O(1) space, with all operations modulo 1e9+7.
"""
