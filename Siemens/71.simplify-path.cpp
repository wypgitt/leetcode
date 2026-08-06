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
    string simplifyPath(string path) {
        /*
        Approach:
        Split by '/'. Ignore empty parts and '.', pop one directory for '..',
        and push ordinary names. Join the stack with single slashes.

        C++ notes:
        vector<string> acts as a stack with push_back/pop_back.

        Complexity: O(n) time and O(n) space.
        */
        vector<string> parts;
        string token;
        stringstream ss(path);
        while (getline(ss, token, '/')) {
            if (token.empty() || token == ".") continue;
            if (token == "..") {
                if (!parts.empty()) parts.pop_back();
            } else {
                parts.push_back(token);
            }
        }
        if (parts.empty()) return "/";
        string ans;
        for (const string& part : parts) ans += "/" + part;
        return ans;
    }
};
