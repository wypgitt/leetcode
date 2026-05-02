#
# @lc app=leetcode id=3878 lang=python3
#
# [3878] Count Good Subarrays
#

# @lc code=start
class Solution:
    pass


# @lc code=end

#
# @lc app=leetcode id=3878 lang=python3
#
# [3878] Count Good Subarrays
#
# --- Notes (problem restatement, bit reasoning, monotonic stacks, complexity, interview) ---
#
# Problem restatement
# nums is given. A subarray is GOOD iff
#   (OR of all elements in the subarray)  equals  some element that appears IN that subarray.
# Count good subarrays (contiguous).
#
# Equivalent counting trick (editorial)
# Group each good subarray by WHICH value equals the OR (pick the designated position i).
# For a fixed index i, consider subarrays whose bitwise OR is EXACTLY nums[i].
# Then nums[i] lies in the subarray (usually as position i at least when OR equals nums[i])
# and the subarray is good with witness nums[i].
# Summing over i of "how many subarrays have OR exactly nums[i]" counts each good subarray
# exactly once — each good subarray has a unique largest index j such that nums[j] equals the
# OR (standard tie-breaking in this construction); the formal proof matches the stack bounds.
#
# Bit condition for OR(nums[L..R]) == nums[i]
# Let x = nums[i]. For every index k in [L, R], we need nums[k] | x == x (every element only
# sets bits already present in x). Equivalently nums[k] is a bitwise subset of x.
# If any element had a bit outside x, the OR would strictly exceed x.
#
# Two scans with monotonic stacks
# We need the maximal interval around i where every nums[k] satisfies nums[k] | x == x (with
# x = nums[i]), but boundaries stop where the condition breaks.
#
# Left boundary l[i]:
# Scan left to right with stack of indices. For current x = nums[i], pop indices j from the
# stack while nums[j] < x AND (nums[j] | x) == x — those values are "dominated" by x in the
# usual stack sense for this problem. Then l[i] is the index below top after pops (-1 if empty).
#
# Right boundary r[i]:
# Scan right to left. Pop while (nums[stk.top()] | nums[i]) == nums[i] — elements whose bits are
# contained in nums[i] when OR-ing from the right perspective. r[i] is first index to the right
# that breaks being able to extend with OR still nums[i].
#
# Contribution
# Number of subarrays with OR exactly nums[i] that use i as the anchor in this enumeration is
# (i - l[i]) * (r[i] - i): choose left endpoint in (l[i], i] and right endpoint in [i, r[i]).
#
# Time complexity
# Each index pushed/popped O(1) amortized -> O(n) total for both passes.
#
# Space complexity
# O(n) for stack and boundary arrays.
#
# Edge cases
# - Single element [x]: OR = x, present -> good; formula gives (0 - (-1)) * (n - i) = 1 for n=1.
# - All zeros: OR = 0, 0 present -> good subarrays counted accordingly.
#
# Tests (examples)
# [4,2,3] -> 4 good subarrays per statement.
# [1,3,1] -> all 6 subarrays good.
#
# Possible improvements
# - Iterative stack only; same asymptotics.
# - If returning 32-bit in some languages, use 64-bit for the sum of products.
#
# Interview walkthrough
# 1) Characterize good subarray via OR equals some witness element.
# 2) Reformulate as counting subarrays with fixed OR = nums[i] using bit-subset constraints.
# 3) Two monotonic passes for left/right first violation.
# 4) Multiply interval lengths; total O(n).
# --- end notes ---

# @lc code=start
class Solution:
    def countGoodSubarrays(self, nums: list[int]) -> int:
        n = len(nums)
        left = [-1] * n
        stk: list[int] = []
        for i, x in enumerate(nums):
            while stk and nums[stk[-1]] < x and (nums[stk[-1]] | x) == x:
                stk.pop()
            left[i] = stk[-1] if stk else -1
            stk.append(i)

        right = [n] * n
        stk.clear()
        for i in range(n - 1, -1, -1):
            while stk and (nums[stk[-1]] | nums[i]) == nums[i]:
                stk.pop()
            right[i] = stk[-1] if stk else n
            stk.append(i)

        return sum((i - left[i]) * (right[i] - i) for i in range(n))


# @lc code=end
