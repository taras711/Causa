# Pilot Setup for Months 11-12

## Environment Verification Complete ✅

All systems verified and ready for design partner pilot:

### Verified Components:
- ✅ `src/core/telemetry.py` - Full telemetry module (StepMetric, AgentCallMetric, TelemetryRecord, TelemetryTracker, @track_step, @track_agent_call)
- ✅ `src/core/engine.py` - WorkflowEngine with telemetry integration (step tracking, completion/failure handling, security events, duration_ms calculation)
- ✅ `src/config/settings.py` - Configuration loading from .env
- ✅ `.env` - Environment configuration exists
- ✅ All 193 tests passing (98 unit + 22 eval + 73 security)
- ✅ README.md roadmap months 9-10 marked complete
- ✅ docs/TECHNICKA_DOKUMENTACE.md - Telemetry section documented

### Quick Verification:
```python
from src.core.telemetry import StepMetric, AgentCallMetric, TelemetryRecord, TelemetryTracker, track_step, track_agent_call, get_tracker
from src.core.engine import WorkflowEngine
from src.config.settings import Settings

s = Settings()  # OK
print("All systems ready for pilot")
```

## Pilot Preparation Checklist

### 1. Environment Setup ✅
- Virtual environment activated (.venv)
- Dependencies installed (`pip install -e .`)
- Ollama running with models: qwen3.5:4b, qwen3:14b, nomic-embed-text
- .env configured (already present)

### 2. Core Ready for Partner ✅
- Workflow engine with checkpointing
- Telemetry tracking of all steps and agent calls
- Security event capture on failures
- Ledger integration for audit trail

### 3. Design Partner Onboarding
- Provide access to local instance (`python -m src.api.main` or Docker Compose)
- Share test A3 cases from `tests/eval/conftest.py` (2 golden cases available)
- Documented API endpoints at `/cases`, `/agents`, `/knowledge`, `/quant`
- Telemetry data accessible via `get_tracker()` for monitoring

### 4. Time Reserve (20-25%)
- Recommended: 8-9 hours of 40-hour work week reserved for pilot feedback, adjustments, and unexpected issues
- Buffer for: design partner onboarding, real case processing, issue debugging, finalization

## Next Steps for Pilot

1. **Start the API**: `python -m src.api.main` (or via Docker Compose)
2. **Test with golden cases**: Use the 2 test A3 cases from `tests/eval/conftest.py`
3. **Monitor telemetry**: Use `get_tracker()._records` to view step metrics and agent calls
4. **Collect feedback**: From design partner on workflow, telemetry usefulness, any issues
5. **Allocate reserve time**: 20-25% of development time for pilot-related work

## Telemetry Monitoring During Pilot

The telemetry tracker automatically records:
- Each workflow step: duration, status (running/completed/failed), result size
- Each agent call: prompt/completion tokens, latency, success/failure
- Security events: step failures, injection attempts, error payloads
- Flush interval: every 100 records (configurable)

Data can be accessed via:
```python
tracker = get_tracker()
for record in tracker._records:
    print(f"{record.event}: {record.data}")
```

---

**Status**: Ready to proceed with design partner pilot. All foundations complete, no blocking issues.