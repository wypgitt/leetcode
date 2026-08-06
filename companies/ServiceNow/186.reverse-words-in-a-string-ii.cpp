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
    void reverseWords(vector<char>& s) {
        /*
        Approach: reverse the whole character array, then reverse each individual
        word. The first reversal puts words in reverse order but with letters
        reversed; the second pass restores letters inside each word.

        C++ notes: vector<char>& mutates the input buffer in place, matching the
        Python list[str] character array.
        Complexity: O(n) time, O(1) space.
        */
        auto rev = [&](int left, int right) {
            while (left < right) swap(s[left++], s[right--]);
        };
        rev(0, (int)s.size() - 1);
        int start = 0;
        for (int i = 0; i <= (int)s.size(); ++i) {
            if (i == (int)s.size() || s[i] == ' ') {
                rev(start, i - 1);
                start = i + 1;
            }
        }
    }
};
