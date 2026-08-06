#
# @lc app=leetcode id=3862 lang=python3
#
# [3862] Find the Smallest Balanced Index
#
# https://leetcode.com/problems/find-the-smallest-balanced-index/description/
#
# algorithms
# Medium (19.26%)
# Likes:    92
# Dislikes: 18
# Total Accepted:    36.8K
# Total Submissions: 191K
# Testcase Example:  '[2,1,2]'
#
# You are given an integer array nums.
# 
# An index i is balanced if the sum of elements strictly to the left of i
# equals the product of elements strictly to the right of i.
# 
# If there are no elements to the left, the sum is considered as 0. Similarly,
# if there are no elements to the right, the product is considered as 1.
# 
# Return an integer denoting the smallest balanced index. If no balanced index
# exists, return -1.
# 
# 
# Example 1:
# 
# 
# Input: nums = [2,1,2]
# 
# Output: 1
# 
# Explanation:
# 
# For index i = 1:
# 
# 
# Left sum = nums[0] = 2
# Right product = nums[2] = 2
# Since the left sum equals the right product, index 1 is balanced.
# 
# 
# No smaller index satisfies the condition, so the answer is 1.
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,8,2,2,5]
# 
# Output: 2
# 
# Explanation:
# 
# For index i = 2:
# 
# 
# Left sum = 2 + 8 = 10
# Right product = 2 * 5 = 10
# Since the left sum equals the right product, index 2 is balanced.
# 
# 
# No smaller index satisfies the condition, so the answer is 2.
# 
# 
# Example 3:
# 
# 
# Input: nums = [1]
# 
# Output: -1
# For index i = 0:
# 
# 
# The left side is empty, so the left sum is 0.
# The right side is empty, so the right product is 1.
# Since the left sum does not equal the right product, index 0 is not
# balanced.
# 
# Therefore, no balanced index exists and the answer is -1.
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10^5
# 1 <= nums[i] <= 10^9
# 
# 
#

# @lc code=start
class Solution:
    def smallestBalancedIndex(self, nums: list[int]) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given an array `nums` of positive integers.

        An index `i` is balanced when:

            sum(nums[0 : i]) == product(nums[i + 1 : n])

        The elements strictly to the left are used for the sum.
        The elements strictly to the right are used for the product.

        Special empty-side rules:

        * If there are no elements on the left, the left sum is 0.
        * If there are no elements on the right, the right product is 1.

        We must return the smallest balanced index, or -1 if none exists.

        Example:

            nums = [2, 1, 2]

            i = 1:
                left sum     = 2
                right product = 2

            so the answer is 1.

        Key challenge
        -------------
        A naive suffix-product array can become enormous.

        With constraints:

            n <= 100000
            nums[i] <= 10^9

        the product of many elements can have hundreds of thousands of digits.
        Even though Python supports big integers, building such a product is far
        too expensive and unnecessary.

        Key observation: cap the product
        --------------------------------
        The left side is always a sum of some elements, so it can never exceed:

            total_sum = sum(nums)

        Therefore, if a right product ever becomes larger than `total_sum`, it
        can never equal any left sum.

        So we safely cap every running product at:

            cap = total_sum + 1

        Meaning:

            right_product == cap

        represents "the true product is greater than total_sum".

        This preserves correctness because no left sum can be `cap` or larger.

        Direction of scan
        -----------------
        We need the smallest balanced index.

        The right product is naturally maintained while scanning from right to
        left:

            before processing i:
                right_product = product(nums[i + 1 : n])
                right_sum     = sum(nums[i + 1 : n])

        Then:

            left_sum = total_sum - nums[i] - right_sum

        So we can check whether:

            left_sum == right_product

        If yes, `i` is balanced.

        Since we scan from right to left, we keep assigning `answer = i` whenever
        we find a balanced index. Later discoveries are smaller indices, so the
        final saved answer is the smallest balanced index.

        Why maintain `right_sum`?
        -------------------------
        We could also scan left-to-right if we stored all suffix products.
        Instead, `right_sum` lets us compute the left sum from `total_sum` during
        a right-to-left scan:

            total_sum = left_sum + nums[i] + right_sum

        Therefore:

            left_sum = total_sum - nums[i] - right_sum

        This avoids a prefix-sum array and keeps extra space O(1).

        Data structure choice
        ---------------------
        We use only scalar variables:

        * `total_sum`: maximum possible left sum and formula source
        * `cap`: sentinel value for "product too large"
        * `right_product`: capped product of elements strictly to the right
        * `right_sum`: sum of elements strictly to the right
        * `answer`: best/smallest balanced index found so far

        No stack, queue, heap, hash map, or DP table is needed because each index
        only depends on aggregate information from its right side plus the total
        sum.

        Algorithm
        ---------
        1. Compute `total_sum = sum(nums)`.
        2. Set:

               cap = total_sum + 1
               right_product = 1
               right_sum = 0
               answer = -1

           Initially, before the last index, the right side is empty, so the
           right product is 1 and the right sum is 0.

        3. Scan indices from `n - 1` down to `0`.
        4. For the current index `i`, compute:

               left_sum = total_sum - nums[i] - right_sum

        5. If `left_sum == right_product`, record:

               answer = i

        6. Add `nums[i]` into the right-side aggregates for the next iteration:

               right_sum += nums[i]
               right_product = min(cap, right_product * nums[i])

        7. Return `answer`.

        Walkthrough
        -----------
        For:

            nums = [2, 8, 2, 2, 5]
            total_sum = 19
            cap = 20

        Scan right to left:

            i = 4:
                left_sum = 14
                right_product = 1
                not balanced

            update right side: sum = 5, product = 5

            i = 3:
                left_sum = 12
                right_product = 5
                not balanced

            update right side: sum = 7, product = 10

            i = 2:
                left_sum = 10
                right_product = 10
                balanced, answer = 2

        No smaller balanced index appears, so return 2.

        Correctness proof
        -----------------
        Lemma 1:
        At the start of each iteration for index `i`, `right_sum` equals the sum
        of elements strictly to the right of `i`.

        Proof:
        Initially, before processing the last index, there are no elements to
        the right, so `right_sum = 0`. After processing index `i`, we add
        `nums[i]` to `right_sum`, so at the next iteration `i - 1`, `right_sum`
        equals the sum of elements strictly to the right of `i - 1`. By
        induction, the invariant holds for every index.

        Lemma 2:
        At the start of each iteration for index `i`, `right_product` equals the
        true product of elements strictly to the right of `i` if that product is
        at most `total_sum`; otherwise it equals `cap`.

        Proof:
        Initially, the right side is empty, and the empty product is 1, which is
        represented exactly. After processing index `i`, the next true product
        is the previous true product multiplied by `nums[i]`. The algorithm
        stores this value exactly when it is at most `total_sum`; otherwise it
        stores `cap = total_sum + 1`. Since all numbers are positive, once a
        product exceeds `total_sum`, multiplying by more positive integers can
        never bring it back down. Thus the capped representation remains valid.

        Lemma 3:
        For each index `i`, the algorithm computes the correct left sum.

        Proof:
        The total array sum can be decomposed as:

            total_sum = sum(left of i) + nums[i] + sum(right of i)

        By Lemma 1, `right_sum` is the right-side sum. Rearranging gives:

            sum(left of i) = total_sum - nums[i] - right_sum

        which is exactly the formula used by the algorithm.

        Lemma 4:
        The algorithm identifies exactly the balanced indices.

        Proof:
        By Lemma 3, `left_sum` is correct. By Lemma 2, `right_product` is either
        the exact right product or a sentinel greater than every possible left
        sum. If the true right product is greater than `total_sum`, equality is
        impossible and the sentinel correctly prevents a match. Otherwise,
        `right_product` is exact, so `left_sum == right_product` holds exactly
        when index `i` is balanced.

        Lemma 5:
        The returned balanced index is the smallest one.

        Proof:
        The scan visits indices in descending order. Whenever a balanced index
        is found, `answer` is set to that index. Any later balanced index in the
        scan has a smaller numeric index and overwrites the previous answer.
        Therefore, after the scan finishes, `answer` is the smallest balanced
        index found. If no balanced index is found, it remains -1.

        Theorem:
        The algorithm returns the smallest balanced index, or -1 if none exists.

        Proof:
        Lemma 4 shows that every and only balanced indices are detected. Lemma 5
        shows that among detected indices, the final answer is the smallest. If
        no index is detected, returning -1 is correct.

        Complexity analysis
        -------------------
        Let `n = len(nums)`.

        Time:

            O(n)

        Reason:
        We compute the total sum once and scan the array once from right to
        left. Every operation inside the scan is O(1) because `right_product` is
        capped at `total_sum + 1` instead of growing without bound.

        Space:

            O(1)

        Reason:
        The algorithm uses only a fixed number of scalar variables regardless of
        input size.

        Edge cases
        ----------
        * One element:
          Left sum is 0 and right product is 1, so no balanced index exists.

        * Balanced at the last index:
          Right product is the empty product 1. The last index is balanced if
          the sum of all previous elements is 1.

        * Balanced at index 0:
          Left sum is 0. Since all numbers are positive, the right product is at
          least 1 when there are right elements, so index 0 cannot be balanced.

        * Very large numbers:
          Products are capped at `total_sum + 1`, avoiding giant integers.

        * Multiple balanced indices:
          The right-to-left scan overwrites `answer` with smaller indices, so
          the smallest one is returned.

        Test strategy
        -------------
        Useful tests:

            [2, 1, 2]       -> 1
            [2, 8, 2, 2, 5] -> 2
            [1]             -> -1
            [1, 1]          -> 1
            [2, 1]          -> -1
            [1, 1, 1]       -> 1
            [5, 10, 1]      -> -1
            [1, 2, 3, 6, 1] -> -1
            [1, 1, 1, 1, 3] -> 3

        For confidence in a local test harness, compare this O(n) solution
        against a brute-force implementation on small random arrays.

        Possible improvements
        ---------------------
        A suffix-product array would also work if products were capped, but it
        would use O(n) extra space. The right-to-left scan is better because it
        keeps the same O(n) time while reducing extra space to O(1).
        """

        total_sum = sum(nums)
        cap = total_sum + 1

        right_product = 1
        right_sum = 0
        answer = -1

        for i in range(len(nums) - 1, -1, -1):
            left_sum = total_sum - nums[i] - right_sum

            if left_sum == right_product:
                answer = i

            right_sum += nums[i]
            right_product = min(cap, right_product * nums[i])

        return answer
# @lc code=end
