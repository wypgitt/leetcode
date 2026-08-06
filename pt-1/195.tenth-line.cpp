// Translated from 195.tenth-line.py.
// Original Python source and explanation are preserved below as comments.
// #
// # =============================================================================
// # WHY YOU SEE: Not supported language "python3" / Command failed for LeetCode 195
// # =============================================================================
// #
// # Problem 195 is tagged **shell** only. The LeetCode CLI only accepts **bash** for
// # this problem. Your extension ran something like:
// #   leetcode show 195 -l python3
// # which triggers: `[ERROR] Not supported language "python3"` (exit code may still
// # be 0 while logging the error — confusing but common).
// #
// # **Fix — switch the active language to Bash for this problem:**
// #
// # 1. **Status bar:** With the LeetCode sidebar open, many setups show the current
// #    language (e.g. Python3) on the bottom bar — click it and choose **Bash**.
// #
// # 2. **Command Palette:** `Cmd+Shift+P` → run **“LeetCode: Switch Default Language”**
// #    (wording may vary slightly by extension version) → pick **bash**.
// #
// # 3. **Settings:** Search settings for `leetcode` / default language and set the
// #    default for **Shell** problems to bash if your plugin supports per-category
// #    defaults.
// #
// # 4. When **creating/opening** the problem file, ensure the extension generates
// #    a `.sh` solution stub, not `.py`. Use **`195.tenth-line.sh`** for submission.
// #
// # After switching to bash, `leetcode show 195 -l bash` should work without the
// # language error.
// #
// # =============================================================================
// # INTERVIEW / NOTES (problem 195 — Tenth Line)
// # =============================================================================
// #
// # Task: Read `file.txt`, print **only** the 10th line (including its newline in
// # shell terms — usually `sed` prints the line without adding extra blank lines).
// #
// # **If fewer than 10 lines:** Print **nothing** (empty stdout). That is the usual
// # convention for `sed -n '10p'` and matches LeetCode’s spoiler note.
// #
// # **Three classic approaches:**
// #
// #   1. `sed -n '10p' file.txt` — print line 10 only; no output if missing.
// #   2. `awk 'NR==10' file.txt` — same behavior when line 10 absent.
// #   3. `head -n 10 file.txt | tail -n 1` — line 10 if it exists; if <10 lines,
// #      `head` outputs fewer lines and `tail -n 1` prints the **last** line present
// #      (WRONG for strict “10th line only”). Prefer **sed** or **awk** for LC.
// #
// # Complexity: O(n) to reach line 10 in the worst case (streaming); O(1) extra
// # space for sed/awk line buffer semantics.
// #
// # Local test (optional):
// #   bash 195.tenth-line.sh   # requires file.txt in cwd
// #
// # =============================================================================
// 
// # This file is **not** submitted to LeetCode for problem 195.
// # Use:  195.tenth-line.sh

#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

int main() {
    ifstream in("file.txt");
    string line;
    for (int i = 1; getline(in, line); ++i) {
        if (i == 10) {
            cout << line << '\n';
            break;
        }
    }
    return 0;
}
