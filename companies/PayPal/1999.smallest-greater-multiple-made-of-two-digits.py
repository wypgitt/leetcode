#
# @lc app=leetcode id=1999 lang=python3
#
# [1999] Smallest Greater Multiple Made of Two Digits
#
# https://leetcode.com/problems/smallest-greater-multiple-made-of-two-digits/description/
#
# algorithms
# Medium (48.03%)
# Likes:    32
# Dislikes: 11
# Total Accepted:    2.7K
# Total Submissions: 5.6K
# Testcase Example:  "2\n0\n2"
#
#
# Given three integers, k, digit1, and digit2, you want to find the
# smallest integer that is:
#
# Larger than k,
#
# A multiple of k, and
#
# Comprised of only the digits digit1 and/or digit2.
#
# Return the smallest such integer. If no such integer exists or the
# integer exceeds the limit of a signed 32-bit integer (2^31 - 1), return
# -1.
#
# Example 1:
#
# Input: k = 2, digit1 = 0, digit2 = 2
# Output: 20
# Explanation:
# 20 is the first integer larger than 2, a multiple of 2, and comprised of
# only the digits 0 and/or 2.
#
# Example 2:
#
# Input: k = 3, digit1 = 4, digit2 = 2
# Output: 24
# Explanation:
# 24 is the first integer larger than 3, a multiple of 3, and comprised of
# only the digits 4 and/or 2.
#
# Example 3:
#
# Input: k = 2, digit1 = 0, digit2 = 0
# Output: -1
# Explanation:
# No integer meets the requirements so return -1.
#
# Constraints:
#
# 1 <= k <= 1000
#
# 0 <= digit1 <= 9
#
# 0 <= digit2 <= 9
#
# @lc code=start
from collections import deque


class Solution:
    def findInteger(self, k: int) -> int:
        """
        Interview explanation:
        Premium. Smallest positive multiple of k that uses at most two distinct
        digits. Enumerate digit pairs (including same digit); BFS by remainder
        mod k to find smallest number (length-bounded).

        Algorithm:
        - For digits a<=b in 0..9: BFS states (remainder, value) appending a or b;
          skip leading zeros; return min successful value or -1 if none <= 10^18-ish.

        Complexity: O(90 * k * 2) per digit-pair BFS; overall O(k) typical.
        """
        if k == 0:
            return -1
        best = None
        for d1 in range(10):
            for d2 in range(d1, 10):
                digits = {d1, d2}
                # BFS on remainder
                q = deque()
                seen = [False] * k
                # start with single non-zero digits from the set
                for d in digits:
                    if d == 0:
                        continue
                    r = d % k
                    if not seen[r]:
                        seen[r] = True
                        q.append((r, d))
                while q:
                    r, val = q.popleft()
                    if r == 0:
                        if best is None or val < best:
                            best = val
                        break  # BFS length order → first hit is smallest for this pair
                    if val > 10**18 // 10:
                        continue
                    for d in digits:
                        nv = val * 10 + d
                        nr = (r * 10 + d) % k
                        if not seen[nr]:
                            seen[nr] = True
                            q.append((nr, nv))
        return best if best is not None else -1

    def findInteger_set(self, k: int) -> int:
        """
        Interview explanation:
        Alternate: same digit-pair BFS storing only remainders; reconstruct via
        parent pointers, or keep the integer value as in primary.

        Algorithm:
        - Identical search; early-stop per pair on remainder 0; take global min.

        Complexity: O(100 * k) time, O(k) space per pair.
        """
        ans = -1
        for a in range(10):
            for b in range(a, 10):
                digs = (a, b) if a != b else (a,)
                q = deque()
                seen = set()
                for d in digs:
                    if d == 0:
                        continue
                    q.append(d)
                    seen.add(d % k)
                found = None
                while q:
                    val = q.popleft()
                    if val % k == 0:
                        found = val
                        break
                    if val >= 10**17:
                        continue
                    for d in digs:
                        nv = val * 10 + d
                        r = nv % k
                        if r not in seen:
                            # note: seen on remainder only may miss smaller later numbers
                            # with same remainder — for minimality keep value BFS by length
                            seen.add(r)
                            q.append(nv)
                if found is not None and (ans < 0 or found < ans):
                    ans = found
        return ans
# @lc code=end

