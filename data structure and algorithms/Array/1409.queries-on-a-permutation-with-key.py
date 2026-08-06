#
# @lc app=leetcode id=1409 lang=python3
#
# [1409] Queries on a Permutation With Key
#
# https://leetcode.com/problems/queries-on-a-permutation-with-key/description/
#
# algorithms
# Medium (84.96%)
# Likes:    522
# Dislikes: 645
# Total Accepted:    60.9K
# Total Submissions: 71.7K
# Testcase Example:  "[3,1,2,1]"
#
# Given the array queries of positive integers between 1 and m, you have to
# process all queries[i] (from i=0 to i=queries.length-1) according to the
# following rules:
#
# In the beginning, you have the permutation P=[1,2,3,...,m].
#
# For the current i, find the position of queries[i] in the permutation P
# (indexing from 0) and then move this at the beginning of the permutation P.
# Notice that the position of queries[i] in P is the result for queries[i].
#
# Return an array containing the result for the given queries.
#
# Example 1:
#
# Input: queries = [3,1,2,1], m = 5
# Output: [2,1,2,1]
# Explanation: The queries are processed as follow:
# For i=0: queries[i]=3, P=[1,2,3,4,5], position of 3 in P is 2, then we move 3
# to the beginning of P resulting in P=[3,1,2,4,5].
# For i=1: queries[i]=1, P=[3,1,2,4,5], position of 1 in P is 1, then we move 1
# to the beginning of P resulting in P=[1,3,2,4,5].
# For i=2: queries[i]=2, P=[1,3,2,4,5], position of 2 in P is 2, then we move 2
# to the beginning of P resulting in P=[2,1,3,4,5].
# For i=3: queries[i]=1, P=[2,1,3,4,5], position of 1 in P is 1, then we move 1
# to the beginning of P resulting in P=[1,2,3,4,5].
# Therefore, the array containing the result is [2,1,2,1].
#
# Example 2:
#
# Input: queries = [4,1,2,2], m = 4
# Output: [3,1,2,0]
#
# Example 3:
#
# Input: queries = [7,5,5,8,3], m = 8
# Output: [6,5,0,7,5]
#
# Constraints:
#
# 1 <= m <= 10^3
#
# 1 <= queries.length <= m
#
# 1 <= queries[i] <= m
#

# @lc code=start
from typing import List


class Solution:
    def processQueries(self, queries: List[int], m: int) -> List[int]:
        """
        Interview explanation:
        Start with P=[1..m]. For each query q: find index of q, record it, move
        q to front. Simulate with a list.

        Algorithm:
        (list simulation)
        - P=list(range(1,m+1)); for q: i=P.index(q); ans.append(i); P.insert(0,P.pop(i))

        Complexity: O(q * m) time, O(m) space.
        """
        P = list(range(1, m + 1))
        ans = []
        for q in queries:
            i = P.index(q)
            ans.append(i)
            P.insert(0, P.pop(i))
        return ans

    def processQueries_fenwick(self, queries: List[int], m: int) -> List[int]:
        """
        Interview explanation:
        Alternate optimal: Fenwick/BIT over positions. Map each value to a
        dynamic position in a range of size m+|queries|; move-to-front = assign
        a new smaller index and BIT query rank.

        Algorithm:
        - pos[val]=m+val initially in BIT of ones; for query: rank=prefix(pos[q]-1);
          remove old, place at next free left slot.

        Complexity: O((m+q) log (m+q)) time, O(m+q) space.
        """
        N = m + len(queries) + 5
        bit = [0] * (N + 1)

        def add(i, v):
            while i <= N:
                bit[i] += v
                i += i & -i

        def summ(i):
            s = 0
            while i:
                s += bit[i]
                i -= i & -i
            return s

        pos = [0] * (m + 1)
        for i in range(1, m + 1):
            pos[i] = len(queries) + i
            add(pos[i], 1)
        cur = len(queries)
        ans = []
        for q in queries:
            ans.append(summ(pos[q] - 1))
            add(pos[q], -1)
            pos[q] = cur
            add(pos[q], 1)
            cur -= 1
        return ans
# @lc code=end
