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
    int maximumSum(vector<int>& arr) {
        int keep = arr[0];
        int drop = INT_MIN / 2;
        int answer = arr[0];

        for (int i = 1; i < (int)arr.size(); ++i) {
            int value = arr[i];
            drop = max(drop + value, keep);
            keep = max(keep + value, value);
            answer = max(answer, max(keep, drop));
        }

        return answer;
    }
};

/*
Interview Explanation

Core idea:
Kadane's algorithm with two states: best subarray ending here with no deletion,
and best subarray ending here with one deletion already used.

C++ data structures:
- Two integers, keep and drop, store rolling DP states.

Algorithm:
For each value:
- drop is either previous drop plus value, or delete current value from the
  previous keep state.
- keep is normal Kadane: extend or restart.
- answer tracks the best of both states.

Correctness:
Every optimal subarray ending at i either has no deletion, represented by keep,
or one deletion, represented by drop. The transitions enumerate all ways to
extend or use the deletion at the current position, so the best over all i is
the answer.

Complexity:
O(n) time and O(1) space.

Edge cases:
- All negative arrays return the largest single element, because the subarray
  cannot be empty.
- One element returns itself.
*/
