from __future__ import annotations

import argparse

from app.agent.coordinator import IncidentCoordinator
from app.models.incident import Incident, IncidentSeverity
from app.services.state_store import LocalStateStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WorkRelay local incident coordination runner."
    )

    parser.add_argument(
        "--title",
        required=True,
        help="Incident title.",
    )

    parser.add_argument(
        "--description",
        required=True,
        help="Incident description.",
    )

    parser.add_argument(
        "--service",
        required=True,
        help="Affected service.",
    )

    parser.add_argument(
        "--severity",
        choices=[severity.value for severity in IncidentSeverity],
        default=IncidentSeverity.MEDIUM.value,
        help="Incident severity.",
    )

    parser.add_argument(
        "--force-remediation-failure",
        action="store_true",
        help="Simulate a remediation failure.",
    )

    parser.add_argument(
        "--fail-remediation-once",
        action="store_true",
        help="Simulate a remediation failure that recovers on retry.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    metadata: dict[str, object] = {}

    if args.force_remediation_failure:
        metadata["force_remediation_failure"] = True

    if args.fail_remediation_once:
        metadata["fail_remediation_once"] = True

    incident = Incident(
        title=args.title,
        description=args.description,
        service=args.service,
        severity=IncidentSeverity(args.severity),
        metadata=metadata,
    )

    store = LocalStateStore()
    coordinator = IncidentCoordinator(store)

    result = coordinator.handle(incident)

    print()
    print("=" * 60)
    print("WORKRELAY INCIDENT RESULT")
    print("=" * 60)
    print(f"Incident ID : {result.id}")
    print(f"Title       : {result.title}")
    print(f"Service     : {result.service}")
    print(f"Severity    : {result.severity.value}")
    print(f"Workflow    : {result.workflow}")
    print(f"Status      : {result.status.value}")
    print(f"Current Step: {result.current_step}")
    print(f"Retries     : {result.retry_count}")

    if result.resolution:
        print(f"Resolution  : {result.resolution}")

    if result.escalation_reason:
        print(f"Escalation  : {result.escalation_reason}")

    print()
    print("Coordination:")
    coordination = result.metadata.get("coordination", {})

    if isinstance(coordination, dict):
        print(f"  Provider : {coordination.get('decision_provider')}")
        print(f"  Reason   : {coordination.get('reasoning')}")

    print()
    print("Metadata:")
    print(f"  {result.metadata}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
