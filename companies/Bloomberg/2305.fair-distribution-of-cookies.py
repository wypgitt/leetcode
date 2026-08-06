#
# @lc app=leetcode id=2305 lang=python3
#
# [2305] Fair Distribution of Cookies
#
# https://leetcode.com/problems/fair-distribution-of-cookies/description/
#
# algorithms
# Medium (70.05%)
# Likes:    2756
# Dislikes: 128
# Total Accepted:    124.9K
# Total Submissions: 178.3K
# Testcase Example:  "[8,15,10,20,8]\n2"
#
# You are given an integer array cookies, where cookies[i] denotes the number of
# cookies in the i^th bag. You are also given an integer k that denotes the
# number of children to distribute all the bags of cookies to. All the cookies
# in the same bag must go to the same child and cannot be split up.
#
# The unfairness of a distribution is defined as the maximum total cookies
# obtained by a single child in the distribution.
#
# Return the minimum unfairness of all distributions.
#
#
#
# Example 1:
#
# Input: cookies = [8,15,10,20,8], k = 2
# Output: 31
# Explanation: One optimal distribution is [8,15,8] and [10,20]
# - The 1^st child receives [8,15,8] which has a total of 8 + 15 + 8 = 31
# cookies.
# - The 2^nd child receives [10,20] which has a total of 10 + 20 = 30 cookies.
# The unfairness of the distribution is max(31,30) = 31.
# It can be shown that there is no distribution with an unfairness less than 31.
#
# Example 2:
#
# Input: cookies = [6,1,3,2,2,4,1,2], k = 3
# Output: 7
# Explanation: One optimal distribution is [6,1], [3,2,2], and [4,1,2]
# - The 1^st child receives [6,1] which has a total of 6 + 1 = 7 cookies.
# - The 2^nd child receives [3,2,2] which has a total of 3 + 2 + 2 = 7 cookies.
# - The 3^rd child receives [4,1,2] which has a total of 4 + 1 + 2 = 7 cookies.
# The unfairness of the distribution is max(7,7,7) = 7.
# It can be shown that there is no distribution with an unfairness less than 7.
#
#
#
# Constraints:
#
#
# 2 <= cookies.length <= 8
#
#
# 1 <= cookies[i] <= 10^5
#
#
# 2 <= k <= cookies.length
#

# @lc code=start
from typing import List


class Solution:
    def distributeCookies(self, cookies: List[int], k: int) -> int:
        """
        Interview explanation:
        Distribute cookie bags to k children to minimize the maximum total
        any child receives (unfairness).

        Algorithm:
        - Backtracking: assign each bag to a child; prune when current max
          >= best. Sort descending to prune earlier.
        - Optionally try empty-child early stop to reduce branching.

        Complexity: O(k^n) worst-case with pruning; O(k) space.
        """
        cookies.sort(reverse=True)
        loads = [0] * k
        best = sum(cookies)

        def dfs(i: int) -> None:
            nonlocal best
            if i == len(cookies):
                best = min(best, max(loads))
                return
            seen = set()
            for j in range(k):
                if loads[j] in seen:
                    continue
                seen.add(loads[j])
                if loads[j] + cookies[i] >= best:
                    continue
                loads[j] += cookies[i]
                dfs(i + 1)
                loads[j] -= cookies[i]
                if loads[j] == 0:
                    break

        dfs(0)
        return best

    def distributeCookies_backtrack(self, cookies: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate name for the same backtracking search.

        Algorithm:
        - Assign bags greedily via DFS with pruning on current unfairness.

        Complexity: O(k^n) with pruning; O(k) space.
        """
        return self.distributeCookies(cookies, k)
# @lc code=end
