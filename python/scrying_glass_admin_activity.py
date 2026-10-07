"""Admin activity endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

class AdminActivityMixin:
    """Implement admin activity handlers using the shared server context."""

    async def export_activity_log_json(self) -> Response:
        """Export activity log json."""
        content = self.context.json.dumps(
            self.context.STATE["activity_log"],
            indent=2,
            ensure_ascii=False,
        )

        return self.context.Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition":
                    'attachment; filename="activity-log.json"',
            },
        )

    async def export_activity_log_csv(self) -> Response:
        """Export activity logs as CSV safe for spreadsheet applications."""
        formula_prefixes = (
            "=",
            "+",
            "-",
            "@",
            "\t",
            "\r",
            "\n",
            "＝",
            "＋",
            "－",
            "＠",
        )

        fieldnames = [
            "id",
            "timestamp",
            "active_combatant_id",
            "active_combatant",
            "active_combatant_state",
            "target_combatant_id",
            "target_combatant",
            "target_combatant_state",
            "action",
            "amount",
        ]

        def spreadsheet_safe(value: Any) -> Any:
            if not isinstance(value, str):
                return value

            return (
                f"'{value}"
                if value.startswith(formula_prefixes)
                else value
            )

        output = self.context.io.StringIO(newline="")
        writer = self.context.csv.DictWriter(
            output,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        for entry in self.context.STATE["activity_log"]:
            if not isinstance(entry, dict):
                continue

            writer.writerow({
                field: spreadsheet_safe(entry.get(field, ""))
                for field in fieldnames
            })

        return self.context.Response(
            content=output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                    'attachment; filename="activity-log.csv"',
            },
        )

    async def clear_activity_log(self) -> dict[str, int]:
        """Clear activity log."""
        cleared = len(self.context.STATE["activity_log"])
        self.context.STATE["activity_log"] = []

        await self.context.changed()

        return {"cleared": cleared}
