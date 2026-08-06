#
# @lc app=leetcode id=3666 lang=python3
#
# [3666] Minimum Operations to Equalize Binary String
#
# https://leetcode.com/problems/minimum-operations-to-equalize-binary-string/description/
#
# algorithms
# Hard (45.12%)
# Likes:    313
# Dislikes: 37
# Total Accepted:    62.7K
# Total Submissions: 138.9K
# Testcase Example:  "\"110\"\n1"
#
#
# You are given a binary string s, and an integer k.
#
# In one operation, you must choose exactly k different indices and flip
# each '0' to '1' and each '1' to '0'.
#
# Return the minimum number of operations required to make all characters
# in the string equal to '1'. If it is not possible, return -1.
#
# Example 1:
#
# Input: s = "110", k = 1
#
# Output: 1
#
# Explanation:
#
# There is one '0' in s.
#
# Since k = 1, we can flip it directly in one operation.
#
# Example 2:
#
# Input: s = "0101", k = 3
#
# Output: 2
#
# Explanation:
#
# One optimal set of operations choosing k = 3 indices in each operation
# is:
#
# Operation 1: Flip indices [0, 1, 3]. s changes from "0101" to "1000".
#
# Operation 2: Flip indices [1, 2, 3]. s changes from "1000" to "1111".
#
# Thus, the minimum number of operations is 2.
#
# Example 3:
#
# Input: s = "101", k = 2
#
# Output: -1
#
# Explanation:
#
# Since k = 2 and s has only one '0', it is impossible to flip exactly k
# indices to make all '1'. Hence, the answer is -1.
#
# Constraints:
#
# 1 <= s.length <= 10^​​​​​​​5
#
# s[i] is either '0' or '1'.
#
# 1 <= k <= s.length
#

# @lc code=start
from collections import deque

from sortedcontainers import SortedSet


class Solution:
    def minOperations(self, s: str, k: int) -> int:
        """
        Interview explanation:
        State collapses to the number of zeros. Flipping exactly k indices maps
        a zero-count z to a contiguous same-parity range of new counts. BFS finds
        the shortest path to 0; an ordered set skips already-visited states.

        Algorithm:
        - Let z' = z + k - 2x with x zeros flipped among the k indices.
          Valid x yields z' in [z+k-2*min(z,k), z+k-2*max(k-n+z,0)].
        - BFS on zero counts; from each state enqueue all unvisited counts in
          that range (same parity), removing them from a SortedSet.
        - Return distance to 0, or -1 if unreachable.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(s)
        ts = [SortedSet(range(p, n + 1, 2)) for p in (0, 1)]
        cnt0 = s.count("0")
        ts[cnt0 % 2].discard(cnt0)
        q = deque([cnt0])
        ans = 0
        while q:
            for _ in range(len(q)):
                cur = q.popleft()
                if cur == 0:
                    return ans
                lo = cur + k - 2 * min(cur, k)
                hi = cur + k - 2 * max(k - n + cur, 0)
                t = ts[lo % 2]
                j = t.bisect_left(lo)
                while j < len(t) and t[j] <= hi:
                    q.append(t[j])
                    t.remove(t[j])
            ans += 1
        return -1
# @lc code=end
