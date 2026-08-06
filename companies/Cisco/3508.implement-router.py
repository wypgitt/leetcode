#
# @lc app=leetcode id=3508 lang=python3
#
# [3508] Implement Router
#
# https://leetcode.com/problems/implement-router/description/
#
# algorithms
# Medium (39.02%)
# Likes:    495
# Dislikes: 118
# Total Accepted:    90.5K
# Total Submissions: 232K
# Testcase Example:  "[\"Router\",\"addPacket\",\"addPacket\",\"addPacket\",\"addPacket\",\"addPacket\",\"forwardPacket\",\"addPacket\",\"getCount\"]\n[[3],[1,4,90],[2,5,90],[1,4,90],[3,5,95],[4,5,105],[],[5,2,110],[5,100,110]]"
#
#
# Design a data structure that can efficiently manage data packets in a
# network router. Each data packet consists of the following attributes:
#
# source: A unique identifier for the machine that generated the packet.
#
# destination: A unique identifier for the target machine.
#
# timestamp: The time at which the packet arrived at the router.
#
# Implement the Router class:
#
# Router(int memoryLimit): Initializes the Router object with a fixed
# memory limit.
#
# memoryLimit is the maximum number of packets the router can store at any
# given time.
#
# If adding a new packet would exceed this limit, the oldest packet must
# be removed to free up space.
#
# bool addPacket(int source, int destination, int timestamp): Adds a
# packet with the given attributes to the router.
#
# A packet is considered a duplicate if another packet with the same
# source, destination, and timestamp already exists in the router.
#
# Return true if the packet is successfully added (i.e., it is not a
# duplicate); otherwise return false.
#
# int[] forwardPacket(): Forwards the next packet in FIFO (First In First
# Out) order.
#
# Remove the packet from storage.
#
# Return the packet as an array [source, destination, timestamp].
#
# If there are no packets to forward, return an empty array.
#
# int getCount(int destination, int startTime, int endTime):
#
# Returns the number of packets currently stored in the router (i.e., not
# yet forwarded) that have the specified destination and have timestamps
# in the inclusive range [startTime, endTime].
#
# Note that queries for addPacket will be made in non-decreasing order of
# timestamp.
#
# Example 1:
#
# Input:
#
# ["Router", "addPacket", "addPacket", "addPacket", "addPacket",
# "addPacket", "forwardPacket", "addPacket", "getCount"]
#
# [[3], [1, 4, 90], [2, 5, 90], [1, 4, 90], [3, 5, 95], [4, 5, 105], [],
# [5, 2, 110], [5, 100, 110]]
#
# Output:
#
# [null, true, true, false, true, true, [2, 5, 90], true, 1]
#
# Explanation
#
# Router router = new Router(3); // Initialize Router with memoryLimit of
# 3.
#
# router.addPacket(1, 4, 90); // Packet is added. Return True.
#
# router.addPacket(2, 5, 90); // Packet is added. Return True.
#
# router.addPacket(1, 4, 90); // This is a duplicate packet. Return False.
#
# router.addPacket(3, 5, 95); // Packet is added. Return True
#
# router.addPacket(4, 5, 105); // Packet is added, [1, 4, 90] is removed
# as number of packets exceeds memoryLimit. Return True.
#
# router.forwardPacket(); // Return [2, 5, 90] and remove it from router.
#
# router.addPacket(5, 2, 110); // Packet is added. Return True.
#
# router.getCount(5, 100, 110); // The only packet with destination 5 and
# timestamp in the inclusive range [100, 110] is [4, 5, 105]. Return 1.
#
# Example 2:
#
# Input:
#
# ["Router", "addPacket", "forwardPacket", "forwardPacket"]
#
# [[2], [7, 4, 90], [], []]
#
# Output:
#
# [null, true, [7, 4, 90], []]
#
# Explanation
#
# Router router = new Router(2); // Initialize Router with memoryLimit of
# 2.
#
# router.addPacket(7, 4, 90); // Return True.
#
# router.forwardPacket(); // Return [7, 4, 90].
#
# router.forwardPacket(); // There are no packets left, return [].
#
# Constraints:
#
# 2 <= memoryLimit <= 10^5
#
# 1 <= source, destination <= 2 * 10^5
#
# 1 <= timestamp <= 10^9
#
# 1 <= startTime <= endTime <= 10^9
#
# At most 10^5 calls will be made to addPacket, forwardPacket, and
# getCount methods altogether.
#
# queries for addPacket will be made in non-decreasing order of timestamp.
#

# @lc code=start
from typing import List
import collections
import bisect
from dataclasses import dataclass


@dataclass(frozen=True)
class Packet:
    source: int
    destination: int
    timestamp: int


class Router:
    """
    Interview explanation:
    FIFO router with duplicate detection and destination timestamp queries.
    Store packets in a deque; uniqueness in a set; per-destination timestamp
    lists with a processed offset for forwarded packets so getCount is binary
    search on the still-stored suffix.

    Complexity: add/forward amortized O(1); getCount O(log n); space O(n).
    """

    def __init__(self, memoryLimit: int):
        """
        Interview explanation:
        Cap storage at memoryLimit packets.

        Algorithm:
        - Init deque, uniqueness set, destination timestamp lists, offsets.

        Complexity: O(1).
        """
        self.memoryLimit = memoryLimit
        self.uniquePackets: set = set()
        self.packetQueue: collections.deque = collections.deque()
        self.destinationTimestamps = collections.defaultdict(list)
        self.processedPacketIndex = collections.Counter()

    def addPacket(self, source: int, destination: int, timestamp: int) -> bool:
        """
        Interview explanation:
        Insert packet if not duplicate; evict oldest when at capacity.

        Algorithm:
        - Reject if (source, dest, time) seen; else forward oldest if full, then
          append and record timestamp under destination.

        Complexity: Amortized O(1).
        """
        packet = Packet(source, destination, timestamp)
        if packet in self.uniquePackets:
            return False
        if len(self.packetQueue) == self.memoryLimit:
            self.forwardPacket()
        self.packetQueue.append(packet)
        self.uniquePackets.add(packet)
        self.destinationTimestamps[destination].append(timestamp)
        return True

    def forwardPacket(self) -> List[int]:
        """
        Interview explanation:
        Pop and return the oldest stored packet (FIFO).

        Algorithm:
        - Popleft; remove from set; advance destination processed index.

        Complexity: O(1).
        """
        if not self.packetQueue:
            return []
        nxt = self.packetQueue.popleft()
        self.uniquePackets.remove(nxt)
        self.processedPacketIndex[nxt.destination] += 1
        return [nxt.source, nxt.destination, nxt.timestamp]

    def getCount(self, destination: int, startTime: int, endTime: int) -> int:
        """
        Interview explanation:
        Count still-stored packets to destination with timestamp in [start, end].

        Algorithm:
        - Binary search the destination's timestamp list from the processed offset.

        Complexity: O(log n).
        """
        if destination not in self.destinationTimestamps:
            return 0
        timestamps = self.destinationTimestamps[destination]
        start_index = self.processedPacketIndex[destination]
        lo = bisect.bisect_left(timestamps, startTime, start_index)
        hi = bisect.bisect_right(timestamps, endTime, start_index)
        return hi - lo

# Your Router object will be instantiated and called as such:
# obj = Router(memoryLimit)
# param_1 = obj.addPacket(source,destination,timestamp)
# param_2 = obj.forwardPacket()
# param_3 = obj.getCount(destination,startTime,endTime)
# @lc code=end
