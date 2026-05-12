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
    vector<int> corpFlightBookings(vector<vector<int>>& bookings, int n) {
        vector<int> diff(n + 1, 0);
        for (const auto& booking : bookings) {
            int first = booking[0] - 1;
            int last = booking[1] - 1;
            int seats = booking[2];
            diff[first] += seats;
            if (last + 1 < n) diff[last + 1] -= seats;
        }

        vector<int> answer(n);
        int running = 0;
        for (int i = 0; i < n; ++i) {
            running += diff[i];
            answer[i] = running;
        }
        return answer;
    }
};

/*
Interview Explanation

Core idea:
Each booking adds the same number of seats to a continuous flight range. A
difference array represents range additions in O(1).

C++ data structures:
- vector<int> diff stores range-start increments and range-end decrements.
- A running prefix sum materializes the final seats per flight.

Algorithm:
1. For booking [first, last, seats], add seats at first-1.
2. Subtract seats right after last, if that index exists.
3. Prefix-sum diff to produce the answer.

Correctness:
In a difference array, adding x at l and subtracting x at r+1 causes every
prefix-summed position from l through r to include x and every later position
to stop including it. Applying this for every booking accumulates exactly all
seat additions for each flight.

Complexity:
O(n + b) time, where b is bookings.size(). O(n) space.

Edge cases:
- Booking ending at flight n has no decrement.
- Overlapping bookings add naturally through the prefix sum.
- 1-indexed flight numbers are converted to 0-indexed vector positions.
*/
