#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    double champagneTower(int poured, int query_row, int query_glass) {
        vector<double> row(1, poured);
        for (int r = 0; r < query_row; ++r) {
            vector<double> next(row.size() + 1, 0.0);
            for (int i = 0; i < (int)row.size(); ++i) {
                double overflow = max(0.0, row[i] - 1.0) / 2.0;
                next[i] += overflow;
                next[i + 1] += overflow;
            }
            row = std::move(next);
        }
        return min(1.0, row[query_glass]);
    }
};

/*
Interview explanation:
Simulate row by row. Each glass keeps one cup and splits overflow equally to the two glasses below.

C++ data structures: vector<double> stores only the current row; move avoids unnecessary deep copy where possible.

Edge cases: answer is capped at 1 because a glass can receive more than one cup in the simulation.

Complexity: O(query_row^2) time and O(query_row) space.
*/
