#
# @lc app=leetcode id=1801 lang=python3
#
# [1801] Number of Orders in the Backlog
#
# https://leetcode.com/problems/number-of-orders-in-the-backlog/description/
#
# algorithms
# Medium (54.19%)
# Likes:    350
# Dislikes: 246
# Total Accepted:    39.6K
# Total Submissions: 73.0K
# Testcase Example:  "[[10,5,0],[15,2,1],[25,1,1],[30,4,0]]"
#
# You are given a 2D integer array orders, where each orders[i] = [price_i,
# amount_i, orderType_i] denotes that amount_i_ orders have been placed of type
# orderType_i at the price price_i. The orderType_i is:
#
# 0 if it is a batch of buy orders, or
#
# 1 if it is a batch of sell orders.
#
# Note that orders[i] represents a batch of amount_i independent orders with
# the same price and order type. All orders represented by orders[i] will be
# placed before all orders represented by orders[i+1] for all valid i.
#
# There is a backlog that consists of orders that have not been executed. The
# backlog is initially empty. When an order is placed, the following happens:
#
# If the order is a buy order, you look at the sell order with the smallest
# price in the backlog. If that sell order's price is smaller than or equal to
# the current buy order's price, they will match and be executed, and that sell
# order will be removed from the backlog. Else, the buy order is added to the
# backlog.
#
# Vice versa, if the order is a sell order, you look at the buy order with the
# largest price in the backlog. If that buy order's price is larger than or
# equal to the current sell order's price, they will match and be executed, and
# that buy order will be removed from the backlog. Else, the sell order is
# added to the backlog.
#
# Return the total amount of orders in the backlog after placing all the orders
# from the input. Since this number can be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: orders = [[10,5,0],[15,2,1],[25,1,1],[30,4,0]]
# Output: 6
# Explanation: Here is what happens with the orders:
# - 5 orders of type buy with price 10 are placed. There are no sell orders, so
# the 5 orders are added to the backlog.
# - 2 orders of type sell with price 15 are placed. There are no buy orders
# with prices larger than or equal to 15, so the 2 orders are added to the
# backlog.
# - 1 order of type sell with price 25 is placed. There are no buy orders with
# prices larger than or equal to 25 in the backlog, so this order is added to
# the backlog.
# - 4 orders of type buy with price 30 are placed. The first 2 orders are
# matched with the 2 sell orders of the least price, which is 15 and these 2
# sell orders are removed from the backlog. The 3^rd order is matched with the
# sell order of the least price, which is 25 and this sell order is removed
# from the backlog. Then, there are no more sell orders in the backlog, so the
# 4^th order is added to the backlog.
# Finally, the backlog has 5 buy orders with price 10, and 1 buy order with
# price 30. So the total number of orders in the backlog is 6.
#
# Example 2:
#
# Input: orders = [[7,1000000000,1],[15,3,0],[5,999999995,0],[5,1,1]]
# Output: 999999984
# Explanation: Here is what happens with the orders:
# - 10^9 orders of type sell with price 7 are placed. There are no buy orders,
# so the 10^9 orders are added to the backlog.
# - 3 orders of type buy with price 15 are placed. They are matched with the 3
# sell orders with the least price which is 7, and those 3 sell orders are
# removed from the backlog.
# - 999999995 orders of type buy with price 5 are placed. The least price of a
# sell order is 7, so the 999999995 orders are added to the backlog.
# - 1 order of type sell with price 5 is placed. It is matched with the buy
# order of the highest price, which is 5, and that buy order is removed from
# the backlog.
# Finally, the backlog has (1000000000-3) sell orders with price 7, and
# (999999995-1) buy orders with price 5. So the total number of orders =
# 1999999991, which is equal to 999999984 % (10^9 + 7).
#
# Constraints:
#
# 1 <= orders.length <= 10^5
#
# orders[i].length == 3
#
# 1 <= price_i, amount_i <= 10^9
#
# orderType_i is either 0 or 1.
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def getNumberOfBacklogOrders(self, orders: List[List[int]]) -> int:
        """
        Interview explanation:
        Match buy/sell against opposite backlog: buys take cheapest sell <= price;
        sells take most expensive buy >= price. Unmatched amount stays in backlog.
        Use two heaps for best opposite prices.

        Algorithm (two heaps):
        - sell min-heap (price, amount); buy max-heap (-price, amount).
        - For each order, greedily match while amounts remain and prices cross;
          push remainder to the appropriate heap.
        - Sum remaining amounts mod 10^9+7.

        Complexity: O(n log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        buy, sell = [], []  # buy: (-price, amt); sell: (price, amt)
        for price, amount, typ in orders:
            if typ == 0:  # buy
                while amount and sell and sell[0][0] <= price:
                    sp, sa = heapq.heappop(sell)
                    used = min(amount, sa)
                    amount -= used
                    sa -= used
                    if sa:
                        heapq.heappush(sell, (sp, sa))
                if amount:
                    heapq.heappush(buy, (-price, amount))
            else:  # sell
                while amount and buy and -buy[0][0] >= price:
                    bp, ba = heapq.heappop(buy)
                    used = min(amount, ba)
                    amount -= used
                    ba -= used
                    if ba:
                        heapq.heappush(buy, (bp, ba))
                if amount:
                    heapq.heappush(sell, (price, amount))
        return (sum(a for _, a in buy) + sum(a for _, a in sell)) % MOD
# @lc code=end
