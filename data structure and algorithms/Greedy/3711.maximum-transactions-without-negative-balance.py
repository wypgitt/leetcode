#
# @lc app=leetcode id=3711 lang=python3
#
# [3711] Maximum Transactions Without Negative Balance
#
# https://leetcode.com/problems/maximum-transactions-without-negative-balance/description/
#
# algorithms
# Medium (46.06%)
# Likes:    10
# Dislikes: 1
# Total Accepted:    818
# Total Submissions: 1.8K
# Testcase Example:  "[2,-5,3,-1,-2]"
#
#
# You are given an integer array transactions, where transactions[i]
# represents the amount of the i^th transaction:
#
# A positive value means money is received.
#
# A negative value means money is sent.
#
# The account starts with a balance of 0, and the balance must never
# become negative. Transactions must be considered in the given order, but
# you are allowed to skip some transactions.
#
# Return an integer denoting the maximum number of transactions that can
# be performed without the balance ever going negative.
#
# Example 1:
#
# Input: transactions = [2,-5,3,-1,-2]
#
# Output: 4
#
# Explanation:
#
# One optimal sequence is [2, 3, -1, -2], balance: 0 → 2 → 5 → 4 → 2.
#
# Example 2:
#
# Input: transactions = [-1,-2,-3]
#
# Output: 0
#
# Explanation:
#
# All transactions are negative. Including any would make the balance
# negative.
#
# Example 3:
#
# Input: transactions = [3,-2,3,-2,1,-1]
#
# Output: 6
#
# Explanation:
#
# All transactions can be taken in order, balance: 0 → 3 → 1 → 4 → 2 → 3 →
# 2.
#
# Constraints:
#
# 1 <= transactions.length <= 10^5
#
# -10^9 <= transactions[i] <= 10^9
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def maxTransactions(self, transactions: List[int]) -> int:
        """
        Interview explanation:
        Take transactions in order; if balance goes negative, drop the most
        negative taken debit (greedy) to restore feasibility.

        Algorithm:
        - Maintain running balance and a min-heap of chosen negative amounts.
        - Always include the next transaction; if balance < 0, undo the smallest
          (most negative) chosen debit via the heap.

        Complexity: O(n log n) time, O(n) space.
        """
        bal = 0
        heap: List[int] = []
        taken = 0
        for t in transactions:
            bal += t
            taken += 1
            if t < 0:
                heapq.heappush(heap, t)
            if bal < 0:
                worst = heapq.heappop(heap)
                bal -= worst
                taken -= 1
        return taken
# @lc code=end
