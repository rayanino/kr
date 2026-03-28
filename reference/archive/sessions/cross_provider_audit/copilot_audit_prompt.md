# Copilot CLI Audit Prompt (Optional — 2 minutes)

Run this in the KR repo directory:

```powershell
copilot -p --model gpt-4.1 "Review the file shared/llm/cli_adapter.py for bugs, edge cases, and failure modes. Focus on: (1) the retry loop in the create() method (line 306) — can it ever exit without returning or raising? (2) the extract_json function — what inputs would cause silent data corruption? (3) the _invoke_codex method — the temp file cleanup in the finally block — what if the file was never created? (4) the _invoke_claude envelope extraction — what if the envelope has 'result' key but it's null? (5) thread safety — is this safe to call from multiple threads? Report each finding with severity (BLOCKING/HIGH/MEDIUM/LOW) and the specific line number."
```

Copy the output and share with the architect.
