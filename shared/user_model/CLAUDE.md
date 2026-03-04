# User Model — نموذج المستخدم

**Responsibility:** Persistent model of the user's scholarly state. Tracks what the user has studied, what they know, what their gaps are, and what their current focus is. Read by the scholar interface for personalization; updated by both the interface (interaction tracking) and the processing engines (new content alerts).

## Data Tracked

- **Curriculum state:** Active curricula per science, current position in each, completion percentage, recommended next steps
- **Study history:** Which entries viewed, which excerpts engaged with, timestamps, duration, depth of engagement
- **Demonstrated knowledge:** Results of Socratic dialogue sessions, comprehension assessments, per-topic mastery estimates
- **Knowledge gaps:** Topics with low or zero engagement, schools not represented in study history, sciences not yet started
- **Current focus:** Active study areas, recent query patterns, declared interests
- **Preferences:** Depth vs. breadth, preferred interaction style, language preferences, study schedule, learning pace
- **Bookmarks and annotations:** User-created markers and notes on excerpts/entries
- **Scholarly level:** Per-science estimate of current level (beginner → intermediate → advanced → researcher), updated by assessment

## Integration Points

- Scholar interface reads the model for every interaction
- Processing engines write alerts: "New excerpts relevant to user's focus area"
- Taxonomy engine contributes coverage analysis per user's engaged topics
- Spaced repetition system reads and writes review schedules
