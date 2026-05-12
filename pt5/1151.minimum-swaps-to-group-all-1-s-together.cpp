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
    int minSwaps(vector<int>& data) {
        int ones = accumulate(data.begin(), data.end(), 0);
        if (ones <= 1) return 0;

        int windowOnes = 0;
        int best = 0;
        for (int i = 0; i < (int)data.size(); ++i) {
            windowOnes += data[i];
            if (i >= ones) windowOnes -= data[i - ones];
            best = max(best, windowOnes);
        }

        return ones - best;
    }
};

/*
Interview Explanation

Core idea:
All 1s must occupy a window whose length equals the total number of 1s. The
minimum swaps equals the number of zeros inside the best such window.

C++ data structures:
- Sliding-window counters are enough; no extra array is needed.

Algorithm:
1. Count total ones.
2. Slide a window of that length.
3. Track the maximum number of ones already inside any window.
4. Answer is total ones minus that maximum.

Correctness:
Any final grouped block has length equal to the number of 1s. If a candidate
block already contains k ones, the remaining ones-k positions are zeros that
must be swapped out. Maximizing k minimizes swaps.

Complexity:
O(n) time and O(1) space.

Edge cases:
- Zero or one 1 needs no swaps.
- All 1s returns 0.
*/
