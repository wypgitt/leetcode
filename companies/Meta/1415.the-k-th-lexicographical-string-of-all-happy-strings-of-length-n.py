#
# @lc app=leetcode id=1415 lang=python3
#
# [1415] The k-th Lexicographical String of All Happy Strings of Length n
#
# https://leetcode.com/problems/the-k-th-lexicographical-string-of-all-happy-strings-of-length-n/description/
#
# algorithms
# Medium (87.07%)
# Likes:    1802
# Dislikes: 56
# Total Accepted:    281K
# Total Submissions: 323K
# Testcase Example:  "1"
#
# A happy string is a string that:
#
# consists only of letters of the set ['a', 'b', 'c'].
#
# s[i] != s[i + 1] for all values of i from 1 to s.length - 1 (string is
# 1-indexed).
#
# For example, strings "abc", "ac", "b" and "abcbabcbcb" are all happy strings
# and strings "aa", "baa" and "ababbc" are not happy strings.
#
# Given two integers n and k, consider a list of all happy strings of length n
# sorted in lexicographical order.
#
# Return the kth string of this list or return an empty string if there are
# less than k happy strings of length n.
#
# Example 1:
#
# Input: n = 1, k = 3
# Output: "c"
# Explanation: The list ["a", "b", "c"] contains all happy strings of length 1.
# The third string is "c".
#
# Example 2:
#
# Input: n = 1, k = 4
# Output: ""
# Explanation: There are only 3 happy strings of length 1.
#
# Example 3:
#
# Input: n = 3, k = 9
# Output: "cab"
# Explanation: There are 12 different happy string of length 3 ["aba", "abc",
# "aca", "acb", "bab", "bac", "bca", "bcb", "cab", "cac", "cba", "cbc"]. You
# will find the 9^th string = "cab"
#
# Constraints:
#
# 1 <= n <= 10
#
# 1 <= k <= 100
#

# @lc code=start
class Solution:
    def getHappyString(self, n: int, k: int) -> str:
        """
        Interview explanation:
        Happy strings: lowercase a/b/c, no two adjacent equal. Lex order.
        Total = 3*2^(n-1). If k larger, "". Build by choosing letters that leave
        enough remaining strings (digit DP / combinatorial indexing).

        Algorithm:
        (math / combinatorial)
        - rem = 2^(n-1); for position: try letters > prev in order; if k>block skip.

        Complexity: O(n) time, O(n) space.
        """
        total = 3 * (1 << (n - 1))
        if k > total:
            return ""
        ans = []
        prev = ""
        for i in range(n):
            block = 1 << (n - i - 1)
            for ch in "abc":
                if ch == prev:
                    continue
                if k > block:
                    k -= block
                else:
                    ans.append(ch)
                    prev = ch
                    break
        return "".join(ans)

    def getHappyString_dfs(self, n: int, k: int) -> str:
        """
        Interview explanation:
        Alternate: DFS/backtracking generate happy strings in lex order; stop at k-th.

        Algorithm:
        - Recurse appending a letter != last; count until k.

        Complexity: O(k * n) time worst-case, O(n) space.
        """
        self.k = k
        self.ans = ""

        def dfs(path):
            if self.ans:
                return
            if len(path) == n:
                self.k -= 1
                if self.k == 0:
                    self.ans = "".join(path)
                return
            for ch in "abc":
                if path and path[-1] == ch:
                    continue
                path.append(ch)
                dfs(path)
                path.pop()
                if self.ans:
                    return

        dfs([])
        return self.ans
# @lc code=end
