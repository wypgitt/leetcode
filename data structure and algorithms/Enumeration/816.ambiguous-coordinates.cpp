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
    vector<string> forms(const string& part) {
        if (part.size() == 1) return {part};
        vector<string> ans;
        if (part[0] != '0') ans.push_back(part);
        for (int i = 1; i < (int)part.size(); ++i) {
            string left = part.substr(0, i), right = part.substr(i);
            if ((left == "0" || left[0] != '0') && right.back() != '0') ans.push_back(left + "." + right);
        }
        return ans;
    }

public:
    vector<string> ambiguousCoordinates(string s) {
        string digits = s.substr(1, s.size() - 2);
        vector<string> ans;
        for (int i = 1; i < (int)digits.size(); ++i) {
            auto lefts = forms(digits.substr(0, i));
            auto rights = forms(digits.substr(i));
            for (const string& l : lefts) for (const string& r : rights) ans.push_back("(" + l + ", " + r + ")");
        }
        return ans;
    }
};

/*
Interview explanation:
Split the inner digits into x and y parts, generate all valid decimal representations for each part, and combine them.

C++ data structures: vector<string> stores generated forms for each side before Cartesian product.

Edge cases: leading zeros are only allowed for the exact number 0; fractional parts cannot end in zero.

Complexity: output-size dominated; worst-case O(n^3) string construction time and O(output) space.
*/
