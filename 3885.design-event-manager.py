#
# @lc app=leetcode id=3885 lang=python3
#
# [3885] Design Event Manager
#
# https://leetcode.com/problems/design-event-manager/description/
#
# algorithms
# Medium (50.83%)
# Likes:    73
# Dislikes: 5
# Total Accepted:    28.7K
# Total Submissions: 56.5K
# Testcase Example:  '["EventManager","pollHighest","updatePriority","pollHighest","pollHighest"]\n' +
# '[[[[5,7],[2,7],[9,4]]],[],[9,7],[],[]]'
#
# You are given an initial list of events, where each event has a unique
# eventId and a priority.
# 
# Implement the EventManager class:
# 
# 
# EventManager(int[][] events) Initializes the manager with the given events,
# where events[i] = [eventIdi, priority​​​​​​​i].
# void updatePriority(int eventId, int newPriority) Updates the priority of the
# active event with id eventId to newPriority.
# int pollHighest() Removes and returns the eventId of the active event with
# the highest priority. If multiple active events have the same priority,
# return the smallest eventId among them. If there are no active events, return
# -1.
# 
# 
# An event is called active if it has not been removed by pollHighest().
# 
# 
# Example 1:
# 
# 
# Input:
# ["EventManager", "pollHighest", "updatePriority", "pollHighest",
# "pollHighest"]
# [[[[5, 7], [2, 7], [9, 4]]], [], [9, 7], [], []]
# 
# Output:
# [null, 2, null, 5, 9] 
# 
# Explanation
# EventManager eventManager = new EventManager([[5,7], [2,7], [9,4]]); //
# Initializes the manager with three events
# eventManager.pollHighest(); // both events 5 and 2 have priority 7, so return
# the smaller id 2
# eventManager.updatePriority(9, 7); // event 9 now has priority 7
# eventManager.pollHighest(); // remaining highest priority events are 5 and 9,
# return 5
# eventManager.pollHighest(); // return 9
# 
# Example 2:
# 
# 
# Input:
# ["EventManager", "pollHighest", "pollHighest", "pollHighest"]
# [[[[4, 1], [7, 2]]], [], [], []]
# 
# Output:
# [null, 7, 4, -1] 
# 
# Explanation
# EventManager eventManager = new EventManager([[4,1], [7,2]]); // Initializes
# the manager with two events
# eventManager.pollHighest(); // return 7
# eventManager.pollHighest(); // return 4
# eventManager.pollHighest(); // no events remain, return -1
# 
# 
# Constraints:
# 
# 
# 1 <= events.length <= 10^5
# events[i] = [eventId, priority]
# 1 <= eventId <= 10^9
# 1 <= priority <= 10^9
# All the values of eventId in events are unique.
# 1 <= newPriority <= 10^9
# For every call to updatePriority, eventId refers to an active event.
# At most 10^5 calls in total will be made to updatePriority and pollHighest.
# 
# 
#

# @lc code=start
import heapq


class EventManager:
    """
    Interview explanation
    =====================

    Restate the problem
    -------------------
    We need to design a data structure that manages active events.

    Each event has:

        eventId
        priority

    Supported operations:

    * `updatePriority(eventId, newPriority)`
      Change the priority of an active event.

    * `pollHighest()`
      Remove and return the active event with:

          1. highest priority
          2. if tied, smallest eventId

      If no active event exists, return -1.

    Constraints are large:

        up to 100,000 initial events
        up to 100,000 method calls
        eventId and priority up to 10^9

    So we need near-logarithmic operations.

    Key challenge: priority updates
    -------------------------------
    A heap is the natural structure for repeatedly taking the highest-priority
    item.  However, Python's `heapq` does not support directly changing the
    priority of an existing heap entry.

    Removing an old entry from the middle of a heap would cost O(n), which is too
    slow.

    The standard solution is lazy deletion.

    Lazy deletion idea
    ------------------
    We store two things:

    1. `self.active_priority`

       A dictionary:

           eventId -> current priority

       If an eventId is not in this dictionary, that event has already been
       removed by `pollHighest`.

    2. `self.heap`

       A heap containing entries:

           (-priority, eventId)

       Python has a min-heap, so using negative priority makes larger priorities
       come out first.  If priorities tie, Python compares the second tuple
       element, so the smaller `eventId` comes out first automatically.

    When an event's priority changes, we do NOT remove the old heap entry.  We
    update the dictionary and push a new heap entry.  The old entry becomes
    stale.  Later, when it reaches the top of the heap, we detect that it no
    longer matches the dictionary and discard it.

    Why the tuple order works
    -------------------------
    We push:

        (-priority, eventId)

    Python pops the smallest tuple lexicographically.

    * Highest priority means most negative `-priority`, so it comes first.
    * If priorities are equal, `-priority` is equal, so smaller eventId comes
      first.

    Example:

        priority 7, id 2 -> (-7, 2)
        priority 7, id 5 -> (-7, 5)

    `(-7, 2)` is smaller, so id 2 is polled first.

    Operations
    ----------
    Initialization:

    * Fill the dictionary with all active events.
    * Push every `(-priority, eventId)` into the heap.
    * Heapify for O(n) construction.

    updatePriority(eventId, newPriority):

    * Update `active_priority[eventId] = newPriority`.
    * Push `(-newPriority, eventId)` into the heap.
    * The old heap entry, if any, is left in the heap as stale.

    pollHighest():

    * While the heap is not empty:
          - peek/pop the heap top
          - convert `-negative_priority` back to the real priority
          - check whether the event is still active and whether this heap entry
            equals its current priority
          - if valid, delete the event from the dictionary and return eventId
          - otherwise discard the stale entry and continue
    * If no valid active event remains, return -1.

    Correctness proof
    -----------------
    Lemma 1: `active_priority` always stores exactly the active events and their
    current priorities.
    Initially, all events are active and inserted into the dictionary.  An
    update changes only the current priority of an active event, so replacing the
    dictionary value preserves correctness.  A successful `pollHighest` removes
    exactly one active event from the dictionary.  No other operation removes an
    event.  Therefore the dictionary always represents exactly the active set.

    Lemma 2: For every active event, the heap contains at least one entry
    matching its current priority.
    Initially, every event is pushed with its initial priority.  Whenever an
    event's priority changes, a new matching entry is pushed.  Matching entries
    are only popped when the event is polled and removed, or when they have
    become stale due to a later update.  After every update, the newest pushed
    entry matches the dictionary value.

    Lemma 3: `pollHighest` never returns a stale or inactive event.
    Before returning, `pollHighest` checks that the popped eventId is still in
    `active_priority` and that the popped priority equals the current dictionary
    priority.  If either condition fails, the entry is discarded.  Therefore a
    returned event is active and has the priority represented by the heap entry.

    Lemma 4: When `pollHighest` returns an event, it is the active event with the
    highest priority, breaking ties by smallest eventId.
    By Lemma 2, every active event has a valid matching heap entry.  The heap
    orders entries by highest priority and then smallest eventId because entries
    are stored as `(-priority, eventId)`.  Stale entries may appear before valid
    ones, but by Lemma 3 they are discarded.  The first valid entry popped is
    therefore the best active event under the required ordering.

    Theorem: All operations behave as required.
    `updatePriority` correctly changes the current priority by Lemma 1.
    `pollHighest` returns -1 exactly when no active event remains; otherwise, by
    Lemma 4, it removes and returns the required event.  Thus the data structure
    satisfies the specification.

    Complexity analysis
    -------------------
    Let:

        n = number of initial events
        q = number of updatePriority/pollHighest calls

    Initialization:

        O(n) time to heapify
        O(n) space

    updatePriority:

        O(log(n + q)) time for one heap push
        O(1) dictionary update

    pollHighest:

        Each heap pop costs O(log(n + q)).  A single call may discard several
        stale entries, but every stale entry was created by a previous update and
        can be discarded only once.

        Therefore, amortized over all operations:

            O(log(n + q)) per call

    Space:

        O(n + q)

    because lazy deletion can leave old heap entries until they are popped.

    Edge cases
    ----------
    * Polling from an empty manager returns -1.
    * Many events with the same priority return in increasing eventId order.
    * Updating an event to the same priority is fine; it pushes a duplicate valid
      entry, and after the event is removed, any duplicate entries become
      inactive stale entries.
    * Repeated updates to the same event are fine; only the dictionary value is
      authoritative.
    * Large eventId/priority values are fine because we only compare integers and
      store them in dictionaries/heaps.

    Test strategy
    -------------
    Useful tests:

    * Provided examples.
    * Tie-breaking by eventId:
          events [[5, 7], [2, 7]] should poll 2 first.
    * Priority update creates a new highest event.
    * Repeated updates on the same event.
    * Poll until empty, then poll once more to get -1.
    * Randomized testing against a simple reference dictionary that scans all
      active events for the best candidate.

    Possible improvement?
    ---------------------
    A balanced binary search tree keyed by `(-priority, eventId)` could support
    exact deletion of old entries.  Python does not provide one in the standard
    library, and implementing one would add unnecessary complexity.  The lazy
    heap solution is the standard practical choice: simple, fast, and amortized
    logarithmic.
    """

    def __init__(self, events: list[list[int]]):
        self.active_priority: dict[int, int] = {}
        self.heap: list[tuple[int, int]] = []

        for event_id, priority in events:
            self.active_priority[event_id] = priority
            self.heap.append((-priority, event_id))

        heapq.heapify(self.heap)

    def updatePriority(self, eventId: int, newPriority: int) -> None:
        self.active_priority[eventId] = newPriority
        heapq.heappush(self.heap, (-newPriority, eventId))

    def pollHighest(self) -> int:
        while self.heap:
            negative_priority, event_id = heapq.heappop(self.heap)
            priority = -negative_priority

            if self.active_priority.get(event_id) == priority:
                del self.active_priority[event_id]
                return event_id

        return -1


# Your EventManager object will be instantiated and called as such:
# obj = EventManager(events)
# obj.updatePriority(eventId,newPriority)
# param_2 = obj.pollHighest()
# @lc code=end
