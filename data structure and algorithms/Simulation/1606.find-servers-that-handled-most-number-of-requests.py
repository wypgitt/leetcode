#
# @lc app=leetcode id=1606 lang=python3
#
# [1606] Find Servers That Handled Most Number of Requests
#
# https://leetcode.com/problems/find-servers-that-handled-most-number-of-requests/description/
#
# algorithms
# Hard (45.6%)
# Likes:    684
# Dislikes: 30
# Total Accepted:    30.4K
# Total Submissions: 66.8K
# Testcase Example:  "3"
#
# You have k servers numbered from 0 to k-1 that are being used to handle
# multiple requests simultaneously. Each server has infinite computational
# capacity but cannot handle more than one request at a time. The requests are
# assigned to servers according to a specific algorithm:
#
# The i^th (0-indexed) request arrives.
#
# If all servers are busy, the request is dropped (not handled at all).
#
# If the (i % k)^th server is available, assign the request to that server.
#
# Otherwise, assign the request to the next available server (wrapping around
# the list of servers and starting from 0 if necessary). For example, if the
# i^th server is busy, try to assign the request to the (i+1)^th server, then
# the (i+2)^th server, and so on.
#
# You are given a strictly increasing array arrival of positive integers, where
# arrival[i] represents the arrival time of the i^th request, and another array
# load, where load[i] represents the load of the i^th request (the time it
# takes to complete). Your goal is to find the busiest server(s). A server is
# considered busiest if it handled the most number of requests successfully
# among all the servers.
#
# Return a list containing the IDs (0-indexed) of the busiest server(s). You
# may return the IDs in any order.
#
# Example 1:
#
# Input: k = 3, arrival = [1,2,3,4,5], load = [5,2,3,3,3]
# Output: [1]
# Explanation:
# All of the servers start out available.
# The first 3 requests are handled by the first 3 servers in order.
# Request 3 comes in. Server 0 is busy, so it's assigned to the next available
# server, which is 1.
# Request 4 comes in. It cannot be handled since all servers are busy, so it is
# dropped.
# Servers 0 and 2 handled one request each, while server 1 handled two
# requests. Hence server 1 is the busiest server.
#
# Example 2:
#
# Input: k = 3, arrival = [1,2,3,4], load = [1,2,1,2]
# Output: [0]
# Explanation:
# The first 3 requests are handled by first 3 servers.
# Request 3 comes in. It is handled by server 0 since the server is available.
# Server 0 handled two requests, while servers 1 and 2 handled one request
# each. Hence server 0 is the busiest server.
#
# Example 3:
#
# Input: k = 3, arrival = [1,2,3], load = [10,12,11]
# Output: [0,1,2]
# Explanation: Each server handles a single request, so they are all considered
# the busiest.
#
# Constraints:
#
# 1 <= k <= 10^5
#
# 1 <= arrival.length, load.length <= 10^5
#
# arrival.length == load.length
#
# 1 <= arrival[i], load[i] <= 10^9
#
# arrival is strictly increasing.
#

# @lc code=start
from typing import List
import heapq
import bisect


class Solution:
    def busiestServers(self, k: int, arrival: List[int], load: List[int]) -> List[int]:
        """
        Interview explanation:
        k servers; request i prefers i%k, else next free (mod k). Track busiest.
        Maintain free servers in sorted structure + busy min-heap by end time.

        Algorithm (heap + sorted free list):
        - free = sorted list 0..k-1; busy=(end, server).
        - On arrival: free finished servers; if free empty skip.
        - Prefer server >= i%k via bisect; else wrap to free[0].
        - Assign, push busy, count++.

        Complexity: O(n log k) time, O(k) space.
        """
        free = list(range(k))
        busy = []  # (end_time, server)
        cnt = [0] * k
        for i, (t, L) in enumerate(zip(arrival, load)):
            while busy and busy[0][0] <= t:
                _, s = heapq.heappop(busy)
                bisect.insort(free, s)
            if not free:
                continue
            idx = bisect.bisect_left(free, i % k)
            if idx == len(free):
                idx = 0
            s = free.pop(idx)
            heapq.heappush(busy, (t + L, s))
            cnt[s] += 1
        mx = max(cnt)
        return [i for i, c in enumerate(cnt) if c == mx]

    def busiestServers_twoheaps(self, k: int, arrival: List[int], load: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate without bisect list: use two ordered free heaps (servers >= target
        and all free) plus busy heap — classic O(n log k) variant.

        Algorithm (two free heaps):
        - busy min-heap (end, server); free_ge / free_any as heaps of server ids
          relative to target. Simpler practical form: rebuild free via busy release
          into a set and scan — here we use sorted set simulation with heap of free.

        Complexity: O(n log k) time, O(k) space.
        """
        # Equivalent: maintain free as a min-heap of server ids and a second for wrap.
        free = list(range(k))
        heapq.heapify(free)
        busy = []
        cnt = [0] * k
        for i, (t, L) in enumerate(zip(arrival, load)):
            while busy and busy[0][0] <= t:
                heapq.heappush(free, heapq.heappop(busy)[1])
            if not free:
                continue
            target = i % k
            # find smallest free >= target using temp buffer
            tmp = []
            chosen = None
            while free:
                s = heapq.heappop(free)
                if s >= target:
                    chosen = s
                    break
                tmp.append(s)
            if chosen is None:
                # wrap: restore and take global min
                for s in tmp:
                    heapq.heappush(free, s)
                if not free:
                    continue
                chosen = heapq.heappop(free)
            else:
                for s in tmp:
                    heapq.heappush(free, s)
            heapq.heappush(busy, (t + L, chosen))
            cnt[chosen] += 1
        mx = max(cnt)
        return [i for i, c in enumerate(cnt) if c == mx]
# @lc code=end
