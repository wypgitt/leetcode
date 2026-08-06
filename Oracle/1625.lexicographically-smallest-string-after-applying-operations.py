#
# @lc app=leetcode id=1625 lang=python3
#
# [1625] Lexicographically Smallest String After Applying Operations
#
# https://leetcode.com/problems/lexicographically-smallest-string-after-applying-operations/description/
#
# algorithms
# Medium (79.26%)
# Likes:    695
# Dislikes: 321
# Total Accepted:    87.3K
# Total Submissions: 110K
# Testcase Example:  "\"5525\""
#
# You are given a string s of even length consisting of digits from 0 to 9, and
# two integers a and b.
#
# You can apply either of the following two operations any number of times and
# in any order on s:
#
# Add a to all odd indices of s (0-indexed). Digits post 9 are cycled back to
# 0. For example, if s = "3456" and a = 5, s becomes "3951".
#
# Rotate s to the right by b positions. For example, if s = "3456" and b = 1, s
# becomes "6345".
#
# Return the lexicographically smallest string you can obtain by applying the
# above operations any number of times on s.
#
# A string a is lexicographically smaller than a string b (of the same length)
# if in the first position where a and b differ, string a has a letter that
# appears earlier in the alphabet than the corresponding letter in b. For
# example, "0158" is lexicographically smaller than "0190" because the first
# position they differ is at the third letter, and '5' comes before '9'.
#
# Example 1:
#
# Input: s = "5525", a = 9, b = 2
# Output: "2050"
# Explanation: We can apply the following operations:
# Start: "5525"
# Rotate: "2555"
# Add: "2454"
# Add: "2353"
# Rotate: "5323"
# Add: "5222"
# Add: "5121"
# Rotate: "2151"
# Add: "2050"
# There is no way to obtain a string that is lexicographically smaller than
# "2050".
#
# Example 2:
#
# Input: s = "74", a = 5, b = 1
# Output: "24"
# Explanation: We can apply the following operations:
# Start: "74"
# Rotate: "47"
# Add: "42"
# Rotate: "24"
# There is no way to obtain a string that is lexicographically smaller than
# "24".
#
# Example 3:
#
# Input: s = "0011", a = 4, b = 2
# Output: "0011"
# Explanation: There are no sequence of operations that will give us a
# lexicographically smaller string than "0011".
#
# Constraints:
#
# 2 <= s.length <= 100
#
# s.length is even.
#
# s consists of digits from 0 to 9 only.
#
# 1 <= a <= 9
#
# 1 <= b <= s.length - 1
#

# @lc code=start
from collections import deque


class Solution:
    def findLexSmallestString(self, s: str, a: int, b: int) -> str:
        """
        Interview explanation:
        Ops: add a to all odd indices (mod 10); rotate right by b. Find lex-smallest
        reachable string. BFS over state space (small: n<=100, digits).

        Algorithm (BFS):
        - Queue/visited; apply both ops; track minimum string seen.

        Complexity: O(n * 10 * n / gcd) states ~ O(n^2 * 10) time.
        """
        n = len(s)
        seen = {s}
        q = deque([s])
        ans = s
        while q:
            cur = q.popleft()
            if cur < ans:
                ans = cur
            chars = list(cur)
            for i in range(1, n, 2):
                chars[i] = str((int(chars[i]) + a) % 10)
            add_s = "".join(chars)
            rot_s = cur[-b:] + cur[:-b]
            for nxt in (add_s, rot_s):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        return ans

    def findLexSmallestString_dfs(self, s: str, a: int, b: int) -> str:
        """
        Interview explanation:
        Alternate DFS/stack enumeration of the same finite transformation graph.

        Algorithm (DFS iterative):
        - Stack + visited; same two transitions; track min.

        Complexity: same as BFS.
        """
        n = len(s)
        seen = set()
        st = [s]
        ans = s
        while st:
            cur = st.pop()
            if cur in seen:
                continue
            seen.add(cur)
            if cur < ans:
                ans = cur
            chars = list(cur)
            for i in range(1, n, 2):
                chars[i] = str((int(chars[i]) + a) % 10)
            st.append("".join(chars))
            st.append(cur[-b:] + cur[:-b])
        return ans
# @lc code=end
