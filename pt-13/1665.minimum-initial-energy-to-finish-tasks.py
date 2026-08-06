#
# @lc app=leetcode id=1665 lang=python3
#
# [1665] Minimum Initial Energy to Finish Tasks
#
# https://leetcode.com/problems/minimum-initial-energy-to-finish-tasks/description/
#
# algorithms
# Hard (76.49%)
# Likes:    867
# Dislikes: 45
# Total Accepted:    104K
# Total Submissions: 136K
# Testcase Example:  "[[1,2],[2,4],[4,8]]"
#
# You are given an array tasks where tasks[i] = [actual_i, minimum_i]:
#
# actual_i is the actual amount of energy you spend to finish the i^th task.
#
# minimum_i is the minimum amount of energy you require to begin the i^th task.
#
# For example, if the task is [10, 12] and your current energy is 11, you
# cannot start this task. However, if your current energy is 13, you can
# complete this task, and your energy will be 3 after finishing it.
#
# You can finish the tasks in any order you like.
#
# Return the minimum initial amount of energy you will need to finish all the
# tasks.
#
# Example 1:
#
# Input: tasks = [[1,2],[2,4],[4,8]]
# Output: 8
# Explanation:
# Starting with 8 energy, we finish the tasks in the following order:
# - 3rd task. Now energy = 8 - 4 = 4.
# - 2nd task. Now energy = 4 - 2 = 2.
# - 1st task. Now energy = 2 - 1 = 1.
# Notice that even though we have leftover energy, starting with 7 energy does
# not work because we cannot do the 3rd task.
#
# Example 2:
#
# Input: tasks = [[1,3],[2,4],[10,11],[10,12],[8,9]]
# Output: 32
# Explanation:
# Starting with 32 energy, we finish the tasks in the following order:
# - 1st task. Now energy = 32 - 1 = 31.
# - 2nd task. Now energy = 31 - 2 = 29.
# - 3rd task. Now energy = 29 - 10 = 19.
# - 4th task. Now energy = 19 - 10 = 9.
# - 5th task. Now energy = 9 - 8 = 1.
#
# Example 3:
#
# Input: tasks = [[1,7],[2,8],[3,9],[4,10],[5,11],[6,12]]
# Output: 27
# Explanation:
# Starting with 27 energy, we finish the tasks in the following order:
# - 5th task. Now energy = 27 - 5 = 22.
# - 2nd task. Now energy = 22 - 2 = 20.
# - 3rd task. Now energy = 20 - 3 = 17.
# - 1st task. Now energy = 17 - 1 = 16.
# - 4th task. Now energy = 16 - 4 = 12.
# - 6th task. Now energy = 12 - 6 = 6.
#
# Constraints:
#
# 1 <= tasks.length <= 10^5
#
# 1 <= actual_i <= minimum_i <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def minimumEffort(self, tasks: List[List[int]]) -> int:
        """
        Interview explanation:
        Each task [actual, minimum]: need >= minimum energy to start; then spend
        actual. Order matters: do tasks with largest (minimum-actual) gap first
        so high reserve requirements happen when energy is still high.

        Algorithm (greedy sort):
        - Sort by (minimum-actual) ascending; ans = max(ans+actual, minimum) for each.

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        tasks.sort(key=lambda t: t[1] - t[0])
        ans = 0
        for actual, minimum in tasks:
            ans = max(ans + actual, minimum)
        return ans

    def minimumEffort_binary_search(self, tasks: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: binary search initial energy; simulate doing largest
        (minimum-actual) tasks first (feasible schedule order).

        Algorithm:
        - Sort by (minimum-actual) descending; lo/hi binary search with simulation.

        Complexity: O(n log n * log SUM) time.
        """
        tasks = sorted(tasks, key=lambda t: t[1] - t[0], reverse=True)

        def ok(energy: int) -> bool:
            cur = energy
            for actual, minimum in tasks:
                if cur < minimum:
                    return False
                cur -= actual
            return True

        lo = max(t[1] for t in tasks)
        hi = sum(t[0] for t in tasks) + lo
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
