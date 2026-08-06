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
    vector<vector<string>> groupStrings(vector<string>& strings) {
        /*
        Approach: normalize each string by recording character offsets from its
        first character modulo 26. Strings in the same shifting group share this
        offset pattern.

        C++ notes: the vector<int> pattern is serialized into a compact string
        key for unordered_map.
        Complexity: O(total characters) time and space.
        */
        unordered_map<string, vector<string>> groups;
        for (const string& s : strings) {
            string key;
            int base = s[0] - 'a';
            for (char ch : s) {
                int offset = (ch - 'a' - base + 26) % 26;
                key += to_string(offset) + '#';
            }
            groups[key].push_back(s);
        }
        vector<vector<string>> ans;
        for (auto& [key, group] : groups) ans.push_back(group);
        return ans;
    }
};
