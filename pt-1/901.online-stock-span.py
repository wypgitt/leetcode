#
# @lc app=leetcode id=901 lang=python3
#
# [901] Online Stock Span
#

# =============================================================================
# INTERVIEW: ELEVATOR PITCH (~30 seconds)
# =============================================================================
#
# "Today's span is how far back we can walk day-by-day while every seen price is
# ≤ today's price — we stop the first time we hit a **strictly higher** earlier price.
# A monotone **decreasing** stack of past days lets us skip runs of smaller quotes in
# bulk: pop everything ≤ today's price and **accumulate their spans** — those days lie
# inside our window. Amortized O(1) per quote; each day enters and leaves the stack once."
#
# =============================================================================
# PROBLEM (PRECISE)
# =============================================================================
#
# Streaming queries `next(price)` for day 1, 2, 3, … Return **span**: the maximum
# number of **consecutive** calendar days ending today such that every stock price in
# that window (including today) is **≤ today's price** — equivalently, walk backward
# day by day until you would encounter a day whose price is **greater than** today's
# price (that day is **not** counted); today **is** counted.
#
# =============================================================================
# WHY A MONOTONE STACK (NOT NAIVE DAY-BY-DAY SCAN)
# =============================================================================
#
# Naive: on each `next`, scan backward through **all** previous days until a higher
# price — **O(k)** per day, **O(n²)** total over **n** days.
#
# Key observation: days with price **≤ current** that lie **consecutively** before a
# barrier behave as one **aggregated width**: once we know their combined span, we only
# need that **integer**, not each intermediate price, for future queries.
#
# Maintain a stack of pairs **`(price, span_agg)`** with **strictly decreasing** prices
# from bottom to top (only **useful** “candles” that can block future spans). When a
# new `price` arrives, **pop** while `stack.top.price ≤ price`, adding each popped
# `span_agg` to a running total — those days are folded into today’s contiguous window.
# After pops, the top (if any) is the **previous greater** price (next barrier). Push
# `(price, total_span)` where `total_span` is `1 + sum of popped spans`.
#
# =============================================================================
# DATA STRUCTURE — STACK OF (PRICE, AGGREGATED_SPAN)
# =============================================================================
#
# • **Python list as stack** — `append` / `pop` at end are **O(1)**.
# • Each entry represents a **compressed segment** of history: the price at the **end**
#   of that segment and how many consecutive days that segment represents toward span
#   calculations.
#
# No heaps, segment trees, or frequency tables needed.
#
# =============================================================================
# AMORTIZED TIME ANALYSIS
# =============================================================================
#
# Each day’s quote is **pushed once** and **popped at most once** over the lifetime of
# the stream. Summed over **n** calls to `next`, total stack work is **O(n)** ⇒
# **amortized O(1)** time per `next`.
#
# **Space:** **O(n)** in the worst case (strictly decreasing prices — nothing popped).
#
# =============================================================================
# EDGE CASES
# =============================================================================
#
# • **First day** — stack empty; span is **1**.
# • **Strictly increasing** sequence — each span is **1** (yesterday always higher in
#   the stack… actually increasing means today > yesterday, so we pop yesterday if
#   yesterday ≤ today — equal case merges). For strictly increasing, each new price
#   pops the previous and accumulates span → actual spans grow (example 100,80,60,70).
# • **Flat market** — repeated same price: `≤` comparison merges consecutive equal
#   quotes into one span block (popping equals extends span correctly).
#
# =============================================================================
# TESTING (MANUAL / UNIT)
# =============================================================================
#
# Walk through LeetCode-style sequence; compare to brute simulate scanning backward
# day-by-day for small **n**.
#
# =============================================================================
# IMPROVEMENTS / VARIANTS
# =============================================================================
#
# • Store **indices** instead of spans if you need dates explicitly — same asymptotics.
# • **Array-based stack** in lower-level languages avoids dynamic list overhead.
#
# =============================================================================

# @lc code=start
from typing import List, Tuple


class StockSpanner:
    """
    Monotone decreasing stack: each frame is (price, span contribution ending at that
    day's compressed segment). Popping all frames with price <= current folds their
    widths into today's span.
    """

    def __init__(self):
        # Stack of (price, aggregated_span_for_that_block); prices strictly decrease bottom-up.
        self.stack: List[Tuple[int, int]] = []

    def next(self, price: int) -> int:
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack[-1][1]
            self.stack.pop()
        self.stack.append((price, span))
        return span


# Your StockSpanner object will be instantiated and called as such:
# obj = StockSpanner()
# param_1 = obj.next(price)
# @lc code=end
