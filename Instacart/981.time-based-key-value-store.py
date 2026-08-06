#
# @lc app=leetcode id=981 lang=python3
#
# [981] Time Based Key-Value Store
#
# https://leetcode.com/problems/time-based-key-value-store/description/
#
# algorithms
# Medium (50.1%)
# Likes:    5342
# Dislikes: 740
# Total Accepted:    774K
# Total Submissions: 1.5M
# Testcase Example:  "[\"TimeMap\",\"set\",\"get\",\"get\",\"set\",\"get\",\"get\"]"
#
# Design a time-based key-value data structure that can store multiple values
# for the same key at different time stamps and retrieve the key's value at a
# certain timestamp.
#
# Implement the TimeMap class:
#
# TimeMap() Initializes the object of the data structure.
#
# void set(String key, String value, int timestamp) Stores the key key with the
# value value at the given time timestamp.
#
# String get(String key, int timestamp) Returns a value such that set was
# called previously, with timestamp_prev <= timestamp. If there are multiple
# such values, it returns the value associated with the largest timestamp_prev.
# If there are no values, it returns "".
#
# Example 1:
#
# Input
# ["TimeMap", "set", "get", "get", "set", "get", "get"]
# [[], ["foo", "bar", 1], ["foo", 1], ["foo", 3], ["foo", "bar2", 4], ["foo",
# 4], ["foo", 5]]
# Output
# [null, null, "bar", "bar", null, "bar2", "bar2"]
#
# Explanation
# TimeMap timeMap = new TimeMap();
# timeMap.set("foo", "bar", 1); // store the key "foo" and value "bar" along
# with timestamp = 1.
# timeMap.get("foo", 1); // return "bar"
# timeMap.get("foo", 3); // return "bar", since there is no value corresponding
# to foo at timestamp 3 and timestamp 2, then the only value is at timestamp 1
# is "bar".
# timeMap.set("foo", "bar2", 4); // store the key "foo" and value "bar2" along
# with timestamp = 4.
# timeMap.get("foo", 4); // return "bar2"
# timeMap.get("foo", 5); // return "bar2"
#
# Constraints:
#
# 1 <= key.length, value.length <= 100
#
# key and value consist of lowercase English letters and digits.
#
# 1 <= timestamp <= 10^7
#
# All the timestamps timestamp of set are strictly increasing.
#
# At most 2 * 10^5 calls will be made to set and get.
#

# @lc code=start
import bisect
from collections import defaultdict
from typing import Dict, List, Tuple


class TimeMap:
    """
    Interview explanation:
    Per key, store a chronologically sorted list of (timestamp, value). set
    appends (timestamps strictly increasing). get binary-searches the rightmost
    timestamp <= query time.
    """

    def __init__(self):
        """
        Interview explanation:
        Map each key to a list of (timestamp, value) pairs, kept sorted by time.

        Algorithm:
        - self.store: Dict[str, List[Tuple[int, str]]]

        Complexity: O(1) time, O(1) space initially.
        """
        self.store: Dict[str, List[Tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        """
        Interview explanation:
        Append (timestamp, value) for key. Guaranteed timestamps increase, so
        the list stays sorted without an extra insert.

        Algorithm:
        - store[key].append((timestamp, value))

        Complexity: O(1) amortized time, O(1) extra space per call.
        """
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        """
        Interview explanation:
        Binary search the largest timestamp <= query among set history for key.
        Use bisect_right on (timestamp, ...) then take previous entry.

        Algorithm:
        - arr = store[key]; if empty return "".
        - i = bisect_right(arr, (timestamp, chr(127))) - 1 (or bisect on times).
        - If i >= 0 return arr[i][1] else "".

        Complexity: O(log n) time per get, O(1) extra space.
        """
        arr = self.store.get(key)
        if not arr:
            return ""
        i = bisect.bisect_right(arr, (timestamp, chr(127))) - 1
        if i >= 0:
            return arr[i][1]
        return ""


# Your TimeMap object will be instantiated and called as such:
# obj = TimeMap()
# obj.set(key,value,timestamp)
# param_2 = obj.get(key,timestamp)
# @lc code=end
