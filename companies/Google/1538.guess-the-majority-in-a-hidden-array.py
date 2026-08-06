#
# @lc app=leetcode id=1538 lang=python3
#
# [1538] Guess the Majority in a Hidden Array
#
# https://leetcode.com/problems/guess-the-majority-in-a-hidden-array/description/
#
# algorithms
# Medium (69.00%)
# Likes:    148
# Dislikes: 122
# Total Accepted:    5.3K
# Total Submissions: 7.7K
# Testcase Example:  "[0,0,1,0,1,1,1,1]"
#
#
# We have an integer array nums, where all the integers in nums are 0 or
# 1. You will not be given direct access to the array, instead, you will
# have an API ArrayReader which have the following functions:
#
# int query(int a, int b, int c, int d): where 0 <= a < b < c < d <
# ArrayReader.length(). The function returns the distribution of the value
# of the 4 elements and returns:
#
# 4 : if the values of the 4 elements are the same (0 or 1).
#
# 2 : if three elements have a value equal to 0 and one element has value
# equal to 1 or vice versa.
#
# 0 : if two element have a value equal to 0 and two elements have a value
# equal to 1.
#
# int length(): Returns the size of the array.
#
# You are allowed to call query() 2 * n times at most where n is equal to
# ArrayReader.length().
#
# Return any index of the most frequent value in nums, in case of tie,
# return -1.
#
# Example 1:
#
# Input: nums = [0,0,1,0,1,1,1,1]
# Output: 5
# Explanation: The following calls to the API
# reader.length() // returns 8 because there are 8 elements in the hidden
# array.
# reader.query(0,1,2,3) // returns 2 this is a query that compares the
# elements nums[0], nums[1], nums[2], nums[3]
# // Three elements have a value equal to 0 and one element has value
# equal to 1 or viceversa.
# reader.query(4,5,6,7) // returns 4 because nums[4], nums[5], nums[6],
# nums[7] have the same value.
# we can infer that the most frequent value is found in the last 4
# elements.
# Index 2, 4, 6, 7 is also a correct answer.
#
# Example 2:
#
# Input: nums = [0,0,1,1,0]
# Output: 0
#
# Example 3:
#
# Input: nums = [1,0,1,0,1,0,1,0]
# Output: -1
#
# Constraints:
#
# 5 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 1
#
# Follow up: What is the minimum number of calls needed to find the
# majority element?
#
# @lc code=start
try:
    ArrayReader
except NameError:

    class ArrayReader:
        def query(self, a: int, b: int, c: int, d: int) -> int:
            return 0

        def length(self) -> int:
            return 0


class Solution:
    def guessMajority(self, reader: "ArrayReader") -> int:
        """
        Interview explanation:
        Premium. Hidden 0/1 array; find any index of the strict majority value
        (or -1 if tie). ArrayReader.query(a,b,c,d) returns how many among the
        four equal the most frequent value in that quadruple. Classify each
        nums[i] equal/unequal to nums[0] via relative queries.

        Algorithm:
        - q=query(0,1,2,3); for i>=4 same[i]=(query(1,2,3,i)==q) meaning
          nums[i]==nums[0].
        - For i in 1..3: same[i] by comparing query swapping 0↔i against
          query(1,2,3,4).
        - Return 0 if same-count wins, else first differing index; -1 on tie.

        Complexity: O(n) queries, O(n) space.
        """
        n = reader.length()
        same = [False] * n
        same[0] = True
        q = reader.query(0, 1, 2, 3)
        for i in range(4, n):
            same[i] = reader.query(1, 2, 3, i) == q
        if n >= 5:
            q1234 = reader.query(1, 2, 3, 4)
            same[1] = reader.query(0, 2, 3, 4) == q1234
            same[2] = reader.query(0, 1, 3, 4) == q1234
            same[3] = reader.query(0, 1, 2, 4) == q1234
        else:
            # n == 4: only one possible query; majority => >=3 equal
            if q == 4:
                return 0
            # three equal, one different — cannot localize odd one with one query;
            # return 0 (correct if nums[0] in majority, which holds for 3 of 4 cases).
            # Prefer returning -1 only on true ties; here majority exists.
            return 0

        cnt_same = sum(same)
        cnt_diff = n - cnt_same
        if cnt_same == cnt_diff:
            return -1
        if cnt_same > cnt_diff:
            return 0
        for i, v in enumerate(same):
            if not v:
                return i
        return -1
# @lc code=end
