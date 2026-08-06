#
# @lc app=leetcode id=1345 lang=python3
#
# [1345] Jump Game IV
#
# https://leetcode.com/problems/jump-game-iv/description/
#
# algorithms
# Hard (51.06%)
# Likes:    4159
# Dislikes: 138
# Total Accepted:    244K
# Total Submissions: 477K
# Testcase Example:  "[100,-23,-23,404,100,23,23,23,3,404]"
#
# Given an array of integers arr, you are initially positioned at the first
# index of the array.
#
# In one step you can jump from index i to index:
#
# i + 1 where: i + 1 < arr.length.
#
# i - 1 where: i - 1 >= 0.
#
# j where: arr[i] == arr[j] and i != j.
#
# Return the minimum number of steps to reach the last index of the array.
#
# Notice that you can not jump outside of the array at any time.
#
# Example 1:
#
# Input: arr = [100,-23,-23,404,100,23,23,23,3,404]
# Output: 3
# Explanation: You need three jumps from index 0 --> 4 --> 3 --> 9. Note that
# index 9 is the last index of the array.
#
# Example 2:
#
# Input: arr = [7]
# Output: 0
# Explanation: Start index is the last index. You do not need to jump.
#
# Example 3:
#
# Input: arr = [7,6,9,6,9,6,9,7]
# Output: 1
# Explanation: You can jump directly from index 0 to index 7 which is last
# index of the array.
#
# Constraints:
#
# 1 <= arr.length <= 5 * 10^4
#
# -10^8 <= arr[i] <= 10^8
#

# @lc code=start
from collections import defaultdict, deque
from typing import List


class Solution:
    def minJumps(self, arr: List[int]) -> int:
        """
        Interview explanation:
        From i jump to i±1 or any j with arr[j]==arr[i]. Shortest path — BFS.
        Critical: clear the value->indices list after first use to avoid O(n^2).

        Algorithm (BFS):
        - Map value to indices; BFS steps from 0; neighbors i-1,i+1,same-value;
          delete map entry after processing.

        Complexity: O(n) time, O(n) space.
        """
        n = len(arr)
        if n == 1:
            return 0
        mp = defaultdict(list)
        for i, v in enumerate(arr):
            mp[v].append(i)
        q = deque([0])
        seen = {0}
        steps = 0
        while q:
            for _ in range(len(q)):
                i = q.popleft()
                if i == n - 1:
                    return steps
                for j in mp[arr[i]]:
                    if j not in seen:
                        seen.add(j)
                        q.append(j)
                mp[arr[i]].clear()
                for j in (i - 1, i + 1):
                    if 0 <= j < n and j not in seen:
                        seen.add(j)
                        q.append(j)
            steps += 1
        return -1
# @lc code=end

