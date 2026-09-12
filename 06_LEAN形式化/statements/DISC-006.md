# DISC-006

For all nodup lists `xs` of natural numbers whose members lie in `{1,...,n}`,
if `xs` is sum-free then `xs.length ≤ (n+1)/2` (integer division).

The argument is pairing with `n+1`: if `n+1 ∈ xs`, the remaining elements inject
into `{1,...,⌊n/2⌋}` by `a ↦ min(a, n+1-a)`.

- Objects: `List Nat`, `Nat`
- Quantifiers: forall xs n
- Assumptions: members of `xs` lie in `{1,...,n}`; `xs.Nodup`; `isSumFree xs`
- Conclusion: inequality
- Note: classical upper bound, not a novelty claim
