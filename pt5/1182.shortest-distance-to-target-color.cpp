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
    vector<int> shortestDistanceColor(vector<int>& colors, vector<vector<int>>& queries) {
        vector<vector<int>> positions(4);
        for (int i = 0; i < (int)colors.size(); ++i) {
            positions[colors[i]].push_back(i);
        }

        vector<int> answer;
        answer.reserve(queries.size());
        for (const auto& query : queries) {
            int index = query[0], color = query[1];
            auto& list = positions[color];
            if (list.empty()) {
                answer.push_back(-1);
                continue;
            }

            int best = INT_MAX;
            auto it = lower_bound(list.begin(), list.end(), index);
            if (it != list.end()) best = min(best, abs(*it - index));
            if (it != list.begin()) best = min(best, abs(*prev(it) - index));
            answer.push_back(best);
        }

        return answer;
    }
};

/*
Interview Explanation

Core idea:
For each color, store all indices where it appears. The closest occurrence to
a query index must be the lower_bound position or the one before it.

C++ data structures:
- vector<vector<int>> positions stores sorted indices for colors 1, 2, and 3.
- lower_bound performs binary search.

Algorithm:
1. Build positions lists by scanning colors.
2. For each query, binary search the target color's list.
3. Compare the candidate at lower_bound and its predecessor.

Correctness:
The positions list is sorted. Any occurrence farther left than the predecessor
or farther right than lower_bound is no closer than those boundary candidates.
Thus checking at most two positions gives the shortest distance.

Complexity:
Preprocessing is O(n). Each query is O(log n). Space is O(n).

Edge cases:
- Missing color returns -1.
- Exact color at query index returns 0.
*/
