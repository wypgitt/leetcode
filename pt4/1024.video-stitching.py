#
# @lc app=leetcode id=1024 lang=python3
#
# [1024] Video Stitching
#
# https://leetcode.com/problems/video-stitching/description/
#
# algorithms
# Medium (52.68%)
# Likes:    1865
# Dislikes: 64
# Total Accepted:    89.1K
# Total Submissions: 169.1K
# Testcase Example:  '[[0,2],[4,6],[8,10],[1,9],[1,5],[5,9]]\n10'
#
# You are given a series of video clips from a sporting event that lasted time
# seconds. These video clips can be overlapping with each other and have
# varying lengths.
# 
# Each video clip is described by an array clips where clips[i] = [starti,
# endi] indicates that the ith clip started at starti and ended at endi.
# 
# We can cut these clips into segments freely.
# 
# 
# For example, a clip [0, 7] can be cut into segments [0, 1] + [1, 3] + [3,
# 7].
# 
# 
# Return the minimum number of clips needed so that we can cut the clips into
# segments that cover the entire sporting event [0, time]. If the task is
# impossible, return -1.
# 
# 
# Example 1:
# 
# 
# Input: clips = [[0,2],[4,6],[8,10],[1,9],[1,5],[5,9]], time = 10
# Output: 3
# Explanation: We take the clips [0,2], [8,10], [1,9]; a total of 3 clips.
# Then, we can reconstruct the sporting event as follows:
# We cut [1,9] into segments [1,2] + [2,8] + [8,9].
# Now we have segments [0,2] + [2,8] + [8,10] which cover the sporting event
# [0, 10].
# 
# 
# Example 2:
# 
# 
# Input: clips = [[0,1],[1,2]], time = 5
# Output: -1
# Explanation: We cannot cover [0,5] with only [0,1] and [1,2].
# 
# 
# Example 3:
# 
# 
# Input: clips =
# [[0,1],[6,8],[0,2],[5,6],[0,4],[0,3],[6,7],[1,3],[4,7],[1,4],[2,5],[2,6],[3,4],[4,5],[5,7],[6,9]],
# time = 9
# Output: 3
# Explanation: We can take clips [0,4], [4,7], and [6,9].
# 
# 
# 
# Constraints:
# 
# 
# 1 <= clips.length <= 100
# 0 <= starti <= endi <= 100
# 1 <= time <= 100
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def videoStitching(self, clips: List[List[int]], time: int) -> int:
        clips.sort()
        clip_index = 0
        used = 0
        covered_until = 0

        while covered_until < time:
            farthest = covered_until

            while clip_index < len(clips) and clips[clip_index][0] <= covered_until:
                farthest = max(farthest, clips[clip_index][1])
                clip_index += 1

            if farthest == covered_until:
                return -1

            used += 1
            covered_until = farthest

        return used
# @lc code=end

"""
Interview Explanation

Core idea:
This is the same greedy structure as Jump Game II or minimum interval cover.
When the current covered prefix is [0, covered_until], the next chosen clip
must start at or before covered_until. Among all such clips, choosing the one
that extends farthest is always optimal for the next step.

Algorithm:
1. Sort clips by start time.
2. While the event is not fully covered, scan all clips whose start is within
   the currently covered prefix.
3. Record the farthest end reachable by adding one more clip.
4. If no clip extends coverage, return -1.
5. Otherwise count one clip and advance coverage to that farthest end.

Data structure choice:
Sorting gives clips in the order they become usable, so a single index is
enough. A heap is unnecessary because once a clip starts too late, no later
clip can help the current gap.

Correctness:
At each step, every feasible solution must choose some clip starting at or
before covered_until. Choosing the clip with the farthest end cannot make a
future solution worse, because it covers every point any shorter feasible clip
would cover and possibly more. Repeating this exchange argument at every step
produces a minimum number of clips. If farthest does not advance, no feasible
clip can cover the next uncovered time, so the answer is impossible.

Complexity:
Sorting costs O(n log n), and the scan is O(n). Extra space is O(1) apart from
the in-place sort.

Tests and edge cases:
- A gap after time 0, such as [[1, 2]], returns -1.
- One clip [0, time] returns 1.
- Heavily overlapping clips still scan once.
- Clips ending past time are fine; the loop stops once coverage reaches time.
"""
