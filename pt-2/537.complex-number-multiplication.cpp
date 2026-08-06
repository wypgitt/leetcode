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
    pair<int, int> parse(const string& num) {
        int plus = num.find('+');
        int real = stoi(num.substr(0, plus));
        int imag = stoi(num.substr(plus + 1, num.size() - plus - 2));
        return {real, imag};
    }

public:
    string complexNumberMultiply(string num1, string num2) {
        auto [a, b] = parse(num1);
        auto [c, d] = parse(num2);
        return to_string(a * c - b * d) + "+" + to_string(a * d + b * c) + "i";
    }
};

/*
Interview explanation:
Parse a+bi into integer pairs and apply (a+bi)(c+di)=(ac-bd)+(ad+bc)i.

C++ data structures: pair<int,int> communicates real/imaginary parts clearly; stoi handles signs.

Edge cases: negative components parse correctly because the separator is the plus between real and imaginary parts.

Complexity: O(length of inputs) time and O(1) space.
*/
