# User Model — نموذج المستخدم

**Responsibility:** Persistent model of the user's scholarly state. Tracks what the user has studied, what they know, what their gaps are, and what their current focus is. Read by the scholar interface for personalization; updated by both the interface (interaction tracking) and the processing engines (new content alerts).

## Data Tracked

- **Study history:** Which entries viewed, which excerpts engaged with, timestamps, duration
- **Demonstrated knowledge:** Results of Socratic dialogue sessions, comprehension assessments
- **Knowledge gaps:** Topics with low or zero engagement, schools not represented in study history
- **Current focus:** Active study areas, recent query patterns, declared interests
- **Preferences:** Depth vs. breadth, preferred interaction style, language preferences, study schedule
- **Bookmarks and annotations:** User-created markers and notes on excerpts/entries

## Integration Points

- Scholar interface reads the model for every interaction
- Processing engines write alerts: "New excerpts relevant to user's focus area"
- Taxonomy engine contributes coverage analysis per user's engaged topics
- Spaced repetition system reads and writes review schedules
