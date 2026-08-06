#
# @lc app=leetcode id=1871 lang=python3
#
# [1871] Jump Game VII
#
# https://leetcode.com/problems/jump-game-vii/description/
#
# algorithms
# Medium (35.63%)
# Likes:    2093
# Dislikes: 131
# Total Accepted:    150K
# Total Submissions: 420K
# Testcase Example:  "\"011010\""
#
# You are given a 0-indexed binary string s and two integers minJump and
# maxJump. In the beginning, you are standing at index 0, which is equal to
# '0'. You can move from index i to index j if the following conditions are
# fulfilled:
#
# i + minJump <= j <= min(i + maxJump, s.length - 1), and
#
# s[j] == '0'.
#
# Return true if you can reach index s.length - 1 in s, or false otherwise.
#
# Example 1:
#
# Input: s = "011010", minJump = 2, maxJump = 3
# Output: true
# Explanation:
# In the first step, move from index 0 to index 3.
# In the second step, move from index 3 to index 5.
#
# Example 2:
#
# Input: s = "01101110", minJump = 2, maxJump = 3
# Output: false
#
# Constraints:
#
# 2 <= s.length <= 10^5
#
# s[i] is either '0' or '1'.
#
# s[0] == '0'
#
# 1 <= minJump <= maxJump < s.length
#

# @lc code=start
from collections import deque


class Solution:
    def canReach(self, s: str, minJump: int, maxJump: int) -> bool:
        """
        Interview explanation:
        From i jump to [i+minJump, i+maxJump] landing on '0'. Reach n-1?
        BFS/sliding window of reachable indices; track farthest processed.

        Algorithm (sliding window DP):
        - reachable[0]=True; maintain count of reachable in window.
        - For i: if window has a reachable index and s[i]=='0': mark reachable.

        Complexity: O(n) time/space.
        """
        n = len(s)
        if s[-1] != "0":
            return False
        reach = [False] * n
        reach[0] = True
        cnt = 0
        for i in range(1, n):
            if i >= minJump:
                cnt += reach[i - minJump]
            if i > maxJump:
                cnt -= reach[i - maxJump - 1]
            reach[i] = cnt > 0 and s[i] == "0"
        return reach[-1]

    def canReach_bfs(self, s: str, minJump: int, maxJump: int) -> bool:
        """
        Interview explanation:
        Alternate BFS: queue of reachable indices; only enqueue unvisited '0's
        in the jump range beyond previous farthest.

        Algorithm:
        - q=[0]; farthest=0; while q: for j in [max(i+minJump,farthest+1), i+maxJump].

        Complexity: O(n) time.
        """
        n = len(s)
        q = deque([0])
        farthest = 0
        while q:
            i = q.popleft()
            start = max(i + minJump, farthest + 1)
            for j in range(start, min(i + maxJump, n - 1) + 1):
                if s[j] == "0":
                    if j == n - 1:
                        return True
                    q.append(j)
            farthest = i + maxJump
        return False
# @lc code=end
