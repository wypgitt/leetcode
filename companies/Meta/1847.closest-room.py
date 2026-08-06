#
# @lc app=leetcode id=1847 lang=python3
#
# [1847] Closest Room
#
# https://leetcode.com/problems/closest-room/description/
#
# algorithms
# Hard (41.74%)
# Likes:    542
# Dislikes: 21
# Total Accepted:    13.0K
# Total Submissions: 31.0K
# Testcase Example:  "[[2,2],[1,2],[3,2]]"
#
# There is a hotel with n rooms. The rooms are represented by a 2D integer
# array rooms where rooms[i] = [roomId_i, size_i] denotes that there is a room
# with room number roomId_i and size equal to size_i. Each roomId_i is
# guaranteed to be unique.
#
# You are also given k queries in a 2D array queries where queries[j] =
# [preferred_j, minSize_j]. The answer to the j^th query is the room number id
# of a room such that:
#
# The room has a size of at least minSize_j, and
#
# abs(id - preferred_j) is minimized, where abs(x) is the absolute value of x.
#
# If there is a tie in the absolute difference, then use the room with the
# smallest such id. If there is no such room, the answer is -1.
#
# Return an array answer of length k where answer[j] contains the answer to the
# j^th query.
#
# Example 1:
#
# Input: rooms = [[2,2],[1,2],[3,2]], queries = [[3,1],[3,3],[5,2]]
# Output: [3,-1,3]
# Explanation: The answers to the queries are as follows:
# Query = [3,1]: Room number 3 is the closest as abs(3 - 3) = 0, and its size
# of 2 is at least 1. The answer is 3.
# Query = [3,3]: There are no rooms with a size of at least 3, so the answer is
# -1.
# Query = [5,2]: Room number 3 is the closest as abs(3 - 5) = 2, and its size
# of 2 is at least 2. The answer is 3.
#
# Example 2:
#
# Input: rooms = [[1,4],[2,3],[3,5],[4,1],[5,2]], queries = [[2,3],[2,4],[2,5]]
# Output: [2,1,3]
# Explanation: The answers to the queries are as follows:
# Query = [2,3]: Room number 2 is the closest as abs(2 - 2) = 0, and its size
# of 3 is at least 3. The answer is 2.
# Query = [2,4]: Room numbers 1 and 3 both have sizes of at least 4. The answer
# is 1 since it is smaller.
# Query = [2,5]: Room number 3 is the only room with a size of at least 5. The
# answer is 3.
#
# Constraints:
#
# n == rooms.length
#
# 1 <= n <= 10^5
#
# k == queries.length
#
# 1 <= k <= 10^4
#
# 1 <= roomId_i, preferred_j <= 10^7
#
# 1 <= size_i, minSize_j <= 10^7
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def closestRoom(self, rooms: List[List[int]], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Offline queries: process rooms/queries by decreasing size so available
        rooms always satisfy minSize. Among available ids, pick closest to
        preferred (tie: smaller id). Use Fenwick on compressed ids for
        predecessor/successor.

        Algorithm (sort + Fenwick order statistics):
        - Compress room ids; BIT stores presence.
        - Sort rooms desc by size; queries desc by minSize.
        - Insert room ids into BIT; for each query find floor/ceil preferred.

        Complexity: O((n+q) log n) time, O(n+q) space.
        """
        ids = sorted({r[0] for r in rooms})
        idx = {v: i + 1 for i, v in enumerate(ids)}  # 1-based
        m = len(ids)
        bit = [0] * (m + 1)

        def add(i: int, v: int) -> None:
            while i <= m:
                bit[i] += v
                i += i & -i

        def sum_(i: int) -> int:
            s = 0
            while i:
                s += bit[i]
                i -= i & -i
            return s

        def find_kth(k: int) -> int:
            # 1-indexed k among present
            pos = 0
            b = 1 << (m.bit_length())
            while b:
                nxt = pos + b
                if nxt <= m and bit[nxt] < k:
                    k -= bit[nxt]
                    pos = nxt
                b >>= 1
            return pos + 1

        rooms = sorted(rooms, key=lambda x: -x[1])
        order = sorted(range(len(queries)), key=lambda i: -queries[i][1])
        ans = [-1] * len(queries)
        j = 0
        for qi in order:
            pref, mn = queries[qi]
            while j < len(rooms) and rooms[j][1] >= mn:
                add(idx[rooms[j][0]], 1)
                j += 1
            total = sum_(m)
            if total == 0:
                continue
            # count of ids < preferred
            # bisect_left on ids
            p = bisect.bisect_left(ids, pref)
            # floor: last present among 1..p (ids index p is first >= pref; floor at p)
            # ids is 0-based; BIT index = position+1
            best = None
            # predecessor: kth among first p present (indices 1..p)
            left_cnt = sum_(p)  # present in ids[:p] i.e. < pref
            if left_cnt:
                floor_i = find_kth(left_cnt)  # BIT index
                best = ids[floor_i - 1]
            # successor: first present at/after preferred -> among ids[p:]
            right_cnt = total - left_cnt
            if right_cnt:
                ceil_i = find_kth(left_cnt + 1)
                cand = ids[ceil_i - 1]
                if best is None or abs(cand - pref) < abs(best - pref) or (
                    abs(cand - pref) == abs(best - pref) and cand < best
                ):
                    best = cand
            ans[qi] = best
        return ans
# @lc code=end
