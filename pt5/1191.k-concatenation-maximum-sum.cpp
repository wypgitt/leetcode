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
    int kConcatenationMaxSum(vector<int>& arr, int k) {
        const long long MOD = 1'000'000'007;
        long long total = accumulate(arr.begin(), arr.end(), 0LL);
        long long bestSub = kadane(arr);

        if (k == 1) return bestSub % MOD;

        long long bestPrefix = 0, running = 0;
        for (int value : arr) {
            running += value;
            bestPrefix = max(bestPrefix, running);
        }

        long long bestSuffix = 0;
        running = 0;
        for (int i = arr.size() - 1; i >= 0; --i) {
            running += arr[i];
            bestSuffix = max(bestSuffix, running);
        }

        long long answer = max(bestSub, bestPrefix + bestSuffix + max(0LL, total) * (k - 2));
        return answer % MOD;
    }

private:
    long long kadane(const vector<int>& arr) {
        long long best = 0;
        long long current = 0;
        for (int value : arr) {
            current = max(0LL, current + value);
            best = max(best, current);
        }
        return best;
    }
};

/*
Interview Explanation

Core idea:
For k >= 2, a maximum subarray either lies inside one copy or crosses from a
suffix of one copy into a prefix of another. Middle full copies only help when
the total array sum is positive.

C++ data structures:
- Scalar long long values avoid overflow before modulo.
- Kadane computes nonnegative maximum subarray sum.

Algorithm:
1. Compute best subarray in one copy.
2. If k == 1, return it.
3. Compute best prefix and suffix sums.
4. Candidate crossing sum is suffix + prefix + max(0,total)*(k-2).
5. Return max candidate modulo 1e9+7.

Correctness:
A subarray in repeated copies can use at most one suffix, at most one prefix,
and any number of full middle arrays. Full middle arrays are beneficial only if
their sum is positive. These cases cover every possible subarray, so the max is
correct.

Complexity:
O(n) time and O(1) space.

Edge cases:
- All negative values return 0 because empty subarray is allowed by this
  problem.
- k = 1 ignores prefix/suffix crossing.
*/
