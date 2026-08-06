#
# @lc app=leetcode id=3829 lang=python3
#
# [3829] Design Ride Sharing System
#
# https://leetcode.com/problems/design-ride-sharing-system/description/
#
# algorithms
# Medium (63.41%)
# Likes:    58
# Dislikes: 7
# Total Accepted:    31.5K
# Total Submissions: 49.7K
# Testcase Example:  "[\"RideSharingSystem\",\"addRider\",\"addDriver\",\"addRider\",\"matchDriverWithRider\",\"addDriver\",\"cancelRider\",\"matchDriverWithRider\",\"matchDriverWithRider\"]\n[[],[3],[2],[1],[],[5],[3],[],[]]"
#
#
# A ride sharing system manages ride requests from riders and availability
# from drivers. Riders request rides, and drivers become available over
# time. The system should match riders and drivers in the order they
# arrive.
#
# Implement the RideSharingSystem class:
#
# RideSharingSystem() Initializes the system.
#
# void addRider(int riderId) Adds a new rider with the given riderId.
#
# void addDriver(int driverId) Adds a new driver with the given driverId.
#
# int[] matchDriverWithRider() Matches the earliest available driver with
# the earliest waiting rider and removes both of them from the system.
# Returns an integer array of size 2 where result = [driverId, riderId] if
# a match is made. If no match is available, returns [-1, -1].
#
# void cancelRider(int riderId) Cancels the ride request of the rider with
# the given riderId if the rider exists and has not yet been matched.
#
# Example 1:
#
# Input:
#
# ["RideSharingSystem", "addRider", "addDriver", "addRider",
# "matchDriverWithRider", "addDriver", "cancelRider",
# "matchDriverWithRider", "matchDriverWithRider"]
#
# [[], [3], [2], [1], [], [5], [3], [], []]
#
# Output:
#
# [null, null, null, null, [2, 3], null, null, [5, 1], [-1, -1]]
#
# Explanation
#
# RideSharingSystem rideSharingSystem = new RideSharingSystem(); //
# Initializes the system
#
# rideSharingSystem.addRider(3); // rider 3 joins the queue
#
# rideSharingSystem.addDriver(2); // driver 2 joins the queue
#
# rideSharingSystem.addRider(1); // rider 1 joins the queue
#
# rideSharingSystem.matchDriverWithRider(); // returns [2, 3]
#
# rideSharingSystem.addDriver(5); // driver 5 becomes available
#
# rideSharingSystem.cancelRider(3); // rider 3 is already matched, cancel
# has no effect
#
# rideSharingSystem.matchDriverWithRider(); // returns [5, 1]
#
# rideSharingSystem.matchDriverWithRider(); // returns [-1, -1]
#
# Example 2:
#
# Input:
#
# ["RideSharingSystem", "addRider", "addDriver", "addDriver",
# "matchDriverWithRider", "addRider", "cancelRider",
# "matchDriverWithRider"]
#
# [[], [8], [8], [6], [], [2], [2], []]
#
# Output:
#
# [null, null, null, null, [8, 8], null, null, [-1, -1]]
#
# Explanation
#
# RideSharingSystem rideSharingSystem = new RideSharingSystem(); //
# Initializes the system
#
# rideSharingSystem.addRider(8); // rider 8 joins the queue
#
# rideSharingSystem.addDriver(8); // driver 8 joins the queue
#
# rideSharingSystem.addDriver(6); // driver 6 joins the queue
#
# rideSharingSystem.matchDriverWithRider(); // returns [8, 8]
#
# rideSharingSystem.addRider(2); // rider 2 joins the queue
#
# rideSharingSystem.cancelRider(2); // rider 2 cancels
#
# rideSharingSystem.matchDriverWithRider(); // returns [-1, -1]
#
# Constraints:
#
# 1 <= riderId, driverId <= 1000
#
# Each riderId is unique among riders and is added at most once.
#
# Each driverId is unique among drivers and is added at most once.
#
# At most 1000 calls will be made in total to addRider​​​​​​​, addDriver,
# matchDriverWithRider, and cancelRider.
#

# @lc code=start
from collections import deque
from typing import List


class RideSharingSystem:
    """
    Interview explanation:
    Match earliest waiting rider with earliest available driver; support cancel
    of unmatched riders via a lazy-deleted queue.

    Algorithm:
    - Deques for rider/driver arrival order; set of still-waiting riders.
    - match: skip cancelled rider ids, then pop one driver and one rider.
    - cancel: remove riderId from the waiting set.

    Complexity: O(1) amortized per operation; O(n) space.
    """

    def __init__(self):
        """
        Interview explanation:
        Initialize empty rider and driver queues.

        Algorithm:
        - Empty deques and an empty active-rider set.

        Complexity: O(1) time.
        """
        self.riders: deque[int] = deque()
        self.drivers: deque[int] = deque()
        self.active: set[int] = set()

    def addRider(self, riderId: int) -> None:
        """
        Interview explanation:
        Enqueue a new waiting rider.

        Algorithm:
        - Append riderId and mark it active.

        Complexity: O(1) time.
        """
        self.riders.append(riderId)
        self.active.add(riderId)

    def addDriver(self, driverId: int) -> None:
        """
        Interview explanation:
        Enqueue a new available driver.

        Algorithm:
        - Append driverId to the driver deque.

        Complexity: O(1) time.
        """
        self.drivers.append(driverId)

    def matchDriverWithRider(self) -> List[int]:
        """
        Interview explanation:
        Pair the earliest active rider with the earliest driver.

        Algorithm:
        - Drop cancelled riders from the front of the rider deque.
        - If either queue is empty, return [-1, -1].
        - Else pop both and return [driverId, riderId].

        Complexity: O(1) amortized time.
        """
        while self.riders and self.riders[0] not in self.active:
            self.riders.popleft()
        if not self.riders or not self.drivers:
            return [-1, -1]
        rider = self.riders.popleft()
        self.active.discard(rider)
        driver = self.drivers.popleft()
        return [driver, rider]

    def cancelRider(self, riderId: int) -> None:
        """
        Interview explanation:
        Cancel a still-waiting rider (no-op if already matched).

        Algorithm:
        - Discard riderId from the active set; lazy skip on match.

        Complexity: O(1) time.
        """
        self.active.discard(riderId)


# Your RideSharingSystem object will be instantiated and called as such:
# obj = RideSharingSystem()
# obj.addRider(riderId)
# obj.addDriver(driverId)
# param_3 = obj.matchDriverWithRider()
# obj.cancelRider(riderId)
# @lc code=end
