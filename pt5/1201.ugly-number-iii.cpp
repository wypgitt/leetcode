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

class Solution {
public:
    int nthUglyNumber(int n, int a, int b, int c) {
        long long ab = lcmLL(a, b);
        long long ac = lcmLL(a, c);
        long long bc = lcmLL(b, c);
        long long abc = lcmLL(ab, c);

        long long left = 1, right = 2'000'000'000LL;
        while (left < right) {
            long long mid = left + (right - left) / 2;
            long long count = mid / a + mid / b + mid / c - mid / ab - mid / ac - mid / bc + mid / abc;
            if (count >= n) right = mid;
            else left = mid + 1;
        }
        return left;
    }

private:
    long long lcmLL(long long x, long long y) {
        return x / gcd(x, y) * y;
    }
};

/*
Interview Explanation

Core idea:
Binary search the answer. For any number x, count how many integers <= x are
divisible by a, b, or c using inclusion-exclusion.

C++ data structures:
- long long is used for LCMs and products to avoid overflow.

Algorithm:
1. Precompute pairwise and triple LCMs.
2. Binary search the smallest x whose ugly count is at least n.
3. Count(x) = x/a + x/b + x/c - x/lcm(a,b) - ... + x/lcm(a,b,c).

Correctness:
The count function is monotonic: larger x never decreases the number of ugly
numbers. Inclusion-exclusion counts each number divisible by at least one of
a,b,c exactly once. Binary search therefore finds the smallest x with at least
n ugly numbers, which is the nth ugly number.

Complexity:
O(log 2e9) time and O(1) space.

Edge cases:
- Divisors can share factors; LCM inclusion-exclusion handles overlap.
- If one divisor is 1, every number is ugly and binary search still works.
*/
