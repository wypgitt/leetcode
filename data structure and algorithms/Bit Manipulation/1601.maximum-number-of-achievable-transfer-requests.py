#
# @lc app=leetcode id=1601 lang=python3
#
# [1601] Maximum Number of Achievable Transfer Requests
#
# https://leetcode.com/problems/maximum-number-of-achievable-transfer-requests/description/
#
# algorithms
# Hard (64.73%)
# Likes:    1503
# Dislikes: 75
# Total Accepted:    65.7K
# Total Submissions: 101K
# Testcase Example:  "5"
#
# We have n buildings numbered from 0 to n - 1. Each building has a number of
# employees. It's transfer season, and some employees want to change the
# building they reside in.
#
# You are given an array requests where requests[i] = [from_i, to_i] represents
# an employee's request to transfer from building from_i to building to_i.
#
# All buildings are full, so a list of requests is achievable only if for each
# building, the net change in employee transfers is zero. This means the number
# of employees leaving is equal to the number of employees moving in. For
# example if n = 3 and two employees are leaving building 0, one is leaving
# building 1, and one is leaving building 2, there should be two employees
# moving to building 0, one employee moving to building 1, and one employee
# moving to building 2.
#
# Return the maximum number of achievable requests.
#
# Example 1:
#
# Input: n = 5, requests = [[0,1],[1,0],[0,1],[1,2],[2,0],[3,4]]
# Output: 5
# Explantion: Let's see the requests:
# From building 0 we have employees x and y and both want to move to building
# 1.
# From building 1 we have employees a and b and they want to move to buildings
# 2 and 0 respectively.
# From building 2 we have employee z and they want to move to building 0.
# From building 3 we have employee c and they want to move to building 4.
# From building 4 we don't have any requests.
# We can achieve the requests of users x and b by swapping their places.
# We can achieve the requests of users y, a and z by swapping the places in the
# 3 buildings.
#
# Example 2:
#
# Input: n = 3, requests = [[0,0],[1,2],[2,1]]
# Output: 3
# Explantion: Let's see the requests:
# From building 0 we have employee x and they want to stay in the same building
# 0.
# From building 1 we have employee y and they want to move to building 2.
# From building 2 we have employee z and they want to move to building 1.
# We can achieve all the requests.
#
# Example 3:
#
# Input: n = 4, requests = [[0,3],[3,1],[1,2],[2,0]]
# Output: 4
#
# Constraints:
#
# 1 <= n <= 20
#
# 1 <= requests.length <= 16
#
# requests[i].length == 2
#
# 0 <= from_i, to_i < n
#

# @lc code=start
from typing import List


class Solution:
    def maximumRequests(self, n: int, requests: List[List[int]]) -> int:
        """
        Interview explanation:
        A subset of transfers is achievable iff every building's net change is 0.
        With <=16 requests, backtrack over include/exclude each request.

        Algorithm (DFS / backtracking):
        - Maintain net[i] for each building; recurse on request index.
        - Include: net[from]--, net[to]++, recurse; backtrack.
        - At end, if all net==0 update answer with count of included requests.

        Complexity: O(2^m * n) time, O(m+n) space; m<=16.
        """
        m = len(requests)
        net = [0] * n
        ans = 0

        def dfs(i: int, cnt: int) -> None:
            nonlocal ans
            if i == m:
                if all(x == 0 for x in net):
                    ans = max(ans, cnt)
                return
            # skip
            dfs(i + 1, cnt)
            # take
            u, v = requests[i]
            net[u] -= 1
            net[v] += 1
            dfs(i + 1, cnt + 1)
            net[u] += 1
            net[v] -= 1

        dfs(0, 0)
        return ans

    def maximumRequests_bitmask(self, n: int, requests: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic alternate: enumerate all 2^m subsets via bitmasks; check balance.

        Algorithm (bitmask):
        - For mask in 0..2^m-1: apply selected requests; if all net 0, track popcount.

        Complexity: O(2^m * m) time, O(n) space.
        """
        m = len(requests)
        ans = 0
        for mask in range(1 << m):
            net = [0] * n
            cnt = 0
            for i in range(m):
                if mask >> i & 1:
                    u, v = requests[i]
                    net[u] -= 1
                    net[v] += 1
                    cnt += 1
            if all(x == 0 for x in net):
                ans = max(ans, cnt)
        return ans
# @lc code=end
