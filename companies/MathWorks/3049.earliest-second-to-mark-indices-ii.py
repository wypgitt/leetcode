#
# @lc app=leetcode id=3049 lang=python3
#
# [3049] Earliest Second to Mark Indices II
#
# https://leetcode.com/problems/earliest-second-to-mark-indices-ii/description/
#
# algorithms
# Hard (22.27%)
# Likes:    85
# Dislikes: 22
# Total Accepted:    4.2K
# Total Submissions: 18.7K
# Testcase Example:  "[3,2,3]\n[1,3,2,2,2,2,3]"
#
#
# You are given two 1-indexed integer arrays, nums and, changeIndices,
# having lengths n and m, respectively.
#
# Initially, all indices in nums are unmarked. Your task is to mark all
# indices in nums.
#
# In each second, s, in order from 1 to m (inclusive), you can perform one
# of the following operations:
#
# Choose an index i in the range [1, n] and decrement nums[i] by 1.
#
# Set nums[changeIndices[s]] to any non-negative value.
#
# Choose an index i in the range [1, n], where nums[i] is equal to 0, and
# mark index i.
#
# Do nothing.
#
# Return an integer denoting the earliest second in the range [1, m] when
# all indices in nums can be marked by choosing operations optimally, or
# -1 if it is impossible.
#
# Example 1:
#
# Input: nums = [3,2,3], changeIndices = [1,3,2,2,2,2,3]
# Output: 6
# Explanation: In this example, we have 7 seconds. The following
# operations can be performed to mark all indices:
# Second 1: Set nums[changeIndices[1]] to 0. nums becomes [0,2,3].
# Second 2: Set nums[changeIndices[2]] to 0. nums becomes [0,2,0].
# Second 3: Set nums[changeIndices[3]] to 0. nums becomes [0,0,0].
# Second 4: Mark index 1, since nums[1] is equal to 0.
# Second 5: Mark index 2, since nums[2] is equal to 0.
# Second 6: Mark index 3, since nums[3] is equal to 0.
# Now all indices have been marked.
# It can be shown that it is not possible to mark all indices earlier than
# the 6th second.
# Hence, the answer is 6.
#
# Example 2:
#
# Input: nums = [0,0,1,2], changeIndices = [1,2,1,2,1,2,1,2]
# Output: 7
# Explanation: In this example, we have 8 seconds. The following
# operations can be performed to mark all indices:
# Second 1: Mark index 1, since nums[1] is equal to 0.
# Second 2: Mark index 2, since nums[2] is equal to 0.
# Second 3: Decrement index 4 by one. nums becomes [0,0,1,1].
# Second 4: Decrement index 4 by one. nums becomes [0,0,1,0].
# Second 5: Decrement index 3 by one. nums becomes [0,0,0,0].
# Second 6: Mark index 3, since nums[3] is equal to 0.
# Second 7: Mark index 4, since nums[4] is equal to 0.
# Now all indices have been marked.
# It can be shown that it is not possible to mark all indices earlier than
# the 7th second.
# Hence, the answer is 7.
#
# Example 3:
#
# Input: nums = [1,2,3], changeIndices = [1,2,3]
# Output: -1
# Explanation: In this example, it can be shown that it is impossible to
# mark all indices, as we don't have enough seconds.
# Hence, the answer is -1.
#
# Constraints:
#
# 1 <= n == nums.length <= 5000
#
# 0 <= nums[i] <= 10^9
#
# 1 <= m == changeIndices.length <= 5000
#
# 1 <= changeIndices[i] <= n
#

# @lc code=start
from typing import List
import heapq
import bisect


class Solution:
    def earliestSecondToMarkIndices(
        self, nums: List[int], changeIndices: List[int]
    ) -> int:
        """
        Interview explanation:
        Like I, but any second may mark any zero index, and changeIndices[s]
        may set that value to 0 in one op. Minimize seconds to mark all.

        Algorithm:
        - Binary search maxSecond. For first occurrences of positive nums[i],
          decide which indices to zero via a reverse scan + min-heap (drop the
          least-saving zero when a mark second is forced).
        - Cost = decrements+marks for non-zeroed + 2 per zeroed (zero+mark).

        Complexity: O(m log m * log m) time, O(n+m) space.
        """
        second_to_index = self._first_zero_seconds(nums, changeIndices)
        nums_sum = sum(nums)

        def can_mark(max_second: int) -> bool:
            min_heap: List[int] = []
            marks = 0
            for second in range(max_second - 1, -1, -1):
                if second in second_to_index:
                    heapq.heappush(min_heap, nums[second_to_index[second]])
                    if marks == 0:
                        heapq.heappop(min_heap)
                        marks += 1
                    else:
                        marks -= 1
                else:
                    marks += 1
            dec_mark = (nums_sum - sum(min_heap)) + (len(nums) - len(min_heap))
            zero_mark = 2 * len(min_heap)
            return dec_mark + zero_mark <= max_second

        lo, hi = 0, len(changeIndices) + 1
        ans = bisect.bisect_left(range(lo, hi), True, key=can_mark) + lo
        return ans if ans <= len(changeIndices) else -1

    def _first_zero_seconds(
        self, nums: List[int], changeIndices: List[int]
    ) -> dict[int, int]:
        index_to_first: dict[int, int] = {}
        for sec, one in enumerate(changeIndices):
            idx = one - 1
            if nums[idx] > 0 and idx not in index_to_first:
                index_to_first[idx] = sec
        return {sec: idx for idx, sec in index_to_first.items()}
# @lc code=end

