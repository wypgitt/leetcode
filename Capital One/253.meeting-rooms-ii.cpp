#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    int minMeetingRooms(vector<vector<int>>& intervals) {
        /*
        Approach: sort meetings by start time. A min-heap stores end times of
        currently occupied rooms. Before placing a meeting, free every room whose
        end time is <= the meeting start. The maximum heap size is the answer.

        C++ notes: priority_queue<int, vector<int>, greater<int>> is a min-heap.
        Complexity: O(n log n) time, O(n) space.
        */
        if (intervals.empty()) return 0;
        sort(intervals.begin(), intervals.end(), [](const vector<int>& a, const vector<int>& b) {
            return a[0] < b[0];
        });
        priority_queue<int, vector<int>, greater<int>> heap;
        int best = 0;
        for (auto& interval : intervals) {
            int start = interval[0], end = interval[1];
            while (!heap.empty() && heap.top() <= start) heap.pop();
            heap.push(end);
            best = max(best, (int)heap.size());
        }
        return best;
    }
};
