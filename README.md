# hw-short-answer

A [Claude Code](https://claude.com/claude-code) skill for writing and polishing the short
written answers in homework: LaTeX problem sets, "Answer:" cells in Jupyter notebooks, lab
reports and closing discussions. It comes with a checker script that flags the patterns that
make an answer read as padded or machine-written.

The rules in one breath: answer only what is asked, back claims with your own numbers, keep
sentences short, and use no parentheses, semicolons or dashes in prose.

## What it does

- **Interactive workflow.** The student states their reasoning first. Claude corrects it,
  explains what was wrong, and only then writes the English answer in the student's own words.
- **Content rules.** Answer the question that was asked, use the mechanism the question names,
  quote numbers exactly as the notebook printed them, and say when a comparison is not fair.
- **Style rules.** Short sentences, no parenthetical asides, no semicolons or dashes, varied
  sentence openings, and no summary closer.
- **Layout rules.** One problem per page in LaTeX, pages that match the grader's question
  outline, and answers placed in the notebook's own answer cells.
- **Checker.** `scripts/check_answers.py` reads `.tex`, `.ipynb`, `.md` and `.txt`. It finds the
  answer text in each file and reports ERRORs to fix and WARNs to judge.

## Install

Copy the `hw-short-answer` folder into a skills directory:

```bash
# for one project
cp -r hw-short-answer /path/to/your/project/.claude/skills/

# or for every project
cp -r hw-short-answer ~/.claude/skills/
```

Claude Code picks it up automatically. It triggers when you ask Claude to write, correct,
polish or check a homework answer.

## Run the checker on its own

```bash
python3 hw-short-answer/scripts/check_answers.py solution.tex
python3 hw-short-answer/scripts/check_answers.py hw2.ipynb --all
python3 hw-short-answer/scripts/check_answers.py answers.md
```

Only the Python standard library is needed. The exit code is 1 if any ERROR is found, so it
also works as a pre-submit check.

| Level | Rules |
|---|---|
| ERROR | dashes, semicolons, parenthetical asides, stock phrases, summary closers, average sentence over 20 words, more than two "not X but Y" frames |
| WARN | overused AI words, "A, B and C" lists, contrast frames, sentences over 30 words, stacked hedges, three sentences in a row with the same opening |

Math such as `f(x)` and references to sub-question labels such as "model (b)" are not counted
as parentheses.

## Customize

The style rules are one student's preferences. Edit `SKILL.md` to match yours, and add your
own before-and-after pairs to `references/examples.md`. Concrete examples teach the skill more
than extra rules do.

## Use it honestly

Use this only where your course allows AI assistance, and follow its disclosure policy. The
skill is built so that the reasoning comes from you and Claude helps you say it clearly. It
does not try to hide AI use.

## Credits

The AI-tells list and the checker's prose rules are adapted from
[humanizer](https://github.com/blader/humanizer) by blader and
[stop-slop](https://github.com/hardikpandya/stop-slop) by hardikpandya. Both are MIT
licensed and draw on Wikipedia's "Signs of AI writing".

## 中文说明

这是一个 Claude Code 的 skill，用来写和润色作业里的英文简答，适用于 LaTeX 书面题、notebook 里的 Answer 格子、lab report 和讨论。流程是你先说思路，Claude 纠错，再用你的话写成英文，最后用自带脚本检查破折号、分号、括号、套话、长句这些问题。规则写在 `SKILL.md` 里，可以按自己的习惯改。请只在课程允许使用 AI 的作业里使用。

## License

MIT
