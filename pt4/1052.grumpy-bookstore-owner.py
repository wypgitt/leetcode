#
# @lc app=leetcode id=1052 lang=python3
#
# [1052] Grumpy Bookstore Owner
#
# https://leetcode.com/problems/grumpy-bookstore-owner/description/
#
# algorithms
# Medium (64.01%)
# Likes:    2724
# Dislikes: 265
# Total Accepted:    239.2K
# Total Submissions: 373.6K
# Testcase Example:  '[1,0,1,2,1,1,7,5]\n[0,1,0,1,0,1,0,1]\n3'
#
# There is a bookstore owner that has a store open for n minutes. You are given
# an integer array customers of length n where customers[i] is the number of
# the customers that enter the store at the start of the i^th minute and all
# those customers leave after the end of that minute.
# 
# During certain minutes, the bookstore owner is grumpy. You are given a binary
# array grumpy where grumpy[i] is 1 if the bookstore owner is grumpy during the
# i^th minute, and is 0 otherwise.
# 
# When the bookstore owner is grumpy, the customers entering during that minute
# are not satisfied. Otherwise, they are satisfied.
# 
# The bookstore owner knows a secret technique to remain not grumpy for minutes
# consecutive minutes, but this technique can only be used once.
# 
# Return the maximum number of customers that can be satisfied throughout the
# day.
# 
# 
# Example 1:
# 
# 
# Input: customers = [1,0,1,2,1,1,7,5], grumpy = [0,1,0,1,0,1,0,1], minutes =
# 3
# 
# Output: 16
# 
# Explanation:
# 
# The bookstore owner keeps themselves not grumpy for the last 3 minutes.
# 
# The maximum number of customers that can be satisfied = 1 + 1 + 1 + 1 + 7 + 5
# = 16.
# 
# 
# Example 2:
# 
# 
# Input: customers = [1], grumpy = [0], minutes = 1
# 
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# n == customers.length == grumpy.length
# 1 <= minutes <= n <= 2 * 10^4
# 0 <= customers[i] <= 1000
# grumpy[i] is either 0 or 1.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def maxSatisfied(self, customers: List[int], grumpy: List[int], minutes: int) -> int:
        always_satisfied = 0
        extra_satisfied = 0
        best_extra = 0

        for i, count in enumerate(customers):
            if grumpy[i] == 0:
                always_satisfied += count
            else:
                extra_satisfied += count

            if i >= minutes and grumpy[i - minutes] == 1:
                extra_satisfied -= customers[i - minutes]

            best_extra = max(best_extra, extra_satisfied)

        return always_satisfied + best_extra
# @lc code=end

"""
Interview Explanation

Core idea:
Customers during non-grumpy minutes are already satisfied. The secret technique
only adds value during grumpy minutes, so we need the length-minutes window
with the largest number of otherwise-unsatisfied customers.

Algorithm:
1. Sum customers where grumpy[i] == 0 into always_satisfied.
2. Slide a window of size minutes across the array.
3. The window gain only includes customers where grumpy[i] == 1.
4. Add the best gain to always_satisfied.

Data structure choice:
A sliding window is perfect because all candidate technique intervals have the
same fixed length. It updates the gain in O(1) as the right side moves.

Correctness:
The technique can be used once for exactly minutes consecutive positions.
For any chosen interval, the only additional satisfied customers are grumpy
customers inside that interval; non-grumpy customers were already counted.
The sliding window evaluates the gain for every possible interval and chooses
the maximum, so the final total is optimal.

Complexity:
Time is O(n), and space is O(1).

Tests and edge cases:
- minutes == n: all customers can be satisfied.
- No grumpy minutes: best_extra stays 0.
- All grumpy minutes: answer is the maximum sum window of length minutes.
- Single minute input works with the same logic.
"""
