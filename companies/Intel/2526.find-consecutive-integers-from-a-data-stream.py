#
# @lc app=leetcode id=2526 lang=python3
#
# [2526] Find Consecutive Integers from a Data Stream
#
# https://leetcode.com/problems/find-consecutive-integers-from-a-data-stream/description/
#
# algorithms
# Medium (51.55%)
# Likes:    345
# Dislikes: 41
# Total Accepted:    39K
# Total Submissions: 75.7K
# Testcase Example:  "[\"DataStream\",\"consec\",\"consec\",\"consec\",\"consec\"]\n[[4,3],[4],[4],[4],[3]]"
#
# For a stream of integers, implement a data structure that checks if the last k
# integers parsed in the stream are equal to value.
#
# Implement the DataStream class:
#
#
# DataStream(int value, int k) Initializes the object with an empty integer
# stream and the two integers value and k.
#
#
# boolean consec(int num) Adds num to the stream of integers. Returns true if
# the last k integers are equal to value, and false otherwise. If there are less
# than k integers, the condition does not hold true, so returns false.
#
#
#
# Example 1:
#
# Input
# ["DataStream", "consec", "consec", "consec", "consec"]
# [[4, 3], [4], [4], [4], [3]]
# Output
# [null, false, false, true, false]
#
# Explanation
# DataStream dataStream = new DataStream(4, 3); //value = 4, k = 3
# dataStream.consec(4); // Only 1 integer is parsed, so returns False.
# dataStream.consec(4); // Only 2 integers are parsed.
#                       // Since 2 is less than k, returns False.
# dataStream.consec(4); // The 3 integers parsed are all equal to value, so
# returns True.
# dataStream.consec(3); // The last k integers parsed in the stream are [4,4,3].
#                       // Since 3 is not equal to value, it returns False.
#
#
#
# Constraints:
#
#
# 1 <= value, num <= 10^9
#
#
# 1 <= k <= 10^5
#
#
# At most 10^5 calls will be made to consec.
#

# @lc code=start
class DataStream:
    def __init__(self, value: int, k: int):
        """
        Interview explanation:
        Stream checker: after each append, report whether the last k integers
        all equal a fixed value.

        Algorithm:
        - Track streak of consecutive `value` counts; reset on mismatch.

        Complexity: O(1) per call, O(1) space.
        """
        self.value = value
        self.k = k
        self.streak = 0

    def consec(self, num: int) -> bool:
        """
        Interview explanation:
        Append num; true iff the last k stream values equal value.

        Algorithm:
        - Increment streak if num == value else reset to 0; compare to k.

        Complexity: O(1) time, O(1) space.
        """
        if num == self.value:
            self.streak += 1
        else:
            self.streak = 0
        return self.streak >= self.k


# Your DataStream object will be instantiated and called as such:
# obj = DataStream(value, k)
# param_1 = obj.consec(num)
# @lc code=end
