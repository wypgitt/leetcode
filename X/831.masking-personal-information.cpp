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
    string maskPII(string s) {
        if (s.find('@') != string::npos) {
            for (char& c : s) c = tolower(c);
            int at = s.find('@');
            return string(1, s[0]) + "*****" + s.substr(at - 1, 1) + s.substr(at);
        }
        string digits;
        for (char c : s) if (isdigit(c)) digits += c;
        string local = "***-***-" + digits.substr(digits.size() - 4);
        int country = digits.size() - 10;
        if (country == 0) return local;
        return "+" + string(country, '*') + "-" + local;
    }
};

/*
Interview explanation:
Email masking lowercases and preserves only first/last name characters. Phone masking strips punctuation, keeps the last four digits, and masks country code length.

C++ data structures: string accumulates normalized digits and builds the formatted result.

Edge cases: phone country code length can be 0..3; email local names are at least two characters by constraints.

Complexity: O(n) time and O(n) space.
*/
