#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    vector<vector<string>> groupAnagrams(vector<string>& strs) {
        /*
        Approach:
        Anagrams have the same sorted character sequence. Sort each string to
        form a key and group original strings by that key.

        C++ notes:
        unordered_map<string, vector<string>> is the hash-table equivalent of a
        Python dict mapping each key to its group.

        Complexity: O(N*K log K) time and O(N*K) space.
        */
        unordered_map<string, vector<string>> groups;
        for (const string& s : strs) {
            string key = s;
            sort(key.begin(), key.end());
            groups[key].push_back(s);
        }
        vector<vector<string>> ans;
        for (auto& entry : groups) ans.push_back(move(entry.second));
        return ans;
    }
};
