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
    string intToRoman(int num) {
        /*
        Approach:
        Include subtractive Roman forms in a descending value table. Greedily
        append the largest symbol that fits the remaining number, then reduce
        the number by that value.

        C++ notes:
        vector<pair<int, string>> represents the fixed lookup table.

        Complexity: O(1) time and O(1) space because num is bounded by 3999.
        */
        vector<pair<int, string>> values = {
            {1000, "M"}, {900, "CM"}, {500, "D"}, {400, "CD"},
            {100, "C"}, {90, "XC"}, {50, "L"}, {40, "XL"},
            {10, "X"}, {9, "IX"}, {5, "V"}, {4, "IV"}, {1, "I"}
        };
        string ans;
        for (auto& [value, symbol] : values) {
            while (num >= value) {
                ans += symbol;
                num -= value;
            }
        }
        return ans;
    }
};
