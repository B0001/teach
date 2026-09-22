SUBGROUPS_BLIND = """Tutor: Today let's talk about subgroups. Before we dive in, remind me what a group is.

Student: A group is a set G with a binary operation that's associative, has an identity element, and every element has an inverse. Closure too — combining two elements stays in the set.

Tutor: Exactly. Now, a subgroup is just what it sounds like: a subset H of G that is itself a group, using the same operation as G. So if G is a group under multiplication, H must also form a group under that same multiplication.

Student: So I just need H to satisfy those four axioms again — closure, associativity, identity, inverses?

Tutor: Almost — you get one for free. Which one?

Student: Associativity! If the operation is associative on all of G, it's automatically associative on any subset, since it's the same operation.

Tutor: Right. So really you only need to check three things to prove H is a subgroup: closure, identity, and inverses. That's called the subgroup test.

Student: Can you state it precisely?

Tutor: Sure. Let G be a group and H a nonempty subset of G. H is a subgroup if: (1) for all a, b in H, ab is in H — closure; (2) the identity e of G is in H; (3) for all a in H, a⁻¹ is in H. If all three hold, H is a subgroup of G, written H ≤ G.

Student: Why does H need to be nonempty explicitly? Doesn't containing the identity already guarantee that?

Tutor: You're right that condition (2) implies nonemptiness, so some textbooks fold "nonempty" into the identity condition rather than stating it separately. Either way works — the point is you can't have an empty subgroup, since every group needs an identity.

Student: Is there a shortcut version? I feel like I've seen a "one-step" test.

Tutor: Good memory. The one-step subgroup test says: H is a subgroup of G if and only if H is nonempty and for all a, b in H, ab⁻¹ is in H. That single condition packages closure and inverses together, and you can derive the identity's membership from it by taking a = b.

Student: Let's do an example. How about the integers under addition?

Tutor: Perfect group to work with, since here "ab" really means "a + b" and "a⁻¹" means "−a". Consider G = ℤ, and let H = 2ℤ, the even integers. Is H a subgroup?

Student: Check closure: even plus even is even, so that's fine. Identity: 0 is even, so 0 is in H. Inverses: if a is even, is −a even? Yes. So 2ℤ is a subgroup of ℤ.

Tutor: Nicely done. In fact, nℤ — all multiples of any fixed integer n — is a subgroup of ℤ for the same reasons. These are literally all the subgroups of ℤ.

Student: What about a non-example, so I can see what goes wrong?

Tutor: Take H = odd integers, as a subset of ℤ under addition. Try closure.

Student: 1 + 3 = 4, which isn't odd. Closure fails immediately. Also 0 isn't in there, so identity fails too. So the odd integers are not a subgroup.

Tutor: Right — it's not even a group on its own, let alone a subgroup. Let's try something with a finite group. Consider G = ℤ₆, the integers mod 6 under addition, and let H = {0, 2, 4}.

Student: Closure: 2+4 = 6 = 0 mod 6, still in H; 4+4=8=2 mod 6, in H. Looks closed. Identity 0 is there. Inverses: the inverse of 2 mod 6 is 4, since 2+4=6=0, and 4 is in H; inverse of 4 is 2, also in H. So {0,2,4} is a subgroup of ℤ₆.

Tutor: Exactly right — it's actually a copy of ℤ₃ sitting inside ℤ₆. One more concept while we're here: every group G has two "trivial" subgroups. Can you name them?

Student: G itself, since it trivially satisfies its own axioms, and {e}, the set containing just the identity — closure holds since e·e = e, identity is there, and e is its own inverse.

Tutor: Exactly. Any subgroup other than those two is called a proper nontrivial subgroup, like our 2ℤ or {0,2,4} examples. That framework — check closure, identity, inverses, or use the one-step test — is really all you need to verify a subgroup in practice.

Student: That makes sense. So the real work is usually just closure and inverses, since identity is often obvious and associativity is inherited for free.

Tutor: That's exactly the right instinct, and it's why the one-step test is so popular — it isolates the two conditions that actually take effort to verify."""

QUOTIENT_GROUPS_BLIND = """Tutor: Last time we talked about subgroups. Today let's build something new out of them — a quotient group. Ever heard of it?

Student: The name sounds like division. Are we dividing a group by a subgroup?

Tutor: That's exactly the right instinct. But before we can "divide," we need to know which subgroups we're allowed to divide by. Not every subgroup works — we need what's called a normal subgroup.

Student: What makes a subgroup normal?

Tutor: A subgroup N of G is normal if, for every element g in G, gNg⁻¹ = N. In words: conjugating N by any element of G just gives you N back. You can also say gN = Ng for all g — the left and right cosets coincide.

Student: Cosets — remind me what those are again?

Tutor: For a subgroup N and an element g in G, the left coset gN is the set {gn : n in N}. Think of it as taking N and "shifting" it by g. Right cosets Ng are defined the same way, just multiplying on the other side.

Student: And these cosets somehow split up the whole group?

Tutor: Right. The left cosets of N partition G — every element of G lies in exactly one coset. That follows because coset membership is an equivalence relation: g₁N = g₂N exactly when g₁⁻¹g₂ is in N. So G gets chopped into disjoint blocks, each one the same size as N.

Student: Okay, so far this works for any subgroup, normal or not. Where does normality come in?

Tutor: Great catch — the partition into cosets happens regardless. Normality is what lets us multiply cosets together and get a well-defined group operation. We want to define (aN)(bN) = abN, but for that to make sense, the answer can't depend on which representatives a and b we picked from their cosets.

Student: And that fails if N isn't normal?

Tutor: Exactly. If N isn't normal, you can pick different representatives of the same cosets and get products landing in different cosets — the operation isn't well-defined. Normality (gNg⁻¹ = N) is precisely the condition that makes the multiplication consistent no matter which representatives you choose.

Student: So once N is normal, the set of all cosets becomes a group?

Tutor: Yes. That set — denoted G/N, read "G mod N" — is the quotient group, or factor group. Its elements are the cosets of N, the operation is (aN)(bN) = abN, the identity element is N itself (that is, eN = N), and the inverse of aN is a⁻¹N.

Student: Can you make this concrete? I like an example.

Tutor: Take G = ℤ, the integers under addition, and N = 5ℤ, the multiples of 5. Since ℤ is abelian, every subgroup is automatically normal. The cosets are 0+5ℤ, 1+5ℤ, 2+5ℤ, 3+5ℤ, 4+5ℤ — five of them. Adding cosets works just like adding remainders mod 5. So ℤ/5ℤ is exactly the group you already know as ℤ₅.

Student: Oh, that's satisfying — so modular arithmetic is a special case of this construction.

Tutor: Precisely, and that's why it's called "factor" or "quotient": you're collapsing all the elements that differ by something in N down to a single point, the way remainders collapse all multiples of 5 into one class.

Student: What about a nonabelian example, so I see why normality actually matters?

Tutor: Take G = S₃, the symmetries of a triangle, and N = A₃, the alternating group of even permutations — that's a normal subgroup of index 2. G/N has just two cosets: N itself (the even permutations) and the other coset of odd permutations. That quotient is isomorphic to ℤ₂: even times even is even, odd times odd is even, even times odd is odd — exactly like parity arithmetic.

Student: And if I'd chosen a subgroup of S₃ that isn't normal?

Tutor: Say one of the order-2 subgroups generated by a single transposition — those aren't normal in S₃. You can check that left and right cosets don't match up, and if you try to multiply cosets by picking representatives, you'll get inconsistent answers. The construction just breaks down; G/N wouldn't even be well-defined as a group.

Student: So to summarize: cosets always partition G into equal-sized blocks, but you only get a bona fide group structure on those blocks when the subgroup is normal, because that's what guarantees coset multiplication doesn't depend on your choice of representative.

Tutor: That's it exactly. And one more thing to file away: |G/N| = |G|/|N| when G is finite — that's essentially Lagrange's theorem in disguise, and it's the real sense in which G/N is "G divided by N.\""""

RING_HOMOMORPHISMS_BLIND = """Tutor: Last time we nailed down what a ring is — a set with addition and multiplication satisfying certain axioms. Today let's talk about how two rings can "talk" to each other: ring homomorphisms.

Student: Is that like a group homomorphism, but for rings?

Tutor: Exactly the same spirit. A function φ: R → S between rings is a ring homomorphism if it preserves both operations: φ(a + b) = φ(a) + φ(b), and φ(a·b) = φ(a)·φ(b), for all a, b in R. If the rings have identities and we want φ to respect that too, we usually also require φ(1_R) = 1_S.

Student: So it's not enough to just preserve addition — it has to respect multiplication as well.

Tutor: Right. A map that only preserves addition is just a group homomorphism of the underlying additive groups. To be a ring homomorphism it has to respect the whole algebraic structure — both operations at once.

Student: Can you give me an example?

Tutor: Sure. Take φ: ℤ → ℤ/nℤ defined by φ(a) = a mod n, the natural reduction map. Check it: φ(a+b) = (a+b) mod n = (a mod n) + (b mod n) mod n, and similarly for multiplication. It preserves both operations, and it sends 1 to 1. That's a ring homomorphism, and it's surjective.

Student: What about a non-example, just so I know what fails?

Tutor: Take φ: ℤ → ℤ defined by φ(a) = 2a. Additive: φ(a+b) = 2a+2b = φ(a)+φ(b), fine. But multiplicative: φ(ab) = 2ab, while φ(a)φ(b) = 4ab. Those aren't equal in general, so it fails to preserve multiplication — not a ring homomorphism, even though it's a perfectly good group homomorphism of (ℤ,+).

Student: Got it. Now what's the kernel? Same idea as in group theory — things that map to zero?

Tutor: Precisely. The kernel of φ: R → S is ker(φ) = { a ∈ R : φ(a) = 0_S }. It's not just a subring — it's an ideal of R. That's the key structural fact: if a is in the kernel and r is any element of R, then φ(ra) = φ(r)φ(a) = φ(r)·0 = 0, so ra is also in the kernel. Same on the right. That absorption property is exactly what makes it an ideal rather than merely a subring.

Student: And that's why we can form quotient rings — R/ker(φ)?

Tutor: Exactly, and this gives you the First Isomorphism Theorem for rings: R/ker(φ) ≅ im(φ). In our example, ker(φ) = nℤ, and indeed ℤ/nℤ ≅ ℤ/nℤ — trivially confirming the theorem, but it's the general machinery that matters.

Student: What's the image, then — just the usual set of outputs?

Tutor: Yes: im(φ) = { φ(a) : a ∈ R }, a subset of S. Unlike the kernel, the image is a subring of S, not necessarily an ideal of S — though it certainly could be an ideal in specific cases.

Student: Wait, why is the kernel an ideal of R but the image only a subring of S, not an ideal of S?

Tutor: Good question. The image sits inside S, and ideal-ness of a subset means it absorbs multiplication by *everything* in S. There's no reason multiplying an element of im(φ) by some arbitrary element of S — which might not itself be in the image — should land back in the image. The kernel's absorption property came from φ being a homomorphism out of R, acting on elements of R; the image doesn't get that same leverage over S.

Student: Can you show me an example where the kernel is trivial?

Tutor: Consider the inclusion map ι: ℤ → ℚ. It's a ring homomorphism — clearly preserves + and ×. Its kernel is {0}, since no nonzero integer maps to 0 in ℚ. A homomorphism with trivial kernel is injective, just like in group theory: if φ(a) = φ(b), then φ(a - b) = 0, so a - b ∈ ker(φ) = {0}, forcing a = b.

Student: So trivial kernel if and only if injective — same criterion as for groups.

Tutor: Same criterion, same proof idea, because a ring homomorphism is in particular a homomorphism of the underlying additive groups, and injectivity is really an additive-group question once you have that linearity.

Student: One more example to cement this — what about evaluation maps?

Tutor: Great one. Let φ: ℝ[x] → ℝ be evaluation at 0, φ(f) = f(0). This is a ring homomorphism: (f+g)(0) = f(0)+g(0), and (fg)(0) = f(0)g(0). The kernel is all polynomials with constant term 0 — that is, all polynomials divisible by x, the ideal (x). The image is all of ℝ, since constant polynomials already hit every real number. So by the isomorphism theorem, ℝ[x]/(x) ≅ ℝ.

Student: That's a nice way to see quotienting by an ideal as "forgetting information down to what the homomorphism can see."

Tutor: That's exactly the right intuition. The kernel measures what collapses to zero — what the map can't distinguish from zero — and the image tells you how much of the target you actually reach. Together they completely control the structure of the map, and the isomorphism theorem tells you the "essential content" of R modulo that collapsing is faithfully realized as the image inside S."""

RING_AXIOMS_BLIND = """Tutor: Today let's talk about rings. You know groups already—a ring is going to build on that idea, but now we'll have two operations instead of one.

Student: Two operations? Like addition and multiplication?

Tutor: Exactly. Formally, a ring is a set R with two binary operations, usually written + and ×, satisfying a specific list of axioms. First, R together with + has to be an abelian group. So addition is associative, commutative, there's an additive identity 0, and every element has an additive inverse.

Student: Okay, so addition is "well-behaved" in the full group sense. What about multiplication?

Tutor: Multiplication is required to be associative—(ab)c = a(bc)—but notice I didn't say commutative or that inverses exist. Multiplication doesn't need to form a group at all. In fact most rings don't have multiplicative inverses for every element.

Student: So multiplication is weaker than addition. What ties the two operations together?

Tutor: The distributive laws. a(b + c) = ab + ac, and (a + b)c = ac + bc. That's the axiom that really makes it a "ring"—without distributivity, + and × would just be two unrelated structures sitting on the same set.

Student: Does a ring need a multiplicative identity, like a 1?

Tutor: Depends on convention. Many modern textbooks, including Judson's, require a multiplicative identity 1 with 1 ≠ 0, and call that a "ring with unity" or "ring with identity." Some older texts don't require it. I'll assume we want a 1 unless I say otherwise.

Student: Can you give me the simplest example?

Tutor: The integers, ℤ, with ordinary addition and multiplication. Addition makes ℤ an abelian group—0 is the identity, -n is the inverse of n. Multiplication is associative, distributes over addition, and 1 is the multiplicative identity. But notice: 2 has no multiplicative inverse in ℤ, since there's no integer x with 2x = 1. That's fine—rings don't require that.

Student: So ℤ is a ring but not a field, since it's missing multiplicative inverses.

Tutor: Right, that's exactly the distinction. A field is a ring where every nonzero element does have a multiplicative inverse, and multiplication is commutative. ℚ, ℝ, ℂ are fields; ℤ is "just" a ring.

Student: What about something less number-like, like matrices?

Tutor: Great example. Take M₂(ℝ), the set of all 2×2 matrices with real entries. Matrix addition is entrywise, so it's an abelian group with the zero matrix as identity. Matrix multiplication is associative and distributes over addition—those are standard facts from linear algebra. The identity matrix I plays the role of 1.

Student: But matrix multiplication isn't commutative.

Tutor: Exactly, and that's the point of bringing it up. AB ≠ BA in general. So M₂(ℝ) is a ring, even a ring with identity, but it's a noncommutative ring. It also has zero divisors—nonzero matrices A and B where AB = 0 even though neither is 0 individually.

Student: Zero divisors—that can't happen in ℤ, right?

Tutor: Correct, ℤ has no zero divisors: if ab = 0 for integers, then a = 0 or b = 0. Rings without zero divisors, that are also commutative with identity, get a special name—integral domains. So ℤ is an integral domain, but M₂(ℝ) is not.

Student: So the axioms are pretty minimal, and then extra properties like commutativity, identity, or no zero divisors carve out these named subclasses—rings, then commutative rings, then integral domains, then fields.

Tutor: That's exactly the hierarchy. It's a good way to organize the whole subject: start from the bare ring axioms—abelian group under +, associative and distributive ×—and each additional property you impose narrows the class and gives you more structure to work with."""

INTEGRAL_DOMAINS_FIELDS_BLIND = """Tutor: Let's talk about integral domains and fields. Before we get there, I want to start with something called a "zero divisor." Do you remember what it means for two numbers to multiply to zero?

Student: Sure, like if a times b equals zero, then either a is zero or b is zero. That's just... how numbers work, right?

Tutor: Right, and that property feels so obvious we don't even notice it's a property. But it actually fails in some rings. A zero divisor is a nonzero element a in a ring such that there's some other nonzero element b where a times b equals zero. So the product vanishes even though neither factor did.

Student: Can you give me an example where that actually happens?

Tutor: Take the ring Z/6Z, the integers mod 6. Consider 2 and 3. Neither one is zero mod 6. But 2 times 3 is 6, which is 0 mod 6. So 2 and 3 are both zero divisors in that ring.

Student: Huh. So multiplication can "lose information" — you can't just cancel things the way you're used to.

Tutor: Exactly, and that's the real consequence. In the integers, if ac = bc and c isn't zero, you can cancel c and conclude a = b. In Z/6Z that fails: 2 times 1 is 2, and 2 times 4 is 8, which is also 2 mod 6. So 2·1 = 2·4 but 1 ≠ 4. Cancellation breaks down whenever zero divisors are around.

Student: Okay, so an integral domain is a ring where that can't happen?

Tutor: Precisely. An integral domain is a commutative ring with a multiplicative identity 1 ≠ 0, that has no zero divisors — meaning if ab = 0, then a = 0 or b = 0. The integers Z are the classic example, which is where the name comes from.

Student: What about Z/6Z — is that not an integral domain because of the 2 and 3 thing?

Tutor: Right, Z/6Z is not an integral domain, precisely because 2·3 = 0 with both factors nonzero. But contrast that with Z/5Z, integers mod a prime. There, you can check every nonzero pair multiplies to something nonzero. In fact Z/pZ is an integral domain whenever p is prime — that's exactly why primality matters here.

Student: So now where does a field fit in? Is that the same thing?

Tutor: Related, but stronger. A field is a commutative ring with 1 ≠ 0 where every nonzero element has a multiplicative inverse — for each nonzero a, there's some a⁻¹ with a·a⁻¹ = 1. Q, R, and C are all fields. The integers are not a field, since, say, 2 has no integer inverse — 1/2 isn't an integer.

Student: Does being a field automatically make you an integral domain?

Tutor: Yes, always. Suppose F is a field and ab = 0 with a ≠ 0. Since a is nonzero, it has an inverse a⁻¹. Multiply both sides by a⁻¹: a⁻¹(ab) = a⁻¹·0, so b = 0. So no zero divisors can exist — every field is an integral domain.

Student: But not every integral domain is a field, since you said Z is a domain but not a field.

Tutor: Exactly right. Z is the standard example of a domain that isn't a field — no zero divisors, but most elements lack inverses. So the containment goes one way: fields ⊂ integral domains ⊂ commutative rings, and each inclusion is strict.

Student: Is there a case where they actually coincide — where a domain is forced to be a field?

Tutor: Yes — any finite integral domain is automatically a field. The idea: fix a nonzero a, and look at the map x ↦ ax on the finite domain. Because there are no zero divisors, this map is injective, and an injective map from a finite set to itself must be surjective too. So some x satisfies ax = 1, meaning a has an inverse. That's exactly why Z/pZ for prime p is not just a domain but a full field — it's finite.

Student: That also explains why Z/6Z fails on both counts — it's finite, so if it had no zero divisors it'd have to be a field, but it does have zero divisors, so it's neither.

Tutor: That's a nice way to tie it together. Zero divisors are the obstruction — kill them and, in the finite case, you get inverses for free too."""
