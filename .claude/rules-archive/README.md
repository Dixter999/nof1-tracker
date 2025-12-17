# Rules Archive

This directory contains rules that were archived to optimize Claude Code memory usage for the nof1-tracker scraper project.

## Why These Rules Were Archived

These 23 rules were moved here because they don't apply to a **Python-based data scraper** with PostgreSQL:

### Not Using These Technologies
- **AI/ML APIs**: Not integrating with OpenAI, Gemini, or LangChain
- **Kubernetes**: Using simple Docker, not K8s orchestration
- **Cloud Infrastructure**: Not deploying to AWS/Azure/GCP with complex setups
- **Frontend**: No UI - backend scraper only

### Verbose Alternatives Exist
- Kept optimized versions of agent and context7 rules
- Archived verbose duplicates to save tokens

### General Advice Files
- Too verbose for context window
- Basic principles covered in essential rules

## Can These Rules Be Restored?

**Yes!** If the project evolves to need these technologies:

```bash
# Restore a specific rule
mv .claude/rules-archive/ui-development-standards.md .claude/rules/

# Restore all rules
mv .claude/rules-archive/*.md .claude/rules/
```

## Current Optimization

- **Before**: 42 rules, ~36,000 words (~48,000 tokens)
- **After**: 19 rules, ~13,860 words (~18,500 tokens)
- **Savings**: 61% reduction in context usage

## Archived Files List

1. `ai-integration-patterns.md`
2. `ai-model-standards.md`
3. `prompt-engineering-standards.md`
4. `ci-cd-kubernetes-strategy.md`
5. `cloud-security-compliance.md`
6. `infrastructure-pipeline.md`
7. `development-environments.md`
8. `ui-development-standards.md`
9. `ui-framework-rules.md`
10. `agent-mandatory.md` (kept optimized version)
11. `context7-enforcement.md` (kept optimized version)
12. `context-hygiene.md`
13. `code-quality-standards.md`
14. `definition-of-done.md`
15. `golden-rules.md`
16. `performance-guidelines.md`
17. `security-checklist.md`
18. `test-coverage-requirements.md`
19. `no-pr-workflow.md`
20. `devops-troubleshooting-playbook.md`
21. `pipeline-mandatory.md`
22. `framework-path-rules.md`
23. `use-ast-grep.md`

---

**Note**: This optimization is specific to the nof1-tracker scraper project. A different project might need different rules.
