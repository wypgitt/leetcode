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
    int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
        /*
        Approach: if total gas is less than total cost, no start works. Otherwise
        scan once while tracking the current tank from a candidate start. When it
        goes negative, no station in that failed segment can be the answer, so
        the next station becomes the new candidate.

        Complexity: O(n) time, O(1) space.
        */
        int total = 0, tank = 0, start = 0;
        for (int i = 0; i < (int)gas.size(); ++i) {
            int diff = gas[i] - cost[i];
            total += diff;
            tank += diff;
            if (tank < 0) { start = i + 1; tank = 0; }
        }
        return total < 0 ? -1 : start;
    }
};
