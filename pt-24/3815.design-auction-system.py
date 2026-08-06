#
# @lc app=leetcode id=3815 lang=python3
#
# [3815] Design Auction System
#
# https://leetcode.com/problems/design-auction-system/description/
#
# algorithms
# Medium (41.92%)
# Likes:    88
# Dislikes: 7
# Total Accepted:    17.2K
# Total Submissions: 40.9K
# Testcase Example:  "[\"AuctionSystem\",\"addBid\",\"addBid\",\"getHighestBidder\",\"updateBid\",\"getHighestBidder\",\"removeBid\",\"getHighestBidder\",\"getHighestBidder\"]\n[[],[1,7,5],[2,7,6],[7],[1,7,8],[7],[2,7],[7],[3]]"
#
#
# You are asked to design an auction system that manages bids from
# multiple users in real time.
#
# Each bid is associated with a userId, an itemId, and a bidAmount.
#
# Implement the AuctionSystem class:​​​​​​​
#
# AuctionSystem(): Initializes the AuctionSystem object.
#
# void addBid(int userId, int itemId, int bidAmount): Adds a new bid for
# itemId by userId with bidAmount. If the same userId already has a bid on
# itemId, replace it with the new bidAmount.
#
# void updateBid(int userId, int itemId, int newAmount): Updates the
# existing bid of userId for itemId to newAmount. It is guaranteed that
# this bid exists.
#
# void removeBid(int userId, int itemId): Removes the bid of userId for
# itemId. It is guaranteed that this bid exists.
#
# int getHighestBidder(int itemId): Returns the userId of the highest
# bidder for itemId. If multiple users have the same highest bidAmount,
# return the user with the highest userId. If no bids exist for the item,
# return -1.
#
# Example 1:
#
# Input:
#
# ["AuctionSystem", "addBid", "addBid", "getHighestBidder", "updateBid",
# "getHighestBidder", "removeBid", "getHighestBidder", "getHighestBidder"]
#
# [[], [1, 7, 5], [2, 7, 6], [7], [1, 7, 8], [7], [2, 7], [7], [3]]
#
# Output:
#
# [null, null, null, 2, null, 1, null, 1, -1]
#
# Explanation
#
# AuctionSystem auctionSystem = new AuctionSystem(); // Initialize the
# Auction system
#
# auctionSystem.addBid(1, 7, 5); // User 1 bids 5 on item 7
#
# auctionSystem.addBid(2, 7, 6); // User 2 bids 6 on item 7
#
# auctionSystem.getHighestBidder(7); // return 2 as User 2 has the highest
# bid
#
# auctionSystem.updateBid(1, 7, 8); // User 1 updates bid to 8 on item 7
#
# auctionSystem.getHighestBidder(7); // return 1 as User 1 now has the
# highest bid
#
# auctionSystem.removeBid(2, 7); // Remove User 2's bid on item 7
#
# auctionSystem.getHighestBidder(7); // return 1 as User 1 is the current
# highest bidder
#
# auctionSystem.getHighestBidder(3); // return -1 as no bids exist for
# item 3
#
# Constraints:
#
# 1 <= userId, itemId <= 5 * 10^4
#
# 1 <= bidAmount, newAmount <= 10^9
#
# At most 5 * 10^4 total calls to addBid, updateBid, removeBid, and
# getHighestBidder.
#
# The input is generated such that for updateBid and removeBid, the bid
# from the given userId for the given itemId will be valid.
#

# @lc code=start

from collections import defaultdict

from sortedcontainers import SortedList


class AuctionSystem:
    """
    Interview explanation:
    Track per-item bids in a SortedList keyed by (amount, userId) so the
    highest bidder (tie: highest userId) is the last element. Map
    userId -> itemId -> amount for O(log m) updates/removals.
    """

    def __init__(self):
        """
        Interview explanation:
        Initialize empty bid stores.

        Algorithm:
        - items[itemId] is a SortedList of (bidAmount, userId).
        - users[userId][itemId] stores the current amount.

        Complexity: O(1).
        """
        self.items = defaultdict(SortedList)
        self.users = {}

    def addBid(self, userId: int, itemId: int, bidAmount: int) -> None:
        """
        Interview explanation:
        Upsert userId's bid on itemId.

        Algorithm:
        - If a prior bid exists, remove it; then record the new amount in
          users and items.

        Complexity: O(log m) time.
        """
        if userId not in self.users:
            self.users[userId] = {}
        if itemId in self.users[userId]:
            self.removeBid(userId, itemId)
        self.users[userId][itemId] = bidAmount
        self.items[itemId].add((bidAmount, userId))

    def updateBid(self, userId: int, itemId: int, newAmount: int) -> None:
        """
        Interview explanation:
        Change an existing bid's amount.

        Algorithm:
        - Remove (oldAmount, userId) from the item's SortedList; insert the
          new tuple; update the users map.

        Complexity: O(log m) time.
        """
        oldAmount = self.users[userId][itemId]
        self.items[itemId].remove((oldAmount, userId))
        self.items[itemId].add((newAmount, userId))
        self.users[userId][itemId] = newAmount

    def removeBid(self, userId: int, itemId: int) -> None:
        """
        Interview explanation:
        Delete userId's bid on itemId.

        Algorithm:
        - Drop from SortedList and users map.

        Complexity: O(log m) time.
        """
        oldAmount = self.users[userId][itemId]
        self.items[itemId].remove((oldAmount, userId))
        self.users[userId].pop(itemId)

    def getHighestBidder(self, itemId: int) -> int:
        """
        Interview explanation:
        Return highest bidder on itemId (highest userId on ties), or -1.

        Algorithm:
        - If the SortedList is empty return -1; else return last element's
          userId.

        Complexity: O(1) time.
        """
        ls = self.items[itemId]
        return -1 if not ls else ls[-1][1]


# Your AuctionSystem object will be instantiated and called as such:
# obj = AuctionSystem()
# obj.addBid(userId,itemId,bidAmount)
# obj.updateBid(userId,itemId,newAmount)
# obj.removeBid(userId,itemId)
# param_4 = obj.getHighestBidder(itemId)
# @lc code=end
