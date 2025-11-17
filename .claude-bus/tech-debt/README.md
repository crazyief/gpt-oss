# Technical Debt Tracking

## Purpose
This directory tracks technical debt accumulated during development. Technical debt represents shortcuts, workarounds, or suboptimal solutions that should be improved in future stages.

## When to Create Debt Records

### During Phase 2 (Development)
- Developer agents recognize they're implementing a workaround
- Time pressure forces quick fix instead of proper solution
- Lack of information prevents ideal implementation

### During Phase 3 (Review)
- QA-Agent identifies code that passes standards but could be better
- Complex code that works but is hard to maintain
- "Approved with comments" reviews

### During Phase 5 (Integration)
- Performance acceptable but not optimal
- Features work but need refactoring

## Debt Types

1. **Code Quality**
   - Complex functions (> 50 lines but < 400 limit)
   - Deep nesting (acceptable but not ideal)
   - Copy-pasted code (DRY violation)
   - Magic numbers/strings

2. **Architecture**
   - Temporary coupling between modules
   - Missing abstraction layers
   - Incomplete separation of concerns

3. **Performance**
   - Unoptimized queries
   - Missing caching
   - Inefficient algorithms (work but slow)

4. **Security**
   - Overly permissive access (works but not least-privilege)
   - Missing rate limiting
   - Incomplete input validation

5. **Testing**
   - Missing edge case tests
   - Low test coverage (> 20% but < 80%)
   - Integration tests missing

6. **Documentation**
   - Incomplete API docs
   - Missing inline explanations
   - Out-of-date examples

## Severity Levels

- **Critical**: Must address before Stage completion
- **High**: Should address in next stage
- **Medium**: Address when convenient
- **Low**: Nice to have, may never fix

## Workflow Integration

### Phase 3 (Review)
QA-Agent can flag technical debt:
```json
// In review results
{
  "status": "approved_with_comments",
  "comments": [
    {
      "type": "technical_debt",
      "severity": "medium",
      "suggestion": "Consider extracting helper functions for better maintainability"
    }
  ]
}
```

If flagged, QA-Agent creates debt record.

### Phase 5 (Integration)
- Review accumulated debt
- Decide paydown priority
- Include high-priority debt in Stage 2 planning

### Stage Transition
PM-Architect reviews all debt:
1. Critical debt → Must fix before stage complete
2. High debt → Add to next stage requirements
3. Medium/Low debt → Archive for future reference

## Paydown Strategy

### Immediate (Before Stage Completion)
- Critical severity items
- Security-related debt
- Items blocking next stage

### Stage 2 (Next Stage)
- High severity items
- Items affecting features planned for Stage 2
- Quick wins (low effort, high impact)

### Later (Future Stages)
- Medium/Low severity
- Items not affecting planned features
- Nice-to-have improvements

### Never (Accept as Tradeoff)
- Low severity + high effort
- Third-party limitations
- Acceptable compromises for scope

## File Naming Convention

- **Active Debt**: `Stage{N}-debt-{number}.json`
- **Resolved Debt**: Move to `archive/Stage{N}-debt-{number}.json`

Examples:
```
Stage1-debt-001.json  (active)
Stage1-debt-002.json  (active)
archive/Stage1-debt-001.json  (resolved in Stage 2)
```

## Reporting

### Debt Summary (per stage)
```bash
# Count active debt
ls *.json | wc -l

# Count by severity
grep '"severity": "critical"' *.json | wc -l
grep '"severity": "high"' *.json | wc -l

# Total estimated effort
jq -r '.estimated_effort' *.json
```

### Debt Dashboard (in PROJECT_STATUS.md)
Update with debt metrics:
- Total debt items
- Critical/High/Medium/Low counts
- Estimated total paydown effort
- Debt trend (increasing/decreasing)

## Best Practices

1. **Be Honest**: Record debt even if embarrassing
2. **Be Specific**: Exact location, current vs ideal approach
3. **Be Realistic**: Accurate effort estimates
4. **Prioritize Ruthlessly**: Not all debt needs paying
5. **Pay Down Incrementally**: Don't let debt overwhelm project

## Anti-Patterns to Avoid

❌ **Don't**: Create debt for every minor imperfection
✅ **Do**: Focus on items that genuinely affect maintainability

❌ **Don't**: Plan to fix all debt immediately
✅ **Do**: Prioritize based on impact and effort

❌ **Don't**: Let critical debt slip to next stage
✅ **Do**: Fix critical items before stage completion

❌ **Don't**: Create vague debt records
✅ **Do**: Be specific with location and solution

## Example Scenarios

### Scenario 1: Complex Function
**Situation**: Chat endpoint is 380 lines (passes 400 limit but complex)
**Action**: Create medium-severity debt
**Paydown**: Stage 2 when adding RAG features

### Scenario 2: Missing Caching
**Situation**: Database queries work but could be cached
**Action**: Create high-severity performance debt
**Paydown**: Stage 2 when optimizing for scale

### Scenario 3: Copy-Pasted Code
**Situation**: Same validation logic in 3 files
**Action**: Create medium-severity code quality debt
**Paydown**: Extract to shared utility in Stage 2

---

**Last Updated**: 2025-11-17
**Maintained By**: QA-Agent, PM-Architect-Agent
