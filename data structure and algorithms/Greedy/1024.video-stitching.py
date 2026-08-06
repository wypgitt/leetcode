#
# @lc app=leetcode id=1024 lang=python3
#
# [1024] Video Stitching
#
# https://leetcode.com/problems/video-stitching/description/
#
# algorithms
# Medium (52.85%)
# Likes:    1878
# Dislikes: 64
# Total Accepted:    92.1K
# Total Submissions: 174K
# Testcase Example:  "[[0,2],[4,6],[8,10],[1,9],[1,5],[5,9]]"
#
# You are given a series of video clips from a sporting event that lasted time
# seconds. These video clips can be overlapping with each other and have
# varying lengths.
#
# Each video clip is described by an array clips where clips[i] = [start_i,
# end_i] indicates that the ith clip started at start_i and ended at end_i.
#
# We can cut these clips into segments freely.
#
# For example, a clip [0, 7] can be cut into segments [0, 1] + [1, 3] + [3, 7].
#
# Return the minimum number of clips needed so that we can cut the clips into
# segments that cover the entire sporting event [0, time]. If the task is
# impossible, return -1.
#
# Example 1:
#
# Input: clips = [[0,2],[4,6],[8,10],[1,9],[1,5],[5,9]], time = 10
# Output: 3
# Explanation: We take the clips [0,2], [8,10], [1,9]; a total of 3 clips.
# Then, we can reconstruct the sporting event as follows:
# We cut [1,9] into segments [1,2] + [2,8] + [8,9].
# Now we have segments [0,2] + [2,8] + [8,10] which cover the sporting event
# [0, 10].
#
# Example 2:
#
# Input: clips = [[0,1],[1,2]], time = 5
# Output: -1
# Explanation: We cannot cover [0,5] with only [0,1] and [1,2].
#
# Example 3:
#
# Input: clips =
# [[0,1],[6,8],[0,2],[5,6],[0,4],[0,3],[6,7],[1,3],[4,7],[1,4],[2,5],[2,6],[3,4],[4,5],[5,7],[6,9]],
# time = 9
# Output: 3
# Explanation: We can take clips [0,4], [4,7], and [6,9].
#
# Constraints:
#
# 1 <= clips.length <= 100
#
# 0 <= start_i <= end_i <= 100
#
# 1 <= time <= 100
#

# @lc code=start
from typing import List


class Solution:
    def videoStitching(self, clips: List[List[int]], time: int) -> int:
        """
        Interview explanation:
        Jump-game style greedy: for current coverage end, among clips starting
        <= end, take the one that extends farthest; count clips; fail if stuck
        before time.

        Algorithm:
        - Sort clips by start
        - cur_end=0, farthest=0, i=0, ans=0
        - While cur_end < time: advance i over clips with start<=cur_end updating farthest
          if farthest==cur_end: return -1; cur_end=farthest; ans++

        Complexity: O(n log n) time, O(1) extra space.
        """
        clips.sort()
        ans = cur_end = farthest = i = 0
        n = len(clips)
        while cur_end < time:
            while i < n and clips[i][0] <= cur_end:
                farthest = max(farthest, clips[i][1])
                i += 1
            if farthest == cur_end:
                return -1
            cur_end = farthest
            ans += 1
        return ans

    def videoStitching_dp(self, clips: List[List[int]], time: int) -> int:
        """
        Interview explanation:
        Alternate classic DP: dp[t] = min clips to cover [0,t]. For each clip
        [s,e], update dp[s+1..e] using dp[s]+1.

        Algorithm:
        - dp[0]=0; dp[1..time]=inf
        - For clip [s,e]: for t in s+1..min(e,time): dp[t]=min(dp[t], dp[s]+1)
        - Repeat until stable or single pass over sorted clips carefully
        - Actually: iterate clips; for each update range from max(s,0)

        Complexity: O(n * time) time, O(time) space.
        """
        INF = 10**9
        dp = [0] + [INF] * time
        for _ in range(time):
            changed = False
            for s, e in clips:
                if s > time:
                    continue
                base = dp[s] if s <= time else INF
                if base >= INF:
                    continue
                for t in range(s + 1, min(e, time) + 1):
                    if base + 1 < dp[t]:
                        dp[t] = base + 1
                        changed = True
            if not changed:
                break
        return dp[time] if dp[time] < INF else -1
# @lc code=end
