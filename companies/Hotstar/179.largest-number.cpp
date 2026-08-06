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
    string largestNumber(vector<int>& nums) {
        /*
        Approach: convert numbers to strings and sort by concatenation order. For
        two strings a and b, a should come first exactly when a+b > b+a.

        C++ notes: sort accepts a custom lambda comparator for the concatenation
        rule.
        Complexity: O(n log n * k) time, O(n*k) space for strings.
        */
        vector<string> parts;
        for (int num : nums) parts.push_back(to_string(num));
        sort(parts.begin(), parts.end(), [](const string& a, const string& b) {
            return a + b > b + a;
        });
        if (!parts.empty() && parts[0] == "0") return "0";
        string ans;
        for (const string& part : parts) ans += part;
        return ans;
    }
};
