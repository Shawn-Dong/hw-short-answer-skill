# AI tells in homework answers

Adapted from a blog style guide's list of AI tells, which is condensed from
[humanizer](https://github.com/blader/humanizer) (MIT, based on Wikipedia's
"Signs of AI writing") and [stop-slop](https://github.com/hardikpandya/stop-slop) (MIT).
Blog-only rules (SEO, headings, links, CTAs) are dropped. Homework-specific tells are added.
Where this file conflicts with SKILL.md, SKILL.md wins.

## Why this matters

A model picks the phrasing that fits the most readers. A student answering one question for
one grader picks the phrasing that answers it. Every tell below is a default choice that adds
words without adding an answer. A grader reads dozens of these, and padding reads as either
filler or not understanding the question.

## Structure (fix on one sighting)

1. **Not X but Y.** "It is not just a gate, it is a residual." The negative half names
   something nobody claimed. State Y. Keep a contrast only when the question itself asked
   about X, for example "Does this surprise you?" answered with "This is not surprising."
2. **Summary closers.** "Overall, the experiments suggest that...", "In conclusion,...",
   "This highlights the importance of...". Cut. End on the last concrete fact.
3. **Restating the question.** "To answer what find_similar_words does, we first note that..."
   Start with the answer.
4. **Sayings that sound deep.** "At its core", "the real question is", "the key insight".
   Replace with the specific claim.
5. **Arguing with no one.** "To be clear", "It is important to note", "One might think".
   Remove unless the question raises the objection.
6. **Unrequested extras.** Named theorems the question did not ask for, extra derivations,
   background paragraphs. Graders read these as padding.

## Rhythm

7. **Forced triads.** Lists of three where the content has two or four. Real lists of data,
   names or models are fine.
8. **Dashes.** None in prose, including LaTeX `--` and `---`. Use a comma, colon or period.
9. **Semicolons.** None in prose. Split the sentence or join with a conjunction.
10. **Parentheses.** None in prose. Math notation like f(x) is fine. Fold the aside into the
    sentence or give it its own sentence.
11. **Metronome sentences.** Three sentences in a row with the same length or the same opening
    word. Change the subject or merge two.
12. **Long sentences.** Over 30 words. Split at the "so", "because" or "which".
13. **Stacked qualifiers.** "could potentially", "may possibly". Keep one hedge, and only
    where the result is genuinely uncertain. A number the notebook printed needs no hedge.
14. **Signposting.** More than one "This shows that" or "This suggests that" per answer.
    State the claim directly after the number.
15. **False agency.** "The data tells us", "the model decides". Name what computed it.

## Inflation

16. **Overused words.** delve, crucial, pivotal, robust in the figurative sense, seamless,
    leverage, showcase, underscore, foster, notably, furthermore, moreover, comprehensive,
    nuanced. One is fine. A cluster is a tell.
17. **Inflated significance.** "a significant impact on performance", "dramatically
    improves". Give the numbers and let them carry the size.
18. **-ing riders.** "..., highlighting the need for longer training." Make it its own
    sentence with the evidence, or cut it.
19. **Avoiding "is".** "serves as", "stands as", "acts as a form of". Use is, are, has.

## Homework-specific

20. **Vague comparisons.** "Some models improved more quickly than others." Name the models
    and give the numbers.
21. **Numbers that do not match the output.** Rounding 445.72 to "about 450" in one place
    and "445.7" in another. Copy the printed value and keep one precision.
22. **Hedging on your own results.** "It seems that the 1-layer model may have performed
    slightly better." The notebook printed 401.8 and 445.7. Say so.
23. **Writing about the answer.** "In this answer I will explain...", "As mentioned above".
24. **Chatbot residue.** "Great question", "I hope this helps", "Let me know".

## Formatting

25. **Bold labels on every list item** in a notebook answer. Use prose unless the labels
    carry information.
26. **Code formatting as decoration.** Backticks or `\texttt` only for identifiers the reader
    would type: function names, variable names, tokens being discussed.

## Editing procedure

1. Read the whole answer once and mark every tell, strongest first: 1, 2, 3, 6.
2. Rewrite around the main point instead of patching phrases one at a time.
3. Compare against the draft. Did any number, qualifier, condition or citation change or
   disappear? That is an error. Restore it.
4. Run `scripts/check_answers.py`. Fix every ERROR and judge every WARN.
5. Read it aloud in your head. Vary sentence length. Keep it in the user's voice.

## Keep

Specific odd details from the run, like a strange nearest neighbor; the user's own
reasoning and examples; real numbers; honest uncertainty about something the experiment
did not test. Removing tells is half the job. The answer still has to sound like this
student, who understands the material.
