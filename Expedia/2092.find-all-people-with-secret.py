#
# @lc app=leetcode id=2092 lang=python3
#
# [2092] Find All People With Secret
#
# https://leetcode.com/problems/find-all-people-with-secret/description/
#
# algorithms
# Hard (48.38%)
# Likes:    1971
# Dislikes: 90
# Total Accepted:    170.6K
# Total Submissions: 352.7K
# Testcase Example:  "6\n[[1,2,5],[2,3,8],[1,5,10]]\n1"
#
# You are given an integer n indicating there are n people numbered from 0 to n
# - 1. You are also given a 0-indexed 2D integer array meetings where
# meetings[i] = [x_i, y_i, time_i] indicates that person x_i and person y_i have
# a meeting at time_i. A person may attend multiple meetings at the same time.
# Finally, you are given an integer firstPerson.
#
# Person 0 has a secret and initially shares the secret with a person
# firstPerson at time 0. This secret is then shared every time a meeting takes
# place with a person that has the secret. More formally, for every meeting, if
# a person x_i has the secret at time_i, then they will share the secret with
# person y_i, and vice versa.
#
# The secrets are shared instantaneously. That is, a person may receive the
# secret and share it with people in other meetings within the same time frame.
#
# Return a list of all the people that have the secret after all the meetings
# have taken place. You may return the answer in any order.
#
#
#
# Example 1:
#
# Input: n = 6, meetings = [[1,2,5],[2,3,8],[1,5,10]], firstPerson = 1
# Output: [0,1,2,3,5]
# Explanation:
# At time 0, person 0 shares the secret with person 1.
# At time 5, person 1 shares the secret with person 2.
# At time 8, person 2 shares the secret with person 3.
# At time 10, person 1 shares the secret with person 5.​​​​
# Thus, people 0, 1, 2, 3, and 5 know the secret after all the meetings.
#
# Example 2:
#
# Input: n = 4, meetings = [[3,1,3],[1,2,2],[0,3,3]], firstPerson = 3
# Output: [0,1,3]
# Explanation:
# At time 0, person 0 shares the secret with person 3.
# At time 2, neither person 1 nor person 2 know the secret.
# At time 3, person 3 shares the secret with person 0 and person 1.
# Thus, people 0, 1, and 3 know the secret after all the meetings.
#
# Example 3:
#
# Input: n = 5, meetings = [[3,4,2],[1,2,1],[2,3,1]], firstPerson = 1
# Output: [0,1,2,3,4]
# Explanation:
# At time 0, person 0 shares the secret with person 1.
# At time 1, person 1 shares the secret with person 2, and person 2 shares the
# secret with person 3.
# Note that person 2 can share the secret at the same time as receiving it.
# At time 2, person 3 shares the secret with person 4.
# Thus, people 0, 1, 2, 3, and 4 know the secret after all the meetings.
#
#
#
# Constraints:
#
#
# 2 <= n <= 10^5
#
#
# 1 <= meetings.length <= 10^5
#
#
# meetings[i].length == 3
#
#
# 0 <= x_i, y_i <= n - 1
#
#
# x_i != y_i
#
#
# 1 <= time_i <= 10^5
#
#
# 1 <= firstPerson <= n - 1
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def findAllPeople(self, n: int, meetings: List[List[int]], firstPerson: int) -> List[int]:
        """
        Interview explanation:
        Person 0 shares the secret with firstPerson at time 0. At each timestamp,
        secret spreads transitively through same-time meetings. Return everyone
        who knows the secret afterward.

        Algorithm:
        - Group meetings by time; build graph; BFS from current knowers; mark new.

        Complexity: O(m log m + n + m) time, O(n + m) space.
        """
        know = [False] * n
        know[0] = know[firstPerson] = True
        meetings.sort(key=lambda x: x[2])
        i, m = 0, len(meetings)
        while i < m:
            t = meetings[i][2]
            g = defaultdict(list)
            people = []
            while i < m and meetings[i][2] == t:
                x, y, _ = meetings[i]
                g[x].append(y)
                g[y].append(x)
                people.append(x)
                people.append(y)
                i += 1
            q = deque(p for p in set(people) if know[p])
            seen = set(q)
            while q:
                u = q.popleft()
                for v in g[u]:
                    if v not in seen:
                        seen.add(v)
                        know[v] = True
                        q.append(v)
        return [p for p in range(n) if know[p]]

    def findAllPeople_uf(self, n: int, meetings: List[List[int]], firstPerson: int) -> List[int]:
        """
        Interview explanation:
        Alternate classic: Union-Find within each timestamp; anyone connected to
        a knower learns; reset parents for people who did not learn before the
        next timestamp.

        Algorithm:
        - Sort meetings; union pairs in a time group; reset non-knowers' parents.

        Complexity: O(m log m + (n+m) α(n)) time, O(n) space.
        """
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        union(0, firstPerson)
        meetings.sort(key=lambda x: x[2])
        i, mlen = 0, len(meetings)
        while i < mlen:
            j = i
            while j < mlen and meetings[j][2] == meetings[i][2]:
                j += 1
            for k in range(i, j):
                union(meetings[k][0], meetings[k][1])
            root = find(0)
            for k in range(i, j):
                for p in (meetings[k][0], meetings[k][1]):
                    if find(p) != root:
                        parent[p] = p
            i = j
        root = find(0)
        return [p for p in range(n) if find(p) == root]
# @lc code=end
