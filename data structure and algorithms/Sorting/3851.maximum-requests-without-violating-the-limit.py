#
# @lc app=leetcode id=3851 lang=python3
#
# [3851] Maximum Requests Without Violating the Limit
#
# https://leetcode.com/problems/maximum-requests-without-violating-the-limit/description/
#
# algorithms
# Medium (63.11%)
# Likes:    5
# Dislikes: 2
# Total Accepted:    503
# Total Submissions: 797
# Testcase Example:  "[[1,1],[2,1],[1,7],[2,8]]\n1\n4"
#
#
# You are given a 2D integer array requests, where requests[i] = [user_i,
# time_i] indicates that user_i made a request at time_i.
#
# You are also given two integers k and window.
#
# A user violates the limit if there exists an integer t such that the
# user makes strictly more than k requests in the inclusive interval [t, t
# + window].
#
# You may drop any number of requests.
#
# Return an integer denoting the maximum​​​​​​​ number of requests that
# can remain such that no user violates the limit.
#
# Example 1:
#
# Input: requests = [[1,1],[2,1],[1,7],[2,8]], k = 1, window = 4
#
# Output: 4
#
# Explanation:​​​​​​​
#
# For user 1, the request times are [1, 7]. The difference between them is
# 6, which is greater than window = 4.
#
# For user 2, the request times are [1, 8]. The difference is 7, which is
# also greater than window = 4.
#
# No user makes more than k = 1 request within any inclusive interval of
# length window. Therefore, all 4 requests can remain.
#
# Example 2:
#
# Input: requests = [[1,2],[1,5],[1,2],[1,6]], k = 2, window = 5
#
# Output: 2
#
# Explanation:​​​​​​​
#
# For user 1, the request times are [2, 2, 5, 6]. The inclusive interval
# [2, 7] of length window = 5 contains all 4 requests.
#
# Since 4 is strictly greater than k = 2, at least 2 requests must be
# removed.
#
# After removing any 2 requests, every inclusive interval of length window
# contains at most k = 2 requests.
#
# Therefore, the maximum number of requests that can remain is 2.
#
# Example 3:
#
# Input: requests = [[1,1],[2,5],[1,2],[3,9]], k = 1, window = 1
#
# Output: 3
#
# Explanation:
#
# For user 1, the request times are [1, 2]. The difference is 1, which is
# equal to window = 1.
#
# The inclusive interval [1, 2] contains both requests, so the count is 2,
# which exceeds k = 1. One request must be removed.
#
# Users 2 and 3 each have only one request and do not violate the limit.
# Therefore, the maximum number of requests that can remain is 3.
#
# Constraints:
#
# 1 <= requests.length <= 10^5
#
# requests[i] = [user_i, time_i]
#
# 1 <= k <= requests.length
#
# 1 <= user_i, time_i, window <= 10^5
#

# @lc code=start
from collections import defaultdict, deque


class Solution:
    def maxRequests(self, requests: list[list[int]], k: int, window: int) -> int:
        """
        Interview explanation:
        Per user, keep as many requests as possible so no window of length
        `window` contains more than k of them. Greedily keep earliest times.

        Algorithm:
        - Group times by user and sort.
        - Sliding deque of kept times within [t-window, t]; keep t if < k
          kept in that window, else drop it.

        Complexity: O(n log n) time, O(n) space.
        """
        g: dict[int, list[int]] = defaultdict(list)
        for u, t in requests:
            g[u].append(t)
        ans = len(requests)
        for ts in g.values():
            ts.sort()
            kept: deque[int] = deque()
            for t in ts:
                while kept and t - kept[0] > window:
                    kept.popleft()
                if len(kept) < k:
                    kept.append(t)
                else:
                    ans -= 1
        return ans
# @lc code=end
