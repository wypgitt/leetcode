#
# @lc app=leetcode id=2630 lang=python3
#
# [2630] Memoize II
#
# https://leetcode.com/problems/memoize-ii/description/
#
# algorithms
# Hard (39.47%)
# Likes:    134
# Dislikes: 46
# Total Accepted:    12.9K
# Total Submissions: 32.6K
# Testcase Example:  "() => [[2,2],[2,2],[1,2]]\nfunction (a, b) { return a + b; }"
#
# Given a function fn, return a memoized version of that function.
#
# A memoized function is a function that will never be called twice with the
# same inputs. Instead it will return a cached value.
#
# fn can be any function and there are no constraints on what type of values it
# accepts. Inputs are considered identical if they are === to each other.
#
#
#
# Example 1:
#
# Input:
# getInputs = () => [[2,2],[2,2],[1,2]]
# fn = function (a, b) { return a + b; }
# Output: [{"val":4,"calls":1},{"val":4,"calls":1},{"val":3,"calls":2}]
# Explanation:
# const inputs = getInputs();
# const memoized = memoize(fn);
# for (const arr of inputs) {
#   memoized(...arr);
# }
#
# For the inputs of (2, 2): 2 + 2 = 4, and it required a call to fn().
# For the inputs of (2, 2): 2 + 2 = 4, but those inputs were seen before so no
# call to fn() was required.
# For the inputs of (1, 2): 1 + 2 = 3, and it required another call to fn() for
# a total of 2.
#
# Example 2:
#
# Input:
# getInputs = () => [[{},{}],[{},{}],[{},{}]]
# fn = function (a, b) { return ({...a, ...b}); }
# Output: [{"val":{},"calls":1},{"val":{},"calls":2},{"val":{},"calls":3}]
# Explanation:
# Merging two empty objects will always result in an empty object. It may seem
# like there should only be 1 call to fn() because of cache-hits, however none
# of those objects are === to each other.
#
# Example 3:
#
# Input:
# getInputs = () => { const o = {}; return [[o,o],[o,o],[o,o]]; }
# fn = function (a, b) { return ({...a, ...b}); }
# Output: [{"val":{},"calls":1},{"val":{},"calls":1},{"val":{},"calls":1}]
# Explanation:
# Merging two empty objects will always result in an empty object. The 2nd and
# 3rd third function calls result in a cache-hit. This is because every object
# passed in is identical.
#
#
#
# Constraints:
#
#
# 1 <= inputs.length <= 10^5
#
#
# 0 <= inputs.flat().length <= 10^5
#
#
# inputs[i][j] != NaN
#

# @lc code=start
from typing import Any, Callable, Dict


def memoize(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Interview explanation:
    Memoize with object-identity semantics (JS ===): unhashable/mutable args
    are keyed by id via a nested trie so the same object identity hits cache.

    Algorithm:
    - Trie nodes keyed by id(arg) for each positional argument in order.
    - A sentinel marks a completed call's cached result at that path.
    - Empty-arg calls use a dedicated root result slot.

    Complexity: O(arity) per call for trie walk; O(unique call paths) space.
    """
    _RESULT = object()
    root: Dict[Any, Any] = {}
    empty_result: Dict[str, Any] = {"has": False, "value": None}

    def wrapped(*args: Any) -> Any:
        """
        Interview explanation:
        Identity-keyed memoized invocation.

        Algorithm:
        - Walk/create trie by id(arg); store/return result under _RESULT.

        Complexity: O(arity) besides fn.
        """
        if not args:
            if not empty_result["has"]:
                empty_result["value"] = fn()
                empty_result["has"] = True
            return empty_result["value"]
        node: Dict[Any, Any] = root
        for arg in args:
            key = id(arg)
            nxt = node.get(key)
            if nxt is None:
                nxt = {}
                node[key] = nxt
            node = nxt
        if _RESULT not in node:
            node[_RESULT] = fn(*args)
        return node[_RESULT]

    return wrapped


class Solution:
    def memoize(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Interview explanation:
        Thin Solution wrapper for Memoize II.

        Algorithm:
        - Delegate to memoize(fn).

        Complexity: Same as memoize.
        """
        return memoize(fn)
# @lc code=end
