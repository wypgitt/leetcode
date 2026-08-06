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

class LogSystem {
    vector<pair<string, int>> logs;
    unordered_map<string, int> cut{{"Year", 4}, {"Month", 7}, {"Day", 10}, {"Hour", 13}, {"Minute", 16}, {"Second", 19}};

public:
    LogSystem() {}

    void put(int id, string timestamp) {
        logs.push_back({timestamp, id});
    }

    vector<int> retrieve(string start, string end, string granularity) {
        int len = cut[granularity];
        string lo = start.substr(0, len), hi = end.substr(0, len);
        vector<int> ans;
        for (auto& [timestamp, id] : logs) {
            string cur = timestamp.substr(0, len);
            if (lo <= cur && cur <= hi) ans.push_back(id);
        }
        return ans;
    }
};

/*
Interview explanation:
Zero-padded timestamps are ordered from most significant to least significant component, so lexicographic prefix comparison is chronological comparison at a granularity.

C++ data structures: vector<pair<string,int>> stores logs in insertion order; unordered_map maps granularity names to prefix lengths.

Edge cases: comparisons are inclusive; smaller components are ignored by prefix truncation.

Complexity: put is O(1), retrieve is O(L) over stored logs and O(answer) output space.
*/
