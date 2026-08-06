#
# @lc app=leetcode id=2622 lang=python3
#
# [2622] Cache With Time Limit
#
# https://leetcode.com/problems/cache-with-time-limit/description/
#
# algorithms
# Medium (76.27%)
# Likes:    545
# Dislikes: 46
# Total Accepted:    88.9K
# Total Submissions: 116.6K
# Testcase Example:  "[\"TimeLimitedCache\", \"set\", \"get\", \"count\", \"get\"]\n[[], [1, 42, 100], [1], [], [1]]\n[0, 0, 50, 50, 150]"
#
# Write a class that allows getting and setting key-value pairs, however a time
# until expiration is associated with each key.
#
# The class has three public methods:
#
# set(key, value, duration): accepts an integer key, an integer value, and a
# duration in milliseconds. Once the duration has elapsed, the key should be
# inaccessible. The method should return true if the same un-expired key already
# exists and false otherwise. Both the value and duration should be overwritten
# if the key already exists.
#
# get(key): if an un-expired key exists, it should return the associated value.
# Otherwise it should return -1.
#
# count(): returns the count of un-expired keys.
#
#
#
# Example 1:
#
# Input:
# actions = ["TimeLimitedCache", "set", "get", "count", "get"]
# values = [[], [1, 42, 100], [1], [], [1]]
# timeDelays = [0, 0, 50, 50, 150]
# Output: [null, false, 42, 1, -1]
# Explanation:
# At t=0, the cache is constructed.
# At t=0, a key-value pair (1: 42) is added with a time limit of 100ms. The
# value doesn't exist so false is returned.
# At t=50, key=1 is requested and the value of 42 is returned.
# At t=50, count() is called and there is one active key in the cache.
# At t=100, key=1 expires.
# At t=150, get(1) is called but -1 is returned because the cache is empty.
#
# Example 2:
#
# Input:
# actions = ["TimeLimitedCache", "set", "set", "get", "get", "get", "count"]
# values = [[], [1, 42, 50], [1, 50, 100], [1], [1], [1], []]
# timeDelays = [0, 0, 40, 50, 120, 200, 250]
# Output: [null, false, true, 50, 50, -1, 0]
# Explanation:
# At t=0, the cache is constructed.
# At t=0, a key-value pair (1: 42) is added with a time limit of 50ms. The value
# doesn't exist so false is returned.
# At t=40, a key-value pair (1: 50) is added with a time limit of 100ms. A
# non-expired value already existed so true is returned and the old value was
# overwritten.
# At t=50, get(1) is called which returned 50.
# At t=120, get(1) is called which returned 50.
# At t=140, key=1 expires.
# At t=200, get(1) is called but the cache is empty so -1 is returned.
# At t=250, count() returns 0 because the cache is empty.
#
#
#
# Constraints:
#
#
# 0 <= key, value <= 10^9
#
#
# 0 <= duration <= 1000
#
#
# 1 <= actions.length <= 100
#
#
# actions.length === values.length
#
#
# actions.length === timeDelays.length
#
#
# 0 <= timeDelays[i] <= 1450
#
#
# actions[i] is one of "TimeLimitedCache", "set", "get" and "count"
#
#
# First action is always "TimeLimitedCache" and must be executed immediately,
# with a 0-millisecond delay
#

# @lc code=start
import time
from typing import Dict, Tuple


class TimeLimitedCache:
    """
    Interview explanation:
    Key-value cache where each entry expires after a duration in milliseconds.
    """

    def __init__(self) -> None:
        """
        Interview explanation:
        Initialize an empty time-limited cache.

        Algorithm:
        - Store key -> (value, expire_at_ms) in a dict.

        Complexity: O(1) time and space.
        """
        self._store: Dict[int, Tuple[int, float]] = {}

    def _now_ms(self) -> float:
        """
        Interview explanation:
        Current wall-clock time in milliseconds.

        Algorithm:
        - Return time.time() * 1000.

        Complexity: O(1).
        """
        return time.time() * 1000.0

    def _is_alive(self, key: int) -> bool:
        """
        Interview explanation:
        Whether key exists and has not expired; prune if expired.

        Algorithm:
        - Compare stored expire timestamp to now; delete if past.

        Complexity: O(1).
        """
        if key not in self._store:
            return False
        _, expire_at = self._store[key]
        if self._now_ms() >= expire_at:
            del self._store[key]
            return False
        return True

    def set(self, key: int, value: int, duration: int) -> bool:
        """
        Interview explanation:
        Set key to value for duration ms. Return whether an unexpired key existed.

        Algorithm:
        - Check prior unexpired presence, then overwrite value and expire time.

        Complexity: O(1) time and space.
        """
        existed = self._is_alive(key)
        self._store[key] = (value, self._now_ms() + duration)
        return existed

    def get(self, key: int) -> int:
        """
        Interview explanation:
        Return value for an unexpired key, else -1.

        Algorithm:
        - Prune if expired; otherwise return stored value.

        Complexity: O(1).
        """
        if not self._is_alive(key):
            return -1
        return self._store[key][0]

    def count(self) -> int:
        """
        Interview explanation:
        Count currently unexpired keys.

        Algorithm:
        - Iterate keys and keep those still alive via _is_alive.

        Complexity: O(n) where n is stored keys.
        """
        keys = list(self._store.keys())
        return sum(1 for k in keys if self._is_alive(k))


class Solution:
    def TimeLimitedCache(self) -> TimeLimitedCache:
        """
        Interview explanation:
        Factory wrapper returning a TimeLimitedCache instance.

        Algorithm:
        - Construct and return TimeLimitedCache().

        Complexity: O(1).
        """
        return TimeLimitedCache()
# @lc code=end
