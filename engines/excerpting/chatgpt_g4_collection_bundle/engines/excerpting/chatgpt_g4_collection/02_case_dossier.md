# Purpose and scope

This dossier preserves the G4 case as questionnaire-side collection material. It is not promoted doctrine.

The case asks whether a later block of conditions should be kept separate or combined with earlier conditions. The owner's answer is not a flat merge-vs-separate preference. It is about content-first condition excerpting, robust continuation support, and careful application of the short-and-harmless rule.

# Explicit layer separation

## Owner-faithful questionnaire layer
- The excerpt should stay separate from earlier conditions.
- A mere note is too weak.
- Stronger continuation support is needed.
- Each condition should have its own place.
- Some internal sub-excerpting is still needed inside this block.
- Not every short extra phrase is harmless.

## Expanded engineering / protocol layer
- Continued-topic detection
- Condition-level branching
- Subcondition branching
- Context carryover rules
- Short-and-harmless analysis
- Proximity-aware overlap
- Naming / vocabulary pressure
- Arabic-only internal naming pressure
- Machine-readability pressure

# Core assessment thesis

This should not become one mega-condition entry. The right direction is to keep the later condition block separate from earlier conditions, but make continuation explicit and reliable. Inside the block itself, multiple distinct conditions and subconditions still need further excerpting.

# Why this should not become one mega-condition entry

Merging this back into earlier conditions would hide real structure:
- `كون المسروق من حرز`
- `مرجع الحرز`
- `انتفاء الشبهة`
- `تطبيقات الشبهة`
- `ثبوت السرقة`
- `الإقرار`
- `الشاهدان`

These are not one homogeneous unit. Some are conditions, some are reference/explanatory material, some are applications, some are methods of establishing the condition.

# Why continuation matters

The phrase `تقدم بعضها` is not trivial. It tells the owner:
- this is not the whole condition-set
- another portion exists elsewhere
- the author split the topic across the text

If the system misses that, the owner may falsely read this block as self-sufficient.

# Why a note alone may be too weak

A minimal note like “earlier conditions were mentioned” is weaker than what the owner is asking for. The stronger direction is:
- show where the earlier part is
- show what came in between
- make clear that the topic was resumed
- preserve the resumed-state as part of study reassurance

# Condition-by-condition splitting pressure

The excerpt as given contains multiple distinct conditions, not one:
1. `كون المسروق من حرز مثله`
2. `انتفاء الشبهة`
3. `ثبوت السرقة`

And some of these contain further internally separable material:
- `مرجع الحرز`
- `تطبيقات الشبهة`
- `الإقرار`
- `الشاهدان`

# Sub-excerpting pressure inside conditions

Two strong examples:
- `كون المسروق من حرز` vs `مرجع الحرز`
- `ثبوت السرقة` vs its two methods (`إقرار`, `شاهدان`)

The case shows that even within one resumed condition block, sub-excerpting can still be justified.

# Context carryover doctrine

Some surrounding text is not direct core content but can still remain attached if:
- it is harmless
- it gives reassurance
- it helps explain why the text appears resumed here

Examples:
- `٤ء للعلماء شروط في قطع يد السارق، تقدم بعضها:`
- `وأهم الباقي`

# Short-and-harmless doctrine

Shortness is not enough. The key test is:
- short
- harmless
- beneficial

A short phrase can still be harmful if it introduces a different شرط and causes silent linkage/confusion.

# Branch proximity doctrine

The owner's raw comments add an important refinement:
- same-branch siblings are much safer places for retained overlap
- distant branches are more dangerous
- proximity changes whether harmless retained overlap will self-resolve during study

# Continued-topic detection doctrine

The system should ideally detect:
- this topic was started earlier
- this is a resumed portion
- the owner should be shown where the earlier part is
- the owner should be shown what intervened
- the owner should be shown why the author may have resumed here

# Naming / vocabulary / machine-readability pressure

This case also pressures internal project vocabulary:
- `entry` is ambiguous
- branch / parent / sibling / leaf need stable definitions
- internal naming should be Arabic-only in the library itself
- files/specs/docs should be as machine-readable as possible for agents

# Arabic-only internal naming pressure

The owner explicitly demands Arabic-only internal naming for the actual library layer:
- titles
- naming
- taxonomy labels

The engineering collection may explain in English where useful, but the library-facing naming pressure is Arabic-first.

# What would be reckless to flatten

- treating earlier mention of conditions as a reason to merge everything
- treating a small note as enough continuation support
- treating every short phrase as harmless
- treating same-branch and distant-branch overlap as equivalent
- ignoring naming/vocabulary pressure

# What would be reckless to automate blindly

- blind merge because “earlier conditions exist”
- blind split of every comma-separated phrase
- blind retention of every short phrase
- blind assumption that continued topics are obvious to the owner
- blind naming without stable vocabulary and agent-readable formats
