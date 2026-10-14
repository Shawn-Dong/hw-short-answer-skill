# Before and after

Each pair shows what changed and why. The questions and numbers are made up for
illustration. The patterns come from real editing sessions.

## 1. Parenthetical explanation removed

A supporting-results line in a lab report.

Before:
> Supporting results from Q1(a) (reported for reference; graded in the notebook).

After:
> Supporting results from Q1a.

Why: the grader does not need the aside, and the parenthesis plus semicolon break two
style rules at once.

## 2. Two "not"s crowding one sentence

Question: why does a bag-of-words sentiment model give the word "not" a small weight?

Before:
> not is a stopword that shows up in every kind of review, so its count is not informative
> on its own and its weight is small.

After:
> The word not appears in positive and negative reviews alike. Its count alone says little
> about the label, so its weight is small.

Why: a sentence that starts with the token "not" and then says "is not informative" is hard
to parse. Splitting it also fixes the length.

## 3. Repeated word

Before:
> The bootstrap estimate is approximately unbiased, and its variance is approximately
> sigma^2 / n.

After:
> The bootstrap estimate is approximately unbiased. Its variance is close to sigma^2 / n.

## 4. Vague claim replaced with the run's numbers

Question: "Discuss trends you observed in training. Support your discussion with metrics."

Before:
> The validation loss curves showed differences in convergence across models. Some models
> improved more quickly, while others required more epochs to reach lower losses.

After:
> After epoch 3 the linear model barely improved. Its validation loss only went from 0.412
> to 0.409 between epoch 3 and epoch 20. The two-layer MLP was still improving at the end,
> by about 0.004 per epoch, so it would likely benefit from longer training.

## 5. Summary closer cut, last sentence ends on a fact

Before:
> In practice the weighted model was doing almost the same thing as the unweighted one. Overall, the
> experiments suggest that model complexity and hyperparameter choices need to be balanced to
> achieve good performance.

After:
> That is also why the weighted model ended at 0.871 accuracy, almost the same as the
> unweighted model's 0.868.

Why: the first sentence only restated the one before it. The "Overall" line says nothing a
reader could check.

## 6. Example that answers the question's real point

Question: "a. Describe a spam filter with recall 1 and give its precision. b. Describe one with
precision 1. What do a and b tell you about reporting either metric alone?"

Student's first idea for a:
> Fix the one spam email the current filter misses. Then recall is 1 and precision stays
> high.

Used instead:
> A filter that marks every email as spam. It catches all 30 spam emails in the 1,000-email
> test set, so recall is 1. Precision is 30/1000 = 0.03.

Why: part b asks what the two systems together say about each metric alone. A good filter
with recall 1 cannot show that. A useless filter with recall 1 can.

## 7. A contrast that stays

Question: "The random forest beat the single tree on the test set. Does this surprise you?"

Kept:
> This is not surprising.

Why: the checker flags it as a "not X" frame, but the question asked exactly this.

## 8. Same-length sentences in a row

The first three sentences were 21, 22 and 22 words. After shortening two of them:

> normalize_rows takes a matrix and returns a copy whose rows all have length 1. It divides
> each row by its Euclidean norm, which turns every dot product between rows into a cosine
> similarity. Rows of all zeros are left as they are.
