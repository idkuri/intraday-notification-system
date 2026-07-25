from __future__ import annotations

from pathlib import Path

from lib.trigger_field_config import TRIGGER_FIELD_CONFIG


def _bool_ts(value: bool) -> str:
    return "true" if value else "false"


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    output_path = (
        repo_root / "client" / "src" / "routes" / "rules" / "triggerFormConfig.generated.ts"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    blocks: list[str] = []
    for trigger_type, config in TRIGGER_FIELD_CONFIG.items():
        blocks.append(
            "\n".join(
                [
                    f"\t{trigger_type.value}: {{",
                    f"\t\tshowAgentId: {_bool_ts(config.show_agent_id)},",
                    f"\t\tshowQueueIds: {_bool_ts(config.show_queue_ids)},",
                    f"\t\tshowThreshold: {_bool_ts(config.show_threshold)},",
                    f"\t\tshowTargetState: {_bool_ts(config.show_target_state)},",
                    f"\t\tagentIdRequired: {_bool_ts(config.agent_id_required)},",
                    f"\t\tqueueIdsRequired: {_bool_ts(config.queue_ids_required)},",
                    f"\t\trequireAgentOrQueues: {_bool_ts(config.require_agent_or_queues)},",
                    "\t},",
                ]
            )
        )

    content = (
        "/* generated using export_trigger_field_config.py — do not edit */\n"
        "import type { TriggerType } from '@/api-client'\n"
        "\n"
        "/** Which create/edit fields a trigger type shows or requires. */\n"
        "export interface TriggerFieldConfig {\n"
        "\tshowAgentId: boolean\n"
        "\tshowQueueIds: boolean\n"
        "\tshowThreshold: boolean\n"
        "\tshowTargetState: boolean\n"
        "\tagentIdRequired: boolean\n"
        "\tqueueIdsRequired: boolean\n"
        "\trequireAgentOrQueues: boolean\n"
        "}\n"
        "\n"
        "export const TRIGGER_FIELD_CONFIG: Record<TriggerType, TriggerFieldConfig> = {\n"
        + "\n".join(blocks)
        + "\n}\n"
    )
    output_path.write_text(content, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
