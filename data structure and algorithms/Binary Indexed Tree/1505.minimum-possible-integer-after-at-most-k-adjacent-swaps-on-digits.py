#
# @lc app=leetcode id=1505 lang=python3
#
# [1505] Minimum Possible Integer After at Most K Adjacent Swaps On Digits
#
# https://leetcode.com/problems/minimum-possible-integer-after-at-most-k-adjacent-swaps-on-digits/description/
#
# algorithms
# Hard (41.71%)
# Likes:    507
# Dislikes: 28
# Total Accepted:    13.4K
# Total Submissions: 32.1K
# Testcase Example:  "\"4321\""
#
# You are given a string num representing the digits of a very large integer
# and an integer k. You are allowed to swap any two adjacent digits of the
# integer at most k times.
#
# Return the minimum integer you can obtain also as a string.
#
# Example 1:
#
# Input: num = "4321", k = 4
# Output: "1342"
# Explanation: The steps to obtain the minimum integer from 4321 with 4
# adjacent swaps are shown.
#
# Example 2:
#
# Input: num = "100", k = 1
# Output: "010"
# Explanation: It's ok for the output to have leading zeros, but the input is
# guaranteed not to have any leading zeros.
#
# Example 3:
#
# Input: num = "36789", k = 1000
# Output: "36789"
# Explanation: We can keep the number without any swaps.
#
# Constraints:
#
# 1 <= num.length <= 3 * 10^4
#
# num consists of only digits and does not contain leading zeros.
#
# 1 <= k <= 10^9
#

# @lc code=start
from collections import deque


class Solution:
    def minInteger(self, num: str, k: int) -> str:
        """
        Interview explanation:
        Build the smallest number by repeatedly bringing the smallest digit
        within the next k+1 positions to the front via adjacent swaps (cost =
        distance). Use digit queues of indices + BIT/Fenwick for how many
        digits already removed before an index (effective position).

        Algorithm:
        - Queues of indices per digit 0-9; for each output position, try d=0..9
          whose front index has cost = idx - removed_before(idx) <= k; pick,
          subtract cost from k, mark removed in BIT.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(num)
        pos = [deque() for _ in range(10)]
        for i, ch in enumerate(num):
            pos[int(ch)].append(i)

        # Fenwick: count of removed indices (1-indexed)
        bit = [0] * (n + 1)

        def bit_add(i: int, v: int = 1) -> None:
            i += 1
            while i <= n:
                bit[i] += v
                i += i & -i

        def bit_sum(i: int) -> int:
            i += 1
            s = 0
            while i > 0:
                s += bit[i]
                i -= i & -i
            return s

        ans = []
        for _ in range(n):
            for d in range(10):
                if not pos[d]:
                    continue
                idx = pos[d][0]
                cost = idx - bit_sum(idx - 1)
                if cost <= k:
                    k -= cost
                    ans.append(str(d))
                    pos[d].popleft()
                    bit_add(idx)
                    break
        return "".join(ans)
# @lc code=end
