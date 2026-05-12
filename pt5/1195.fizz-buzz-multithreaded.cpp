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

class FizzBuzz {
private:
    int n;
    int current = 1;
    mutex mtx;
    condition_variable cv;

    void runWhen(function<bool(int)> predicate, function<void(int)> action) {
        while (true) {
            unique_lock<mutex> lock(mtx);
            cv.wait(lock, [&] { return current > n || predicate(current); });
            if (current > n) {
                cv.notify_all();
                return;
            }
            action(current);
            ++current;
            cv.notify_all();
        }
    }

public:
    FizzBuzz(int n) : n(n) {}

    void fizz(function<void()> printFizz) {
        runWhen([](int x) { return x % 3 == 0 && x % 5 != 0; }, [&](int) { printFizz(); });
    }

    void buzz(function<void()> printBuzz) {
        runWhen([](int x) { return x % 5 == 0 && x % 3 != 0; }, [&](int) { printBuzz(); });
    }

    void fizzbuzz(function<void()> printFizzBuzz) {
        runWhen([](int x) { return x % 15 == 0; }, [&](int) { printFizzBuzz(); });
    }

    void number(function<void(int)> printNumber) {
        runWhen([](int x) { return x % 3 != 0 && x % 5 != 0; }, printNumber);
    }
};

/*
Interview Explanation

Core idea:
Only one thread should print for each current number. A shared current counter
and condition_variable let each method wait until its predicate is true.

C++ data structures:
- mutex protects current.
- condition_variable blocks waiting print methods.
- Predicate/action helper removes duplicated synchronization code.

Algorithm:
Each method calls runWhen with its divisibility predicate. When current matches
that predicate, it prints, increments current, and notifies all threads. When
current exceeds n, all methods exit.

Correctness:
For every value, exactly one predicate is true among fizz, buzz, fizzbuzz, and
number. The mutex ensures only one thread updates current, and notify_all wakes
the next eligible thread. Therefore output follows the required order.

Complexity:
O(n) print steps and O(1) shared state.

Edge cases:
- Spurious wakeups are safe because wait uses a predicate.
- Threads exit cleanly after n.
*/
