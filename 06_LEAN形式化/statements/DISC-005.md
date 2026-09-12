# DISC-005

The list `[1, 2, 3]` is not sum-free, because `1+2=3`.

This is the witness used by the Python falsifier on `{1,2,3}` inside `{1,...,5}`.

- Objects: `List Nat`
- Quantifiers: none
- Assumptions: `isSumFree` forbids `a+b` in the list, including `a=a`
- Conclusion: negation
