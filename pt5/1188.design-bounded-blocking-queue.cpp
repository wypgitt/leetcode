#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class BoundedBlockingQueue {
private:
    int capacity;
    deque<int> q;
    mutable mutex mtx;
    condition_variable cv;

public:
    BoundedBlockingQueue(int capacity) : capacity(capacity) {}

    void enqueue(int element) {
        unique_lock<mutex> lock(mtx);
        cv.wait(lock, [&] { return (int)q.size() < capacity; });
        q.push_back(element);
        cv.notify_all();
    }

    int dequeue() {
        unique_lock<mutex> lock(mtx);
        cv.wait(lock, [&] { return !q.empty(); });
        int value = q.front();
        q.pop_front();
        cv.notify_all();
        return value;
    }

    int size() {
        lock_guard<mutex> lock(mtx);
        return q.size();
    }
};

/*
Interview Explanation

Core idea:
Producers wait while the queue is full; consumers wait while it is empty.
condition_variable provides blocking behavior without busy-waiting.

C++ data structures:
- deque<int> stores queue elements.
- mutex protects the deque and capacity checks.
- condition_variable wakes waiting producers/consumers when state changes.

Algorithm:
enqueue waits until size < capacity, pushes, then notifies.
dequeue waits until non-empty, pops front, then notifies.
size reads under the mutex.

Correctness:
All queue mutations happen while holding the mutex, so size and contents stay
consistent. The wait predicates enforce capacity and non-empty constraints even
with spurious wakeups.

Complexity:
Each operation is O(1) excluding blocking time. Space is O(capacity).

Edge cases:
- enqueue blocks on full queue.
- dequeue blocks on empty queue.
*/
