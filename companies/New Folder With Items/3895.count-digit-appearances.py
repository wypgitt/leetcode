#
# @lc app=leetcode id=3895 lang=python3
#
# [3895] Count Digit Appearances
#
# https://leetcode.com/problems/count-digit-appearances/description/
#
# algorithms
# Medium (86.50%)
# Likes:    35
# Dislikes: 4
# Total Accepted:    39.9K
# Total Submissions: 46.1K
# Testcase Example:  '[12,54,32,22]\n2'
#
# You are given an integer array nums and an integer digit.
# 
# Return the total number of times digit appears in the decimal representation
# of all elements in nums.
# 
# 
# Example 1:
# 
# 
# Input: nums = [12,54,32,22], digit = 2
# 
# Output: 4
# 
# Explanation:
# 
# The digit 2 appears once in 12 and 32, and twice in 22. Thus, the total
# number of times digit 2 appears is 4.
# 
# 
# Example 2:
# 
# 
# Input: nums = [1,34,7], digit = 9
# 
# Output: 0
# 
# Explanation:
# 
# The digit 9 does not appear in the decimal representation of any element in
# nums, so the total number of times digit 9 appears is 0.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 1000
# 1 <= nums[i] <= 10^6​​​​​​​
# 0 <= digit <= 9
# 
# 
#

# @lc code=start
class Solution:
    def countDigitOccurrences(self, nums: list[int], digit: int) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given:

        * an integer array `nums`
        * one decimal digit `digit`, from 0 to 9

        We need to count how many times that digit appears when every number in
        `nums` is written in normal base-10 decimal form.

        Example:
            nums = [12, 54, 32, 22], digit = 2

            "12" has one '2'
            "54" has zero '2'
            "32" has one '2'
            "22" has two '2's

            total = 1 + 0 + 1 + 2 = 4

        Key observation
        ---------------
        This is not asking for a mathematical range count like "how many 2s
        appear from 1 to n".  It only asks us to inspect the specific numbers in
        the input array.

        The constraints are small:

            len(nums) <= 1000
            nums[i] <= 10^6

        Each number has at most 7 decimal digits.  So the total amount of data to
        inspect is tiny: at most about 7000 characters.

        Because of that, the cleanest solution is to convert each number to a
        string and use the built-in `count` method.

        Why choose string conversion?
        -----------------------------
        In an interview, this is the important judgment call:

        * Decimal representation is naturally a string concept.
        * Python's `str(x).count(ch)` is simple, readable, and implemented
          efficiently.
        * The constraints are nowhere near large enough to require a more
          complicated arithmetic digit extraction loop.

        An arithmetic solution is also possible:

            while x > 0:
                if x % 10 == digit:
                    answer += 1
                x //= 10

        But the string version is less error-prone, especially for digit `0`.
        Since nums[i] >= 1, there is no special case for the number 0 itself.

        Algorithm
        ---------
        1. Convert the target digit into a character:

               target = str(digit)

        2. Initialize `total = 0`.
        3. For every number in `nums`:

               total += str(number).count(target)

        4. Return `total`.

        Correctness proof
        -----------------
        We prove that the algorithm returns the exact number of appearances of
        `digit`.

        Lemma 1: For any number `x`, `str(x)` is exactly the decimal
        representation whose digits the problem asks us to inspect.
        The problem defines appearances in the decimal representation of each
        element.  Python's `str` on a positive integer produces that standard
        decimal representation without leading zeroes.

        Lemma 2: For any number `x`, `str(x).count(str(digit))` equals the
        number of times `digit` appears in `x`.
        By Lemma 1, `str(x)` contains exactly the decimal digits of `x`.  The
        string `count` method counts all positions in that representation whose
        character equals the target digit.

        Lemma 3: Summing the counts for all numbers gives the total number of
        appearances across the whole array.
        Each digit appearance belongs to exactly one input number, and the
        numbers are counted independently.  Therefore adding the per-number
        counts counts every valid appearance once.

        Theorem: The algorithm returns the required answer.
        By Lemma 2, each term added by the algorithm is the exact occurrence
        count for one number.  By Lemma 3, their sum is exactly the total count
        over all elements of `nums`.

        Complexity analysis
        -------------------
        Let:
            n = len(nums)
            D = maximum number of decimal digits in any nums[i]

        Converting a number to a string costs O(D), and counting within that
        string also costs O(D).  We do this for each number.

        Total time:  O(n * D)
        Total space: O(D) extra space for each temporary string

        Under the given constraints, D <= 7, so this is effectively linear in
        the number of input elements.

        Edge cases
        ----------
        * The digit does not appear anywhere:
              nums = [1, 34, 7], digit = 9 -> 0

        * The digit appears multiple times in one number:
              nums = [222], digit = 2 -> 3

        * Counting zero:
              nums = [10, 100, 101], digit = 0 -> 4

          This works naturally with strings.  We count zeroes that are actually
          present inside the decimal representation, not imaginary leading
          zeroes.

        * Single-element array:
              nums = [5], digit = 5 -> 1

        Test strategy
        -------------
        Useful tests include:

        * sample cases from the prompt
        * every digit from 0 through 9
        * numbers with repeated target digits
        * numbers with no target digits
        * numbers containing zero when digit is 0

        Possible improvement?
        ---------------------
        For this exact problem, the string solution is already ideal: short,
        readable, and easily fast enough.  If the problem instead asked for a
        count over a huge range like [1, n], then we would use a mathematical
        digit-DP/counting formula.  That heavier approach is unnecessary here.
        """

        target = str(digit)
        return sum(str(number).count(target) for number in nums)
# @lc code=end
