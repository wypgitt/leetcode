#
# @lc app=leetcode id=3822 lang=python3
#
# [3822] Design Order Management System
#
# https://leetcode.com/problems/design-order-management-system/description/
#
# algorithms
# Medium (78.59%)
# Likes:    8
# Dislikes: 1
# Total Accepted:    1.8K
# Total Submissions: 2.2K
# Testcase Example:  "[\"OrderManagementSystem\",\"addOrder\",\"addOrder\",\"addOrder\",\"getOrdersAtPrice\",\"modifyOrder\",\"modifyOrder\",\"getOrdersAtPrice\",\"cancelOrder\",\"cancelOrder\",\"getOrdersAtPrice\"]\n[[],[1,\"buy\",1],[2,\"buy\",1],[3,\"sell\",2],[\"buy\",1],[1,3],[2,1],[\"buy\",1],[3],[2],[\"buy\",1]]"
#
#
# You are asked to design a simple order management system for a trading
# platform.
#
# Each order is associated with an orderId, an orderType ("buy" or
# "sell"), and a price.
#
# An order is considered active unless it is canceled.
#
# Implement the OrderManagementSystem class:
#
# OrderManagementSystem(): Initializes the order management system.
#
# void addOrder(int orderId, string orderType, int price): Adds a new
# active order with the given attributes. It is guaranteed that orderId is
# unique.
#
# void modifyOrder(int orderId, int newPrice): Modifies the price of an
# existing order. It is guaranteed that the order exists and is active.
#
# void cancelOrder(int orderId): Cancels an existing order. It is
# guaranteed that the order exists and is active.
#
# vector<int> getOrdersAtPrice(string orderType, int price): Returns the
# orderIds of all active orders that match the given orderType and price.
# If no such orders exist, return an empty list.
#
# Note: The order of returned orderIds does not matter.
#
# Example 1:
#
# Input:
#
# ["OrderManagementSystem", "addOrder", "addOrder", "addOrder",
# "getOrdersAtPrice", "modifyOrder", "modifyOrder", "getOrdersAtPrice",
# "cancelOrder", "cancelOrder", "getOrdersAtPrice"]
#
# [[], [1, "buy", 1], [2, "buy", 1], [3, "sell", 2], ["buy", 1], [1, 3],
# [2, 1], ["buy", 1], [3], [2], ["buy", 1]]
#
# Output:
#
# [null, null, null, null, [2, 1], null, null, [2], null, null, []]
#
# Explanation
#
# OrderManagementSystem orderManagementSystem = new
# OrderManagementSystem();
#
# orderManagementSystem.addOrder(1, "buy", 1); // A buy order with ID 1 is
# added at price 1.
#
# orderManagementSystem.addOrder(2, "buy", 1); // A buy order with ID 2 is
# added at price 1.
#
# orderManagementSystem.addOrder(3, "sell", 2); // A sell order with ID 3
# is added at price 2.
#
# orderManagementSystem.getOrdersAtPrice("buy", 1); // Both buy orders
# (IDs 1 and 2) are active at price 1, so the result is [2, 1].
#
# orderManagementSystem.modifyOrder(1, 3); // Order 1 is updated: its
# price becomes 3.
#
# orderManagementSystem.modifyOrder(2, 1); // Order 2 is updated, but its
# price remains 1.
#
# orderManagementSystem.getOrdersAtPrice("buy", 1); // Only order 2 is
# still an active buy order at price 1, so the result is [2].
#
# orderManagementSystem.cancelOrder(3); // The sell order with ID 3 is
# canceled and removed from active orders.
#
# orderManagementSystem.cancelOrder(2); // The buy order with ID 2 is
# canceled and removed from active orders.
#
# orderManagementSystem.getOrdersAtPrice("buy", 1); // There are no active
# buy orders left at price 1, so the result is [].
#
# Constraints:
#
# 1 <= orderId <= 2000
#
# orderId is unique across all orders.
#
# orderType is either "buy" or "sell".
#
# 1 <= price <= 10^9
#
# The total number of calls to addOrder, modifyOrder, cancelOrder, and
# getOrdersAtPrice does not exceed 2000.
#
# For modifyOrder and cancelOrder, the specified orderId is guaranteed to
# exist and be active.
#

# @lc code=start

from collections import defaultdict
from typing import Dict, List, Tuple


class OrderManagementSystem:
    """
    Interview explanation:
    Maintain active orders by id and index them by (orderType, price) for
    fast getOrdersAtPrice. Small n (<= 2000) makes list remove acceptable.
    """

    def __init__(self):
        """
        Interview explanation:
        Initialize empty order maps.

        Algorithm:
        - orders[id] = (type, price); t[(type, price)] = list of ids.

        Complexity: O(1).
        """
        self.orders: Dict[int, Tuple[str, int]] = {}
        self.t: Dict[Tuple[str, int], List[int]] = defaultdict(list)

    def addOrder(self, orderId: int, orderType: str, price: int) -> None:
        """
        Interview explanation:
        Register a new active order.

        Algorithm:
        - Store (type, price) and append orderId under that key.

        Complexity: O(1) time.
        """
        self.orders[orderId] = (orderType, price)
        self.t[(orderType, price)].append(orderId)

    def modifyOrder(self, orderId: int, newPrice: int) -> None:
        """
        Interview explanation:
        Move an active order to a new price.

        Algorithm:
        - Remove id from old (type, price) list; append under new price;
          update orders map.

        Complexity: O(n) time for list remove.
        """
        orderType, price = self.orders[orderId]
        self.orders[orderId] = (orderType, newPrice)
        self.t[(orderType, price)].remove(orderId)
        self.t[(orderType, newPrice)].append(orderId)

    def cancelOrder(self, orderId: int) -> None:
        """
        Interview explanation:
        Deactivate an order.

        Algorithm:
        - Remove from index list and delete from orders.

        Complexity: O(n) time for list remove.
        """
        orderType, price = self.orders[orderId]
        del self.orders[orderId]
        self.t[(orderType, price)].remove(orderId)

    def getOrdersAtPrice(self, orderType: str, price: int) -> List[int]:
        """
        Interview explanation:
        List active order ids with the given type and price.

        Algorithm:
        - Return the stored list (order irrelevant).

        Complexity: O(1) time.
        """
        return self.t[(orderType, price)]


# Your OrderManagementSystem object will be instantiated and called as such:
# obj = OrderManagementSystem()
# obj.addOrder(orderId,orderType,price)
# obj.modifyOrder(orderId,newPrice)
# obj.cancelOrder(orderId)
# param_4 = obj.getOrdersAtPrice(orderType,price)
# @lc code=end
