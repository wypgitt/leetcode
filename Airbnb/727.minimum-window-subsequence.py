#
# @lc app=leetcode id=727 lang=python3
#
# [727] Minimum Window Subsequence
#
# https://leetcode.com/problems/minimum-window-subsequence/description/
#
# algorithms
# Hard (43.86%)
# Likes:    1490
# Dislikes: 95
# Total Accepted:    99.8K
# Total Submissions: 227.5K
# Testcase Example:  "\"abcdebdde\"\n\"bde\""
#
#
# Given strings s1 and s2, return the minimum contiguous substring part of
# s1, so that s2 is a subsequence of the part.
#
# If there is no such window in s1 that covers all characters in s2,
# return the empty string "". If there are multiple such minimum-length
# windows, return the one with the left-most starting index.
#
# Example 1:
#
# Input: s1 = "abcdebdde", s2 = "bde"
# Output: "bcde"
# Explanation:
# "bcde" is the answer because it occurs before "bdde" which has the same
# length.
# "deb" is not a smaller window because the elements of s2 in the window
# must occur in order.
#
# Example 2:
#
# Input: s1 = "jmeqksfrsdcmsiwvaovztaqenprpvnbstl", s2 = "u"
# Output: ""
#
# Constraints:
#
# 1 <= s1.length <= 2 * 10^4
#
# 1 <= s2.length <= 100
#
# s1 and s2 consist of lowercase English letters.
#
# @lc code=start
class Solution:
    def minWindow(self, s1: str, s2: str) -> str:
        """
        Interview explanation:
        Premium. Find the shortest substring of s1 that contains s2 as a
        subsequence. Two-pointer scan: for each start matching s2[0], advance
        through s1 until s2 is fully matched, then shrink from the left while
        still covering s2 (by walking s2 backward), and track the best window.

        Algorithm (two pointers / forward-backward):
        - i over s1; when s1[i] == s2[0], let j walk s1 matching s2 forward.
        - If s2 fully matched ending at end, walk backward from end matching s2
          to find the tightest start; update best if shorter.
        - Continue scanning from start+1.

        Complexity: O(|s1| * |s2|) time worst case, O(1) extra space.
        """
        if not s2:
            return ""
        n, m = len(s1), len(s2)
        best_len = float("inf")
        best = ""
        i = 0
        while i < n:
            if s1[i] != s2[0]:
                i += 1
                continue
            j = i
            k = 0
            while j < n and k < m:
                if s1[j] == s2[k]:
                    k += 1
                j += 1
            if k < m:
                break
            end = j - 1
            # shrink: walk s2 backward from end
            k = m - 1
            j = end
            while k >= 0:
                if s1[j] == s2[k]:
                    k -= 1
                j -= 1
            start = j + 1
            if end - start + 1 < best_len:
                best_len = end - start + 1
                best = s1[start : end + 1]
            i = start + 1
        return best

    def minWindow_dp(self, s1: str, s2: str) -> str:
        """
        Interview explanation:
        Alternate classic DP: dp[i][j] = start index in s1 of the shortest window
        ending at i-1 that covers s2[:j] as a subsequence (or -1 if impossible).
        Track the minimum length window among endings that cover all of s2.

        Algorithm:
        - dp[0][0] = 0; dp[0][j>0] = -1
        - For i in 1..n: for j in 0..m: if j==0: dp[i][0]=i; elif s1[i-1]==s2[j-1]
          and dp[i-1][j-1]>=0: dp[i][j]=dp[i-1][j-1]; else dp[i][j]=dp[i-1][j]
        - For each i with dp[i][m]>=0, window [dp[i][m], i)

        Complexity: O(|s1| * |s2|) time and space (space optimizable to O(|s2|)).
        """
        n, m = len(s1), len(s2)
        # rolling: prev[j] = start for covering s2[:j] ending at previous i
        INF = n + 1
        prev = [-1] * (m + 1)
        prev[0] = 0
        best_len = INF
        best = ""
        for i in range(1, n + 1):
            cur = [-1] * (m + 1)
            cur[0] = i
            ch = s1[i - 1]
            for j in range(1, m + 1):
                if ch == s2[j - 1] and prev[j - 1] >= 0:
                    cur[j] = prev[j - 1]
                else:
                    cur[j] = prev[j]
            if cur[m] >= 0 and i - cur[m] < best_len:
                best_len = i - cur[m]
                best = s1[cur[m] : i]
            prev = cur
        return best
# @lc code=end

