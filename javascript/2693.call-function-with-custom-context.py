#
# @lc app=leetcode id=2693 lang=python3
#
# [2693] Call Function with Custom Context
#
# https://leetcode.com/problems/call-function-with-custom-context/description/
#
# algorithms
# Medium (77.32%)
# Likes:    146
# Dislikes: 14
# Total Accepted:    15.5K
# Total Submissions: 20K
# Testcase Example:  "function add(b) { return this.a + b; }\n[{\"a\":5},7]"
#
# Enhance all functions to have the callPolyfill method. The method accepts an
# object obj as its first parameter and any number of additional arguments.
# The obj becomes the this context for the function. The additional arguments
# are passed to the function (that the callPolyfill method belongs on).
#
# For example if you had the function:
#
# function tax(price, taxRate) {
#   const totalCost = price * (1 + taxRate);
#   console.log(`The cost of ${this.item} is ${totalCost}`);
# }
#
# Calling this function like tax(10, 0.1) will log "The cost of undefined is
# 11". This is because the this context was not defined.
#
# However, calling the function like tax.callPolyfill({item: "salad"}, 10,
# 0.1) will log "The cost of salad is 11". The this context was appropriately
# set, and the function logged an appropriate output.
#
# Please solve this without using the built-in Function.call method.
#
#
#
# Example 1:
#
# Input:
# fn = function add(b) {
#   return this.a + b;
# }
# args = [{"a": 5}, 7]
# Output: 12
# Explanation:
# fn.callPolyfill({"a": 5}, 7); // 12
# callPolyfill sets the "this" context to {"a": 5}. 7 is passed as an argument.
#
# Example 2:
#
# Input:
# fn = function tax(price, taxRate) {
#  return `The cost of the ${this.item} is ${price * taxRate}`;
# }
# args = [{"item": "burger"}, 10, 1.1]
# Output: "The cost of the burger is 11"
# Explanation: callPolyfill sets the "this" context to {"item": "burger"}. 10
# and 1.1 are passed as additional arguments.
#
#
#
# Constraints:
#
#
# typeof args[0] == 'object' and args[0] != null
#
#
# 1 <= args.length <= 100
#
#
# 2 <= JSON.stringify(args[0]).length <= 10^5
#

# @lc code=start

from typing import Any, Callable, List


class Solution:
    def callPolyfill(self, fn: Callable[..., Any], args: List[Any], context: Any = None) -> Any:
        """
        Interview explanation:
        JavaScript 30: Function.prototype.callPolyfill(context, ...args) invokes fn with given this.
        Python port: call fn with context bound via __self__ simulation — supply context as first
        arg if fn expects it, else use types.MethodType for bound call when possible.

        Algorithm:
        - Prefer binding: call fn(*args) after temporarily attaching; simplest portable form is
          invoking fn with explicit context via a wrapper that sets fn.__globals__ style is wrong.
          Use: if context is None: return fn(*args); else return types.MethodType(fn, context)(*args)
          when fn is a function; fallback fn(context, *args).

        Complexity: O(1) + fn cost.
        """
        import types

        if context is None:
            return fn(*args)
        try:
            return types.MethodType(fn, context)(*args)
        except TypeError:
            return fn(context, *args)


def callPolyfill(fn: Callable[..., Any], context: Any, *args: Any) -> Any:
    """
    Interview explanation:
    Top-level callPolyfill(fn, context, *args) matching JS semantics.

    Algorithm:
    - Delegate to Solution.callPolyfill.

    Complexity: O(1) + fn cost.
    """
    return Solution().callPolyfill(fn, list(args), context)
# @lc code=end
