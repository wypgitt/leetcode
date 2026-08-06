#
# @lc app=leetcode id=1845 lang=python3
#
# [1845] Seat Reservation Manager
#
# https://leetcode.com/problems/seat-reservation-manager/description/
#
# algorithms
# Medium (67.35%)
# Likes:    1486
# Dislikes: 92
# Total Accepted:    153K
# Total Submissions: 226K
# Testcase Example:  "[\"SeatManager\",\"reserve\",\"reserve\",\"unreserve\",\"reserve\",\"reserve\",\"reserve\",\"reserve\",\"unreserve\"]"
#
# Design a system that manages the reservation state of n seats that are
# numbered from 1 to n.
#
# Implement the SeatManager class:
#
# SeatManager(int n) Initializes a SeatManager object that will manage n seats
# numbered from 1 to n. All seats are initially available.
#
# int reserve() Fetches the smallest-numbered unreserved seat, reserves it, and
# returns its number.
#
# void unreserve(int seatNumber) Unreserves the seat with the given seatNumber.
#
# Example 1:
#
# Input
# ["SeatManager", "reserve", "reserve", "unreserve", "reserve", "reserve",
# "reserve", "reserve", "unreserve"]
# [[5], [], [], [2], [], [], [], [], [5]]
# Output
# [null, 1, 2, null, 2, 3, 4, 5, null]
#
# Explanation
# SeatManager seatManager = new SeatManager(5); // Initializes a SeatManager
# with 5 seats.
# seatManager.reserve(); // All seats are available, so return the lowest
# numbered seat, which is 1.
# seatManager.reserve(); // The available seats are [2,3,4,5], so return the
# lowest of them, which is 2.
# seatManager.unreserve(2); // Unreserve seat 2, so now the available seats are
# [2,3,4,5].
# seatManager.reserve(); // The available seats are [2,3,4,5], so return the
# lowest of them, which is 2.
# seatManager.reserve(); // The available seats are [3,4,5], so return the
# lowest of them, which is 3.
# seatManager.reserve(); // The available seats are [4,5], so return the lowest
# of them, which is 4.
# seatManager.reserve(); // The only available seat is seat 5, so return 5.
# seatManager.unreserve(5); // Unreserve seat 5, so now the available seats are
# [5].
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 1 <= seatNumber <= n
#
# For each call to reserve, it is guaranteed that there will be at least one
# unreserved seat.
#
# For each call to unreserve, it is guaranteed that seatNumber will be
# reserved.
#
# At most 10^5 calls in total will be made to reserve and unreserve.
#

# @lc code=start
import heapq


class SeatManager:
    def __init__(self, n: int):
        """
        Interview explanation:
        Manage seats 1..n; reserve smallest free; unreserve returns a seat.
        Min-heap of available seats (initially all, or lazy next unused + heap of returned).

        Algorithm (min-heap of free seats):
        - free = [1..n] heapified; or marker+returned heap for O(1) init.

        Complexity: O(n) init for full heap; O(1) with lazy variant below.
        """
        self.next_new = 1
        self.n = n
        self.freed = []

    def reserve(self) -> int:
        """
        Interview explanation:
        Return smallest unreserved seat.

        Algorithm:
        - If freed heap non-empty, pop min; else allocate next_new++.

        Complexity: O(log n).
        """
        if self.freed:
            return heapq.heappop(self.freed)
        seat = self.next_new
        self.next_new += 1
        return seat

    def unreserve(self, seatNumber: int) -> None:
        """
        Interview explanation:
        Mark seatNumber available again.

        Algorithm:
        - Push seatNumber onto freed min-heap.

        Complexity: O(log n).
        """
        heapq.heappush(self.freed, seatNumber)
# @lc code=end
