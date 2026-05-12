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

class FooBar {
private:
    int n;
    mutex mtx;
    condition_variable cv;
    bool fooTurn = true;

public:
    FooBar(int n) : n(n) {}

    void foo(function<void()> printFoo) {
        for (int i = 0; i < n; ++i) {
            unique_lock<mutex> lock(mtx);
            cv.wait(lock, [&] { return fooTurn; });
            printFoo();
            fooTurn = false;
            cv.notify_all();
        }
    }

    void bar(function<void()> printBar) {
        for (int i = 0; i < n; ++i) {
            unique_lock<mutex> lock(mtx);
            cv.wait(lock, [&] { return !fooTurn; });
            printBar();
            fooTurn = true;
            cv.notify_all();
        }
    }
};

/*
Interview Explanation

Core idea:
Two threads must alternate. A boolean turn flag plus condition_variable is a
direct C++ synchronization model.

C++ data structures:
- mutex protects shared state.
- condition_variable blocks a thread until its turn.
- bool fooTurn indicates which method may print.

Algorithm:
foo waits for fooTurn, prints, flips the turn, and notifies.
bar waits for !fooTurn, prints, flips the turn back, and notifies.

Correctness:
Only the thread whose predicate is true can leave cv.wait. After printing, it
sets the predicate for the other thread. Therefore outputs alternate exactly
foo, bar, foo, bar for n iterations.

Complexity:
O(n) print operations. Synchronization state uses O(1) space.

Edge cases:
- Spurious wakeups are safe because cv.wait uses a predicate.
- n = 1 prints exactly "foobar".
*/
