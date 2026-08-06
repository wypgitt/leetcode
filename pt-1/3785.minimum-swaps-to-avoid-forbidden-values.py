#
# @lc app=leetcode id=3785 lang=python3
#
# [3785] Minimum Swaps to Avoid Forbidden Values
#
# https://leetcode.com/problems/minimum-swaps-to-avoid-forbidden-values/description/
#
# algorithms
# Hard (30.62%)
# Likes:    110
# Dislikes: 7
# Total Accepted:    11.6K
# Total Submissions: 37.9K
# Testcase Example:  '[1,2,3]\n[3,2,1]'
#
# You are given two integer arrays, nums and forbidden, each of length n.
# 
# You may perform the following operation any number of times (including
# zero):
# 
# 
# Choose two distinct indices i and j, and swap nums[i] with nums[j].
# 
# 
# Return the minimum number of swaps required such that, for every index i, the
# value of nums[i] is not equal to forbidden[i]. If no amount of swaps can
# ensure that every index avoids its forbidden value, return -1.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,2,3], forbidden = [3,2,1]
# 
# Output: 1
# 
# Explanation:
# 
# One optimal set of swaps:
# 
# 
# Select indices i = 0 and j = 1 in nums and swap them, resulting in nums = [2,
# 1, 3].
# After this swap, for every index i, nums[i] is not equal to forbidden[i].
# 
# 
# 
# Example 2:
# 
# 
# Input: nums = [4,6,6,5], forbidden = [4,6,5,5]
# 
# Output: 2
# 
# Explanation:
# One optimal set of swaps:
# 
# 
# Select indices i = 0 and j = 2 in nums and swap them, resulting in nums = [6,
# 6, 4, 5].
# Select indices i = 1 and j = 3 in nums and swap them, resulting in nums = [6,
# 5, 4, 6].
# After these swaps, for every index i, nums[i] is not equal to
# forbidden[i].
# 
# 
# 
# Example 3:
# 
# 
# Input: nums = [7,7], forbidden = [8,7]
# 
# Output: -1
# 
# Explanation:
# It is not possible to make nums[i] different from forbidden[i] for all
# indices.
# 
# Example 4:
# 
# 
# Input: nums = [1,2], forbidden = [2,1]
# 
# Output: 0
# 
# Explanation:
# 
# No swaps are required because nums[i] is already different from forbidden[i]
# for all indices, so the answer is 0.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n == nums.length == forbidden.length <= 10^5
# 1 <= nums[i], forbidden[i] <= 10^9
# 
# 
#

# @lc code=start
from collections import Counter, deque
from typing import List


class Solution:
    def minSwaps(self, nums: List[int], forbidden: List[int]) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We have two arrays:

            nums
            forbidden

        We may swap any two positions in `nums`.  We need the minimum number of
        swaps so that:

            nums[i] != forbidden[i]

        for every index `i`.  If this is impossible, return -1.

        Important distinction
        ---------------------
        We are not allowed to change the multiset of values in `nums`; swaps only
        permute those values.

        So the task is:

            Can we rearrange the values of nums so no index receives its
            forbidden value?

        and, if yes:

            What is the fewest swaps from the current arrangement?

        Feasibility check
        -----------------
        Consider one value `x`.

        Suppose `nums` contains `count_nums[x]` copies of `x`.
        These copies must all be placed into positions where:

            forbidden[i] != x

        The number of positions that allow value `x` is:

            n - count_forbidden[x]

        Therefore a necessary condition is:

            count_nums[x] <= n - count_forbidden[x]

        Equivalently:

            count_nums[x] + count_forbidden[x] <= n

        If this fails for any value, there are more copies of `x` than available
        safe positions for `x`, so the answer is impossible.

        This condition is also sufficient for this problem's value-vs-forbidden
        structure.  Every value only has one kind of forbidden position: indices
        whose forbidden value equals that same value.

        Which positions matter for the minimum swaps?
        ---------------------------------------------
        Let an index be "bad" if:

            nums[i] == forbidden[i]

        Every bad position must change value.  Positions that are already good
        do not need to move unless they are used as helpers.

        Let:

            bad_total = number of bad positions
            bad_count[x] = number of bad positions whose value is x

        Example:

            nums      = [4, 6, 6, 5]
            forbidden = [4, 6, 5, 5]

        Bad positions are:

            index 0: value 4
            index 1: value 6
            index 3: value 5

        so:

            bad_total = 3
            bad_count = {4: 1, 6: 1, 5: 1}

        Lower bound 1: bad positions
        ----------------------------
        Every bad position must participate in at least one swap; otherwise its
        value never changes.

        One swap touches at most two bad positions.

        Therefore:

            swaps >= ceil(bad_total / 2)

        Lower bound 2: same-value bad positions
        ---------------------------------------
        Consider all bad positions whose value is `x`.

        Swapping two of these positions with each other does nothing, because
        both contain `x`.  A single swap can fix at most one bad position of a
        particular value `x`.

        Therefore:

            swaps >= bad_count[x]

        for every value `x`, so:

            swaps >= max(bad_count.values())

        Final answer
        ------------
        If the feasibility check passes, the minimum number of swaps is:

            max(
                ceil(bad_total / 2),
                max_bad_count
            )

        Why this is achievable
        ----------------------
        There are two cases.

        Case 1: No value dominates the bad positions.

            max_bad_count <= bad_total / 2

        We can pair bad positions with different values.  Swapping such a pair
        fixes both positions:

            bad position with value a and forbidden a
            bad position with value b and forbidden b

        After swapping:

            first position gets b, and b != a
            second position gets a, and a != b

        So each swap fixes two bad positions, except possibly one final bad
        position when `bad_total` is odd.  That needs one more swap with a safe
        helper position.  Total is `ceil(bad_total / 2)`.

        Case 2: One value dominates the bad positions.

            max_bad_count > bad_total / 2

        Let the dominant value be `x`.  Every swap can fix at most one bad
        `x`-position, so at least `max_bad_count` swaps are required.  The
        feasibility condition guarantees enough safe helper positions for the
        leftover bad `x` positions: positions where the current value is not `x`
        and the forbidden value is not `x`.  Each such helper can be swapped
        with one bad `x` position.  Therefore `max_bad_count` swaps are enough.

        Data structure choice
        ---------------------
        We use `Counter` for frequency maps:

        * `nums_count`
        * `forbidden_count`
        * `bad_count`

        Values can be as large as `10^9`, so fixed-size arrays are not
        appropriate.  A hash map handles sparse large values naturally.

        Algorithm
        ---------
        1. Count values in `nums`.
        2. Count values in `forbidden`.
        3. For every value appearing in either array, check:

               nums_count[value] + forbidden_count[value] <= n

           If not, return -1.

        4. Scan all indices:
              if `nums[i] == forbidden[i]`, count it as bad.

        5. If there are no bad positions, return 0.

        6. Return:

               max((bad_total + 1) // 2, max(bad_count.values()))

        Correctness proof
        -----------------
        Lemma 1: If some value `x` has
        `count_nums[x] + count_forbidden[x] > n`, no valid arrangement exists.
        There are `count_nums[x]` copies of `x` that must be placed into indices
        where `forbidden[i] != x`.  Only `n - count_forbidden[x]` such indices
        exist.  If there are more copies than allowed positions, placement is
        impossible.

        Lemma 2: Every valid solution needs at least `ceil(bad_total / 2)`
        swaps.
        Every initially bad position must receive a different value, so it must
        be touched by a swap.  One swap touches at most two bad positions.

        Lemma 3: Every valid solution needs at least `max_bad_count` swaps.
        For a fixed value `x`, a swap can fix at most one initially bad position
        containing `x`.  Swapping two bad `x` positions does not change either
        value.  Therefore at least `bad_count[x]` swaps are needed for every
        `x`.

        Lemma 4: If the feasibility check passes, the algorithm's number of
        swaps is achievable.
        If no value dominates the bad positions, pair bad positions with
        different values and swap each pair.  This fixes two bad positions per
        swap, with at most one final helper swap when the number of bad
        positions is odd.  If one value dominates, pair as many dominant bad
        positions as possible with non-dominant bad positions, then use safe
        helper positions guaranteed by feasibility for the remaining dominant
        bad positions.  This uses exactly the maximum of the two lower bounds.

        Theorem: The algorithm returns the minimum number of swaps, or -1 if no
        valid arrangement exists.
        By Lemma 1, returning -1 on a failed feasibility check is correct.  If
        feasible, Lemma 2 and Lemma 3 prove the returned value is a lower bound,
        and Lemma 4 proves that lower bound can be achieved.  Therefore the
        returned value is optimal.

        Complexity analysis
        -------------------
        Let `n = len(nums)`.

        Counting frequencies and scanning bad positions are linear.

        Time:

            O(n)

        Space:

            O(n)

        in the worst case, because there may be O(n) distinct values.

        Edge cases
        ----------
        * Already valid:
          `bad_total = 0`, so return 0.

        * Impossible due to too many copies of one value:
          Example: `nums = [7, 7]`, `forbidden = [8, 7]`.
          There is only one position that allows value 7, but there are two
          copies of 7.

        * All bad positions have distinct values:
          Each swap can usually fix two bad positions, so the answer is
          `ceil(bad_total / 2)`.

        * Many bad positions have the same value:
          The answer is driven by `max_bad_count`.

        * Large values:
          Counters handle values up to `10^9` without coordinate compression.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              [1,2,3], [3,2,1]       -> 1
              [4,6,6,5], [4,6,5,5]   -> 2
              [7,7], [8,7]           -> -1
              [1,2], [2,1]           -> 0

        * One element valid and invalid.
        * Dominant bad value requiring helper positions.
        * Small arrays compared with brute-force BFS over permutations.

        Possible improvement
        --------------------
        The formula is already optimal at O(n).  A constructive version could
        also output the actual swaps, but this problem asks only for the
        minimum count.
        """

        n = len(nums)
        nums_count = Counter(nums)
        forbidden_count = Counter(forbidden)

        for value in nums_count.keys() | forbidden_count.keys():
            if nums_count[value] + forbidden_count[value] > n:
                return -1

        bad_count = Counter()
        bad_total = 0

        for value, blocked in zip(nums, forbidden):
            if value == blocked:
                bad_count[value] += 1
                bad_total += 1

        if bad_total == 0:
            return 0

        return max((bad_total + 1) // 2, max(bad_count.values()))
# @lc code=end


if __name__ == "__main__":
    def brute_force_min_swaps(test_nums: List[int], test_forbidden: List[int]) -> int:
        start = tuple(test_nums)
        n = len(test_nums)

        def is_valid(state: tuple[int, ...]) -> bool:
            return all(state[index] != test_forbidden[index] for index in range(n))

        if is_valid(start):
            return 0

        queue = deque([(start, 0)])
        seen = {start}

        while queue:
            state, swaps = queue.popleft()

            for first in range(n):
                for second in range(first + 1, n):
                    next_state = list(state)
                    next_state[first], next_state[second] = (
                        next_state[second],
                        next_state[first],
                    )
                    next_tuple = tuple(next_state)

                    if next_tuple in seen:
                        continue

                    if is_valid(next_tuple):
                        return swaps + 1

                    seen.add(next_tuple)
                    queue.append((next_tuple, swaps + 1))

        return -1

    solution = Solution()

    fixed_tests = [
        ([1, 2, 3], [3, 2, 1], 1),
        ([4, 6, 6, 5], [4, 6, 5, 5], 2),
        ([7, 7], [8, 7], -1),
        ([1, 2], [2, 1], 0),
        ([1], [1], -1),
        ([1], [2], 0),
        ([1, 1, 2, 3], [1, 1, 4, 4], 2),
        ([1, 2, 3, 4], [1, 2, 3, 4], 2),
    ]

    for test_nums, test_forbidden, expected in fixed_tests:
        assert solution.minSwaps(test_nums, test_forbidden) == expected

    brute_force_cases = [
        ([1, 2, 3], [1, 2, 3]),
        ([1, 1, 2, 2], [1, 2, 1, 2]),
        ([1, 1, 2, 3], [1, 1, 4, 4]),
        ([1, 2, 1, 3], [1, 1, 3, 4]),
        ([1, 2, 3, 1], [2, 1, 1, 3]),
    ]

    for test_nums, test_forbidden in brute_force_cases:
        expected = brute_force_min_swaps(test_nums, test_forbidden)
        assert solution.minSwaps(test_nums, test_forbidden) == expected
