#
# @lc app=leetcode id=368 lang=python3
#
# [368] Largest Divisible Subset
#
# https://leetcode.com/problems/largest-divisible-subset/description/
#
# algorithms
# Medium (49.62%)
# Likes:    6883
# Dislikes: 329
# Total Accepted:    503.5K
# Total Submissions: 1M
# Testcase Example:  '[1,2,3]'
#
# Given a set of distinct positive integers nums, return the largest subset
# answer such that every pair (answer[i], answer[j]) of elements in this subset
# satisfies:
# 
# 
# answer[i] % answer[j] == 0, or
# answer[j] % answer[i] == 0
# 
# 
# If there are multiple solutions, return any of them.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,2,3]
# Output: [1,2]
# Explanation: [1,3] is also accepted.
# 
# 
# Example 2:
# 
# 
# Input: nums = [1,2,4,8]
# Output: [1,2,4,8]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 1000
# 1 <= nums[i] <= 2 * 10^9
# All the integers in nums are unique.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def largestDivisibleSubset(self, nums: List[int]) -> List[int]:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given a list of distinct positive integers.  We need to return
        the largest subset such that for every pair of numbers `(a, b)` in the
        subset:

            a % b == 0 or b % a == 0

        If several largest subsets exist, any one of them is acceptable.

        Key observation
        ---------------
        Sort the numbers in increasing order.

        After sorting, if we build a subset as an increasing sequence:

            x1 <= x2 <= x3 <= ... <= xt

        then the divisibility condition we need between adjacent chosen numbers
        is:

            x_next % x_previous == 0

        The important transitive property is:

            if b % a == 0 and c % b == 0, then c % a == 0

        So once the sorted subset forms a chain where every number is divisible
        by the previous number, every earlier/later pair in that chain is also
        divisible.

        That means the problem becomes:

            Find the longest divisible chain in the sorted array.

        Why dynamic programming?
        ------------------------
        For each number `nums[i]`, ask:

            What is the largest divisible subset that ends at nums[i]?

        If a previous number `nums[j]` divides `nums[i]`, then any valid subset
        ending at `nums[j]` can be extended by `nums[i]`.

        Recurrence:

            dp[i] = 1 + max(dp[j]) over all j < i where nums[i] % nums[j] == 0

        If no previous number divides `nums[i]`, then:

            dp[i] = 1

        We also store a parent pointer so we can reconstruct the actual subset,
        not just its length.

        Data structures
        ---------------
        * `dp[i]`:
          Length of the largest divisible subset ending at sorted position `i`.

        * `parent[i]`:
          Previous index in that best subset ending at `i`.
          If `parent[i] == -1`, `nums[i]` starts the chain.

        * `best_index`:
          Index where the longest chain ends.

        Why this data structure choice?
        -------------------------------
        We need to compare each number against smaller numbers.  A simple array
        DP is direct and reliable because `n <= 1000`, so O(n^2) pair checks are
        well within the constraint.

        A graph formulation would create edges `j -> i` when `nums[j]` divides
        `nums[i]`, then find the longest path in a DAG.  The DP below is exactly
        that idea without explicitly storing the graph, so it saves space and is
        easier to explain in an interview.

        Algorithm
        ---------
        1. Sort `nums`.
        2. Initialize:

               dp = [1] * n
               parent = [-1] * n

           Every number alone is a valid subset of length 1.

        3. For each index `i` from left to right:
              For every previous index `j < i`:
                  If `nums[i] % nums[j] == 0`, then `nums[i]` can extend the
                  chain ending at `j`.

                  If `dp[j] + 1 > dp[i]`, update:

                      dp[i] = dp[j] + 1
                      parent[i] = j

        4. Track the index with the largest `dp[i]`.
        5. Reconstruct the subset by walking parent pointers from `best_index`.
        6. Reverse the reconstructed list, because parent pointers walk from
           largest number back to smallest number.

        Walkthrough
        -----------
        For:

            nums = [1, 2, 4, 8]

        After sorting, the order is unchanged.

        * 2 is divisible by 1, so chain [1, 2] has length 2.
        * 4 is divisible by 1 and 2.  Extending [1, 2] gives [1, 2, 4].
        * 8 is divisible by 1, 2, and 4.  Extending [1, 2, 4] gives
          [1, 2, 4, 8].

        Correctness proof
        -----------------
        Lemma 1: In a sorted divisible chain, if each selected number is
        divisible by the selected number immediately before it, then every pair
        in the chain satisfies the problem condition.
        Divisibility is transitive.  If `x2 % x1 == 0` and `x3 % x2 == 0`, then
        `x3` is also divisible by `x1`.  Repeating this argument proves every
        later number is divisible by every earlier number.

        Lemma 2: `dp[i]` equals the length of the largest divisible subset that
        ends at `nums[i]`.
        Any valid subset ending at `nums[i]` must have some previous last number
        `nums[j]` with `j < i` and `nums[i] % nums[j] == 0`, unless the subset
        has only `nums[i]`.  The recurrence checks every such `j` and chooses
        the best extendable subset.  Therefore `dp[i]` is optimal for subsets
        ending at `i`.

        Lemma 3: The best value among all `dp[i]` is the length of the largest
        divisible subset overall.
        Every non-empty subset has a largest element after sorting, so it ends
        at some index `i`.  By Lemma 2, that subset's best possible length is
        represented by `dp[i]`.  Taking the maximum over all endpoints gives the
        global optimum.

        Theorem: The algorithm returns a largest divisible subset.
        By Lemma 3, `best_index` identifies an endpoint of an optimal-length
        subset.  The `parent` pointers record exactly the choices that produced
        the DP length at each index.  Walking those pointers reconstructs a
        valid chain of optimal length.  By Lemma 1, that chain satisfies the
        pairwise divisibility requirement.

        Complexity analysis
        -------------------
        Let n be `len(nums)`.

        Sorting:

            O(n log n)

        Dynamic programming:

            O(n^2)

        because for each `i`, we scan all `j < i`.

        Reconstruction:

            O(n)

        Total time:

            O(n^2)

        The O(n^2) DP dominates sorting for the given constraints.

        Space:

            O(n)

        for `dp`, `parent`, and the reconstructed answer.

        Edge cases
        ----------
        * One number:
          Return that number.

        * No two numbers divide each other:
          Any single number is a valid largest subset.

        * Multiple valid answers:
          The problem allows returning any one.  The DP may choose one depending
          on tie order.

        * Input is unsorted:
          Sorting is required so divisibility can be treated as a forward chain
          from smaller numbers to larger numbers.

        * Large values:
          Values can be up to 2 * 10^9, but we only use modulo operations, so
          no special numeric handling is needed in Python.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              [1, 2, 3]       -> [1, 2] or [1, 3]
              [1, 2, 4, 8]    -> [1, 2, 4, 8]

        * Single element:
              [7]             -> [7]

        * No chain longer than 1:
              [5, 7, 11]      -> any one element

        * Unsorted input:
              [8, 1, 4, 2]    -> [1, 2, 4, 8]

        * Competing chains:
              [1, 2, 3, 4, 9] -> [1, 2, 4] or [1, 3, 9]

        Possible improvements
        ---------------------
        O(n^2) is the standard solution for this constraint.  There are number
        theory optimizations for special value ranges, but here values are large
        and n is only 1000, so the simple DP is the best interview choice:
        correct, readable, and comfortably efficient.
        """

        nums.sort()
        n = len(nums)

        dp = [1] * n
        parent = [-1] * n
        best_index = 0

        for i in range(n):
            for j in range(i):
                if nums[i] % nums[j] == 0 and dp[j] + 1 > dp[i]:
                    dp[i] = dp[j] + 1
                    parent[i] = j

            if dp[i] > dp[best_index]:
                best_index = i

        answer = []
        current = best_index
        while current != -1:
            answer.append(nums[current])
            current = parent[current]

        answer.reverse()
        return answer
# @lc code=end


if __name__ == "__main__":
    def is_valid_divisible_subset(subset: List[int]) -> bool:
        for i in range(len(subset)):
            for j in range(i + 1, len(subset)):
                a = subset[i]
                b = subset[j]
                if a % b != 0 and b % a != 0:
                    return False
        return True

    def assert_solution(nums: List[int], expected_length: int) -> None:
        result = Solution().largestDivisibleSubset(nums[:])
        assert len(result) == expected_length, (nums, result)
        assert set(result).issubset(set(nums)), (nums, result)
        assert is_valid_divisible_subset(result), (nums, result)

    assert_solution([1, 2, 3], 2)
    assert_solution([1, 2, 4, 8], 4)
    assert_solution([7], 1)
    assert_solution([5, 7, 11], 1)
    assert_solution([8, 1, 4, 2], 4)
    assert_solution([1, 2, 3, 4, 9], 3)
    assert_solution([3, 4, 16, 8], 3)
