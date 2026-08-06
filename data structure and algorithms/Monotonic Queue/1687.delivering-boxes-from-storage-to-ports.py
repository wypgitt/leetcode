#
# @lc app=leetcode id=1687 lang=python3
#
# [1687] Delivering Boxes from Storage to Ports
#
# https://leetcode.com/problems/delivering-boxes-from-storage-to-ports/description/
#
# algorithms
# Hard (39.99%)
# Likes:    412
# Dislikes: 33
# Total Accepted:    9.6K
# Total Submissions: 24.1K
# Testcase Example:  "[[1,1],[2,1],[1,1]]"
#
# You have the task of delivering some boxes from storage to their ports using
# only one ship. However, this ship has a limit on the number of boxes and the
# total weight that it can carry.
#
# You are given an array boxes, where boxes[i] = [ports_i, weight_i], and three
# integers portsCount, maxBoxes, and maxWeight.
#
# ports_i is the port where you need to deliver the i^th box and weights_i is
# the weight of the i^th box.
#
# portsCount is the number of ports.
#
# maxBoxes and maxWeight are the respective box and weight limits of the ship.
#
# The boxes need to be delivered in the order they are given. The ship will
# follow these steps:
#
# The ship will take some number of boxes from the boxes queue, not violating
# the maxBoxes and maxWeight constraints.
#
# For each loaded box in order, the ship will make a trip to the port the box
# needs to be delivered to and deliver it. If the ship is already at the
# correct port, no trip is needed, and the box can immediately be delivered.
#
# The ship then makes a return trip to storage to take more boxes from the
# queue.
#
# The ship must end at storage after all the boxes have been delivered.
#
# Return the minimum number of trips the ship needs to make to deliver all
# boxes to their respective ports.
#
# Example 1:
#
# Input: boxes = [[1,1],[2,1],[1,1]], portsCount = 2, maxBoxes = 3, maxWeight =
# 3
# Output: 4
# Explanation: The optimal strategy is as follows:
# - The ship takes all the boxes in the queue, goes to port 1, then port 2,
# then port 1 again, then returns to storage. 4 trips.
# So the total number of trips is 4.
# Note that the first and third boxes cannot be delivered together because the
# boxes need to be delivered in order (i.e. the second box needs to be
# delivered at port 2 before the third box).
#
# Example 2:
#
# Input: boxes = [[1,2],[3,3],[3,1],[3,1],[2,4]], portsCount = 3, maxBoxes = 3,
# maxWeight = 6
# Output: 6
# Explanation: The optimal strategy is as follows:
# - The ship takes the first box, goes to port 1, then returns to storage. 2
# trips.
# - The ship takes the second, third and fourth boxes, goes to port 3, then
# returns to storage. 2 trips.
# - The ship takes the fifth box, goes to port 2, then returns to storage. 2
# trips.
# So the total number of trips is 2 + 2 + 2 = 6.
#
# Example 3:
#
# Input: boxes = [[1,4],[1,2],[2,1],[2,1],[3,2],[3,4]], portsCount = 3,
# maxBoxes = 6, maxWeight = 7
# Output: 6
# Explanation: The optimal strategy is as follows:
# - The ship takes the first and second boxes, goes to port 1, then returns to
# storage. 2 trips.
# - The ship takes the third and fourth boxes, goes to port 2, then returns to
# storage. 2 trips.
# - The ship takes the fifth and sixth boxes, goes to port 3, then returns to
# storage. 2 trips.
# So the total number of trips is 2 + 2 + 2 = 6.
#
# Constraints:
#
# 1 <= boxes.length <= 10^5
#
# 1 <= portsCount, maxBoxes, maxWeight <= 10^5
#
# 1 <= ports_i <= portsCount
#
# 1 <= weights_i <= maxWeight
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def boxDelivering(self, boxes: List[List[int]], portsCount: int, maxBoxes: int, maxWeight: int) -> int:
        """
        Interview explanation:
        Deliver boxes in order in trips: each trip takes a prefix of remaining
        boxes under maxBoxes/maxWeight; cost = number of distinct consecutive
        port changes + 2 (go and return). DP: dp[i]=min trips cost to finish
        first i boxes. Optimize with sliding window + deque for min(dp[j]-extra).

        Algorithm (DP + monoqueue):
        - dp[0]=0; maintain window [j,i) valid by boxes/weight; track port diffs.
        - Use deque of j minimizing dp[j] - port_changes_prefix related term.

        Complexity: O(n) time, O(n) space.
        """
        n = len(boxes)
        # dp[i] = min trips to deliver first i boxes (1-index)
        dp = [0] * (n + 1)
        # sliding window left, weight sum, and number of port changes in (left, i]
        j = 0
        weight = 0
        # diff[i] = 1 if boxes[i] port != boxes[i-1] port (i>=1)
        # For trip from j..i-1 (0-index), cost = 2 + sum_{t=j+1}^{i-1} (port[t]!=port[t-1])
        # dp[i] = min_{j} dp[j] + cost(j..i-1)
        # Use deque storing j; need min dp[j] - pref[j] where pref counts port changes from 0
        pref = [0] * (n + 1)
        for i in range(1, n):
            pref[i] = pref[i - 1] + (boxes[i][0] != boxes[i - 1][0])
        pref[n] = pref[n - 1]

        dq = deque([0])  # indices j
        # ws[i] = weight of box i
        cur_w = 0
        left = 0
        for i in range(1, n + 1):
            cur_w += boxes[i - 1][1]
            while i - left > maxBoxes or cur_w > maxWeight:
                cur_w -= boxes[left][1]
                left += 1
            while dq and dq[0] < left:
                dq.popleft()
            # cost from j to i-1: 2 + (pref[i-1] - pref[j])
            # dp[i] = min_j dp[j] + 2 + pref[i-1] - pref[j]
            j0 = dq[0]
            dp[i] = dp[j0] + 2 + pref[i - 1] - pref[j0]
            # push i as future j; key = dp[i] - pref[i]
            if i < n:
                while dq and dp[dq[-1]] - pref[dq[-1]] >= dp[i] - pref[i]:
                    dq.pop()
                dq.append(i)
        return dp[n]
# @lc code=end
