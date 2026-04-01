
────────────────────────────────────────  
SSTcore Taxonomy Spine: Hyperbolic Volume + Chirality  
────────────────────────────────────────

A) Definitions (what you store)

For each knot/link candidate $K$ (e.g. “5\_2”, “6\_1”, “L2a1”, or a composite from your KnotPlot export), store:

1.  Topology identity


-   `id`: canonical name (Rolfsen / Hoste-Thistlethwaite / link table id)

-   `pd_code` or `dt_code`: diagram encoding (needed for robust SnapPy entry)

-   `components`: integer (1 for knots, >1 for links)

-   `is_prime`: bool

-   `knot_type`: enum {`torus`, `hyperbolic`, `satellite`, `composite`, `unknown`}


2.  Hyperbolic geometry invariant


-   `vol_hyperbolic`: float | null (Mostow-rigid volume if hyperbolic; else null)

-   `vol_ref`: float | null (reference volume used to normalize; e.g. figure-eight $4_1$)

-   `hvol_norm`: float | null defined as

    $$
    H_{\mathrm{vol}}(K) = \frac{\mathrm{Vol}(K)}{\mathrm{Vol}(K_{\mathrm{ref}})}.
    $$

    (dimensionless)


3.  Chirality / mirror label (taxonomy sign)


-   `chirality`: enum {`chiral_left`, `chiral_right`, `amphichiral`, `unknown`}

-   `sigma_chi`: int in {+1, -1, 0}  
    convention: +1 = matter (ccw), -1 = antimatter (cw), 0 = amphichiral

-   `hvol_signed`: float | null defined as

    $$
    H_{\mathrm{vol}}^{(\pm)}(K) = \sigma_{\chi}\,H_{\mathrm{vol}}(K).
    $$


4.  Your energy functional features (separate layer)


-   `C_raw`: integer | float (crossings/contacts proxy you already compute)

-   `L_rope`: float (ropelength / total length proxy)

-   `H_link`: float (helicity / Hopf-like measure if used)

-   `E_eff`: float | null

    $$
    \mathcal{E}_{\mathrm{eff}}[K]=\alpha C+\beta L+\gamma \mathcal{H}
    $$

    (exact mapping depends on your current definitions)


5.  Provenance & reproducibility


-   `source`: enum {`knot_table`, `knotplot_export`, `snappy`, `user_defined`}

-   `compute`: object with versions and tolerances (important!)

    -   `snappy_version`

    -   `tolerance_volume`

    -   `triangulation_method` (e.g. `canonical`, `randomize+verify`)

    -   `mirror_convention` (explicit, see below)


────────────────────────────────────────  
B) JSON schema (practical)  
────────────────────────────────────────

Save as `schemas/sstcore_taxonomy_knot.schema.json` (draft 2020-12-ish). Minimal shape:

```
JSON

{  
  "$schema": "https://json-schema.org/draft/2020-12/schema",  
  "title": "SSTcore Knot Taxonomy Record",  
  "type": "object",  
  "required": \["id", "components", "knot\_type", "chirality", "sigma\_chi", "source", "compute"\],  
  "properties": {  
    "id": {"type": "string"},  
    "components": {"type": "integer", "minimum": 1},  
    "pd\_code": {"type": \["string", "null"\]},  
    "dt\_code": {"type": \["string", "null"\]},  
    "is\_prime": {"type": \["boolean", "null"\]},  
    "knot\_type": {"type": "string", "enum": \["torus", "hyperbolic", "satellite", "composite", "unknown"\]},  
  
    "vol\_hyperbolic": {"type": \["number", "null"\], "minimum": 0},  
    "vol\_ref": {"type": \["number", "null"\], "minimum": 0},  
    "hvol\_norm": {"type": \["number", "null"\]},  
    "hvol\_signed": {"type": \["number", "null"\]},  
  
    "chirality": {"type": "string", "enum": \["chiral\_left", "chiral\_right", "amphichiral", "unknown"\]},  
    "sigma\_chi": {"type": "integer", "enum": \[\-1, 0, 1\]},  
  
    "features": {  
      "type": "object",  
      "properties": {  
        "C\_raw": {"type": \["number", "null"\]},  
        "L\_rope": {"type": \["number", "null"\]},  
        "H\_link": {"type": \["number", "null"\]},  
        "E\_eff": {"type": \["number", "null"\]}  
      },  
      "additionalProperties": false  
    },  
  
    "source": {"type": "string", "enum": \["knot\_table", "knotplot\_export", "snappy", "user\_defined"\]},  
  
    "compute": {  
      "type": "object",  
      "required": \["mirror\_convention"\],  
      "properties": {  
        "snappy\_version": {"type": \["string", "null"\]},  
        "tolerance\_volume": {"type": \["number", "null"\], "minimum": 0},  
        "triangulation\_method": {"type": \["string", "null"\]},  
        "mirror\_convention": {"type": "string"}  
      },  
      "additionalProperties": false  
    }  
  },  
  "additionalProperties": false  
}
```

────────────────────────────────────────  
C) Mirror & chirality conventions (don’t skip this)  
────────────────────────────────────────

You must pick one explicit convention and never deviate:

-   Define `K.mirror()` as the diagrammatic mirror (crossings flipped).

-   Decide:

    -   matter = “original orientation” = $\sigma_{\chi}=+1$

    -   antimatter = “mirror” = $\sigma_{\chi}=-1$


Then:

-   If $K$ is amphichiral (equivalent to its mirror), set $\sigma_{\chi}=0$.

-   Otherwise set $\sigma_{\chi}=\pm 1$ according to your matter/anti mapping.


Important: Hyperbolic volume itself is nonnegative. The “signed” part is purely from $\sigma_{\chi}$.

────────────────────────────────────────  
D) Computation pipeline (deterministic, robust)  
────────────────────────────────────────

Stage 0: Normalize input

-   If you receive KnotPlot geometry: convert to a knot ID if possible (DT or PD), or store as `user_defined` with `pd_code=null` and skip geometric invariants until identified.

-   If you receive table knots: you already have standard IDs.


Stage 1: Determine geometric type

-   Attempt hyperbolicity test via SnapPy:

    -   compute a triangulation from PD/DT

    -   try `M.verify_hyperbolicity()` (or equivalent)

-   Set `knot_type`:

    -   verified hyperbolic → `hyperbolic`

    -   known torus from table → `torus`

    -   else `unknown`/`satellite`/`composite` as your detector improves


Stage 2: Compute $\mathrm{Vol}(K)$ if hyperbolic

-   If hyperbolic verified:

    -   `vol_hyperbolic = M.volume()`

-   Else:

    -   `vol_hyperbolic = null`


Stage 3: Normalize volume  
Pick a fixed reference $K_{\mathrm{ref}}$. Most common is figure-eight $4_1$:

$$
H_{\mathrm{vol}}(K)=\frac{\mathrm{Vol}(K)}{\mathrm{Vol}(4_1)}.
$$

Store `vol_ref` once globally or per record (I recommend per record for reproducibility).

Stage 4: Chirality

-   Determine amphichirality/chirality:

    -   Fast route: use table metadata where available (many small knots have known chirality).

    -   Robust route: compare invariants of $K$ and mirror(K) (e.g., Jones/Alexander signature + confirm equivalence with a simplifier) to classify as amphichiral vs chiral.

-   Set `sigma_chi` and `chirality`.


Stage 5: Signed hyperbolic coordinate  
If `hvol_norm != null`:

$$
H_{\mathrm{vol}}^{(\pm)} = \sigma_{\chi}H_{\mathrm{vol}}.
$$

Stage 6: Energy features (existing SSTcore)  
Compute and store `C_raw, L_rope, H_link, E_eff` as your existing pipeline does. The taxonomy spine does not change those.

────────────────────────────────────────  
E) Classification rule (what this “route” actually means)  
────────────────────────────────────────

Use the pair $(knot\_type, H_{\mathrm{vol}}^{(\pm)})$ as a taxonomy coordinate:

-   leptons track (old rule): primarily `torus` (often zero hyperbolic volume)

-   quark track (old rule): `hyperbolic` + `sigma_chi ≠ 0`

-   neutrino / inert track (your stated hypothesis): amphichiral or effectively “signed-cancelled”

    -   operationally: `sigma_chi = 0` (amphichiral)

    -   OR a rule like “weak coupling to swirl-gravity” for near-amphichiral families


Then, within each class, your quantitative model ranks by $\mathcal{E}_{\mathrm{eff}}$.

This is the key separation:

-   Volume + chirality: “what family am I in?”

-   $\mathcal{E}_{\mathrm{eff}}$: “what mass / stability do I get?”


────────────────────────────────────────  
F) Minimal API hooks (Python + C++)  
────────────────────────────────────────

Python side (fast iteration):

-   `taxonomy.compute_record(knot_id | pd_code | dt_code) -> TaxonomyRecord`

-   `taxonomy.compute_hvol(record, ref="4_1")`

-   `taxonomy.classify(record) -> {"sector": ..., "matter_sign": ...}`


C++ side (performance):

-   Keep volume computation in Python unless you *need* it in C++ (SnapPy is Python-native).

-   Store computed invariants in your database and read them in C++ for runtime evaluation.


Recommended division:

-   Python: SnapPy + chirality classification + persistence

-   C++: your knot energy integrals and fast evaluation loops


────────────────────────────────────────  
G) Sanity checks (unit tests you should add)  
────────────────────────────────────────

1.  Hyperbolic volume invariance under re-triangulation (within tolerance):


-   compute volume multiple times after randomization; assert stddev < eps


2.  Mirror volume equality:


-   `Vol(K) ≈ Vol(mirror(K))` for hyperbolic knots


3.  Amphichiral sign cancellation:


-   if amphichiral → `sigma_chi == 0` and `hvol_signed == 0` (even though volume may be nonzero)


4.  Non-hyperbolic:


-   torus knots → `vol_hyperbolic == null` (or 0, but null is cleaner)


────────────────────────────────────────  
H) Practical next step in your repo  
────────────────────────────────────────

1.  Add `schemas/sstcore_taxonomy_knot.schema.json`

2.  Add `taxonomy/compute_taxonomy.py` (SnapPy-based)

3.  Create `data/taxonomy_db.jsonl` (one record per line) so it scales

4.  Update your evaluator to load `hvol_signed` and `knot_type` as features for taxonomy-only gating