#!/usr/bin/env bash
# LeetCode 195 — Tenth Line (submit in Shell / Bash tab only).
#
# If file.txt has fewer than 10 lines, sed prints nothing (empty output), which
# matches typical judge expectations for this problem.

sed -n '10p' file.txt
