# Zyntalic Syntax Guide

Guide to sentence structure and syntactic patterns in Zyntalic.

## Clause Structure

Zyntalic clauses follow the S-O-V-C template with specific positions for different elements.

**Basic Clause Template:**
[Subject] [Indirect Object] [Direct Object] [Obliques] [Verb] [Context Clauses] [Context Tail]

**Context Clauses:**
Context clauses are introduced by specific markers and appear after the main verb:
- Temporal: 뛀쨮 (when), 뚧홧 (while), 켓뚜 (after)
- Spatial: 홍뛸 (in/at), 뷠콮 (on), 멷뚺 (at)  
- Causal: 룏딲 (because), 솻뷨 (if)

**Context Tail:**
The distinctive Korean-style context tail ⟦ctx:...⟧ contains grammatical metadata.

## Complex Sentences

Zyntalic handles complex sentences through subordination and context marking.

**Subordination:**
Subordinate clauses are marked and positioned in the context area:
- Relative clauses follow their head nouns
- Complement clauses follow the main verb
- Adverbial clauses are marked with context markers

**Coordination:**
Multiple clauses of equal status are linked with conjunctions or juxtaposition.

### Examples

1. **Zyntalic:** teacher lesson explained 켓뚜 class ended . ⟦ctx:han=잨끑; verb=explained; args=2; type=main⟧
   **English:** The teacher explained the lesson to students after class ended.
   **Note:** Complex sentence with 1 context clause(s)

2. **Zyntalic:** sun , rises 뛀쨮 the sun rises , birds sing 뚧홧 flowers bloom . ⟦ctx:han=뎺캲; verb=rises; args=2; type=main⟧
   **English:** When the sun rises, birds sing while flowers bloom.
   **Note:** Complex sentence with 2 context clause(s)

3. **Zyntalic:** you study hard , you succeed 솻뷨 you study hard , you will succeed 홍뛸 life . ⟦ctx:han=쾗둗쾒; verb=succeed; args=1; type=main⟧
   **English:** If you study hard, you will succeed in life.
   **Note:** Complex sentence with 2 context clause(s)
