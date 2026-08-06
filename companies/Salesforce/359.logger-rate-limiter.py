#
# @lc app=leetcode id=359 lang=python3
#
# [359] Logger Rate Limiter
#
# https://leetcode.com/problems/logger-rate-limiter/description/
#
# algorithms
# Easy (76.87%)
# Likes:    1812
# Dislikes: 198
# Total Accepted:    400.8K
# Total Submissions: 521.4K
# Testcase Example:  "[\"Logger\",\"shouldPrintMessage\",\"shouldPrintMessage\",\"shouldPrintMessage\",\"shouldPrintMessage\",\"shouldPrintMessage\",\"shouldPrintMessage\"]\n[[],[1,\"foo\"],[2,\"bar\"],[3,\"foo\"],[8,\"bar\"],[10,\"foo\"],[11,\"foo\"]]"
#
#
# Design a logger system that receives a stream of messages along with
# their timestamps. Each unique message should only be printed at most
# every 10 seconds (i.e. a message printed at timestamp t will prevent
# other identical messages from being printed until timestamp t + 10).
#
# All messages will come in chronological order. Several messages may
# arrive at the same timestamp.
#
# Implement the Logger class:
#
# Logger() Initializes the logger object.
#
# bool shouldPrintMessage(int timestamp, string message) Returns true if
# the message should be printed in the given timestamp, otherwise returns
# false.
#
# Example 1:
#
# Input
# ["Logger", "shouldPrintMessage", "shouldPrintMessage",
# "shouldPrintMessage", "shouldPrintMessage", "shouldPrintMessage",
# "shouldPrintMessage"]
# [[], [1, "foo"], [2, "bar"], [3, "foo"], [8, "bar"], [10, "foo"], [11,
# "foo"]]
# Output
# [null, true, true, false, false, false, true]
#
# Explanation
# Logger logger = new Logger();
# logger.shouldPrintMessage(1, "foo");  // return true, next allowed
# timestamp for "foo" is 1 + 10 = 11
# logger.shouldPrintMessage(2, "bar");  // return true, next allowed
# timestamp for "bar" is 2 + 10 = 12
# logger.shouldPrintMessage(3, "foo");  // 3 < 11, return false
# logger.shouldPrintMessage(8, "bar");  // 8 < 12, return false
# logger.shouldPrintMessage(10, "foo"); // 10 < 11, return false
# logger.shouldPrintMessage(11, "foo"); // 11 >= 11, return true, next
# allowed timestamp for "foo" is 11 + 10 = 21
#
# Constraints:
#
# 0 <= timestamp <= 10^9
#
# Every timestamp will be passed in non-decreasing order (chronological
# order).
#
# 1 <= message.length <= 30
#
# At most 10^4 calls will be made to shouldPrintMessage.
#
# @lc code=start
class Logger:
    """
    Interview explanation:
    Hashmap message -> last printed timestamp. shouldPrintMessage returns True
    and updates the stamp when never seen or timestamp - last >= 10.

    Algorithm:
    - last: dict[str, int].
    - If msg not in last or timestamp - last[msg] >= 10: update and True else False.

    Complexity: O(1) per call, O(U) space for unique messages.
    """

    def __init__(self):
        """
        Interview explanation:
        Map each message to the last timestamp it was allowed to print.

        Algorithm:
        - last: empty dict[str, int].

        Complexity: O(1) init, O(U) space for unique messages over time.
        """
        self.last: dict[str, int] = {}

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        """
        Interview explanation:
        Allow print if message is new or ≥10 seconds since last print; update
        the stored timestamp on success.

        Algorithm:
        - If seen and timestamp - last[message] < 10: False; else update and True.

        Complexity: O(1) time, O(1) amortized space for a new message.
        """
        if message in self.last and timestamp - self.last[message] < 10:
            return False
        self.last[message] = timestamp
        return True


# Your Logger object will be instantiated and called as such:
# obj = Logger()
# param_1 = obj.shouldPrintMessage(timestamp,message)
# @lc code=end
