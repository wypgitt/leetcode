package main

import (
	"sort"
	"strings"
)

func beforeAndAfterPuzzles(phrases []string) []string {
	words := make([][]string, len(phrases))
	for i, phrase := range phrases {
		words[i] = strings.Split(phrase, " ")
	}

	puzzles := map[string]bool{}
	for i, firstWords := range words {
		for j, secondWords := range words {
			if i == j || firstWords[len(firstWords)-1] != secondWords[0] {
				continue
			}
			tail := strings.Join(secondWords[1:], " ")
			if tail == "" {
				puzzles[phrases[i]] = true
			} else {
				puzzles[phrases[i]+" "+tail] = true
			}
		}
	}

	answer := make([]string, 0, len(puzzles))
	for puzzle := range puzzles {
		answer = append(answer, puzzle)
	}
	sort.Strings(answer)
	return answer
}

