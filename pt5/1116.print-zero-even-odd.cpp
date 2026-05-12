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

class ZeroEvenOdd {
private:
    int n;
    int current = 1;
    int turn = 0; // 0 = zero, 1 = odd, 2 = even
    mutex mtx;
    condition_variable cv;

public:
    ZeroEvenOdd(int n) : n(n) {}

    void zero(function<void(int)> printNumber) {
        for (int i = 1; i <= n; ++i) {
            unique_lock<mutex> lock(mtx);
            cv.wait(lock, [&] { return turn == 0; });
            printNumber(0);
            turn = (i % 2 == 1) ? 1 : 2;
            cv.notify_all();
        }
    }

    void even(function<void(int)> printNumber) {
        for (int i = 2; i <= n; i += 2) {
            unique_lock<mutex> lock(mtx);
            cv.wait(lock, [&] { return turn == 2; });
            printNumber(i);
            turn = 0;
            cv.notify_all();
        }
    }

    void odd(function<void(int)> printNumber) {
        for (int i = 1; i <= n; i += 2) {
            unique_lock<mutex> lock(mtx);
            cv.wait(lock, [&] { return turn == 1; });
            printNumber(i);
            turn = 0;
            cv.notify_all();
        }
    }
};

/*
Interview Explanation

Core idea:
The sequence is 0,1,0,2,0,3,... The zero thread always runs before each number
and then hands control to odd or even based on the next value.

C++ data structures:
- mutex and condition_variable coordinate the three threads.
- turn encodes which thread may print next.

Algorithm:
1. zero prints 0 for each value i and sets turn to odd/even.
2. odd prints odd numbers when turn == 1.
3. even prints even numbers when turn == 2.
4. Number threads return turn to zero.

Correctness:
The turn variable permits exactly one category of thread at a time. zero runs
before every value and selects the correct number thread. That thread prints
the current number and returns control to zero, producing the required order.

Complexity:
O(n) prints and O(1) synchronization state.

Edge cases:
- n = 1 uses only zero and odd.
- Spurious wakeups are handled by predicates.
*/
