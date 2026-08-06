#
# @lc app=leetcode id=2076 lang=python3
#
# [2076] Process Restricted Friend Requests
#
# https://leetcode.com/problems/process-restricted-friend-requests/description/
#
# algorithms
# Hard (61.34%)
# Likes:    680
# Dislikes: 16
# Total Accepted:    27.8K
# Total Submissions: 45.3K
# Testcase Example:  "3\n[[0,1]]\n[[0,2],[2,1]]"
#
# You are given an integer n indicating the number of people in a network. Each
# person is labeled from 0 to n - 1.
#
# You are also given a 0-indexed 2D integer array restrictions, where
# restrictions[i] = [x_i, y_i] means that person x_i and person y_i cannot
# become friends, either directly or indirectly through other people.
#
# Initially, no one is friends with each other. You are given a list of friend
# requests as a 0-indexed 2D integer array requests, where requests[j] = [u_j,
# v_j] is a friend request between person u_j and person v_j.
#
# A friend request is successful if u_j and v_j can be friends. Each friend
# request is processed in the given order (i.e., requests[j] occurs before
# requests[j + 1]), and upon a successful request, u_j and v_j become direct
# friends for all future friend requests.
#
# Return a boolean array result, where each result[j] is true if the j^th friend
# request is successful or false if it is not.
#
# Note: If u_j and v_j are already direct friends, the request is still
# successful.
#
#
#
# Example 1:
#
# Input: n = 3, restrictions = [[0,1]], requests = [[0,2],[2,1]]
# Output: [true,false]
# Explanation:
# Request 0: Person 0 and person 2 can be friends, so they become direct
# friends.
# Request 1: Person 2 and person 1 cannot be friends since person 0 and person 1
# would be indirect friends (1--2--0).
#
# Example 2:
#
# Input: n = 3, restrictions = [[0,1]], requests = [[1,2],[0,2]]
# Output: [true,false]
# Explanation:
# Request 0: Person 1 and person 2 can be friends, so they become direct
# friends.
# Request 1: Person 0 and person 2 cannot be friends since person 0 and person 1
# would be indirect friends (0--2--1).
#
# Example 3:
#
# Input: n = 5, restrictions = [[0,1],[1,2],[2,3]], requests =
# [[0,4],[1,2],[3,1],[3,4]]
# Output: [true,false,true,false]
# Explanation:
# Request 0: Person 0 and person 4 can be friends, so they become direct
# friends.
# Request 1: Person 1 and person 2 cannot be friends since they are directly
# restricted.
# Request 2: Person 3 and person 1 can be friends, so they become direct
# friends.
# Request 3: Person 3 and person 4 cannot be friends since person 0 and person 1
# would be indirect friends (0--4--3--1).
#
#
#
# Constraints:
#
#
# 2 <= n <= 1000
#
#
# 0 <= restrictions.length <= 1000
#
#
# restrictions[i].length == 2
#
#
# 0 <= x_i, y_i <= n - 1
#
#
# x_i != y_i
#
#
# 1 <= requests.length <= 1000
#
#
# requests[j].length == 2
#
#
# 0 <= u_j, v_j <= n - 1
#
#
# u_j != v_j
#

# @lc code=start
from typing import List


class Solution:
    def friendRequests(self, n: int, restrictions: List[List[int]], requests: List[List[int]]) -> List[bool]:
        """
        Interview explanation:
        Process friend requests in order with Union-Find. A request is denied if
        it would put any restricted pair in the same component.

        Algorithm:
        - For request (u,v): if find(u)!=find(v), check no restriction has ends
          in the two components; if ok, union and True else False.

        Complexity: O((n + R*Q) α(n)) time, O(n) space.
        """
        parent = list(range(n))
        rank = [0] * n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int):
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1

        ans = []
        for u, v in requests:
            pu, pv = find(u), find(v)
            if pu == pv:
                ans.append(True)
                continue
            ok = True
            for x, y in restrictions:
                px, py = find(x), find(y)
                if (px == pu and py == pv) or (px == pv and py == pu):
                    ok = False
                    break
            if ok:
                union(u, v)
            ans.append(ok)
        return ans
# @lc code=end
