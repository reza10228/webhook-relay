def format_alerts(data):
    """
    Advanced formatter for:
    - Alertmanager payloads
    - Simple text payloads
    - Login alerts
    - Zulip
    - Mattermost

    Features:
    - Dynamic labels
    - Smart filtering
    - Better markdown rendering
    - Multi-alert handling
    - Runbook/dashboard support
    - Safe fallback handling
    """

    #
    # HELPERS
    #
    def valid(value):
        """
        Check if a value is meaningful.
        """

        invalid_values = {
            "",
            "-",
            "unknown",
            "unknown-instance",
            "unknown-node",
            "no-name",
            "no-summary",
            "no-description",
            "None",
            None
        }

        return value not in invalid_values

    def add_field(message, title, value, code=True):
        """
        Append field only if value is valid.
        """

        if valid(value):

            if code:
                message.append(f"- **{title}:** `{value}`")
            else:
                message.append(f"- **{title}:** {value}")

    #
    # SIMPLE PAYLOAD
    #
    if isinstance(data, dict) and "text" in data:

        text = data.get("text", "")

        return f"""
ℹ️ Notification

{text}
""".strip()

    #
    # VALIDATE ALERTMANAGER PAYLOAD
    #
    if not isinstance(data, dict):

        return "Invalid payload format"

    alerts = data.get("alerts", [])

    if not alerts:

        return "No alerts found in payload"

    status = str(
        data.get("status", "unknown")
    ).lower()

    #
    # HEADER
    #
    message = []

    if status == "firing":
        message.append("# 🚨 ALERT FIRING")
    elif status == "resolved":
        message.append("# ✅ ALERT RESOLVED")
    else:
        message.append(f"# ℹ️ ALERT STATUS: {status.upper()}")

    message.append("")

    #
    # PROCESS ALERTS
    #
    for index, alert in enumerate(alerts, start=1):

        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        #
        # LOGIN ALERT HANDLER
        #
        alert_type = labels.get("type", "")

        if alert_type == "login":

            user = labels.get("user", "unknown-user")
            instance = labels.get("instance", "unknown-instance")

            text = annotations.get(
                "text",
                annotations.get("summary", "")
            )

            if valid(text):

                text = (
                    text
                    .replace(user, f"**{user}**")
                    .replace(instance, f"**{instance}**")
                )

            else:

                text = (
                    f"User **{user}** logged into "
                    f"server **{instance}**"
                )

            message.append("## 🔐 Login Alert")
            message.append("")
            message.append(text)
            message.append("")
            message.append("----------")
            message.append("")

            continue

        #
        # ALERT FIELDS
        #
        alertname = labels.get("alertname")
        severity = labels.get("severity", "unknown")

        severity_emoji = {
            "critical": "🔴",
            "warning": "🟡",
            "info": "🔵"
        }.get(severity.lower(), "⚪")

        #
        # SECTION TITLE
        #
        title = alertname if valid(alertname) else "UnknownAlert"

        message.append(
            f"## {severity_emoji} {title}"
        )

        message.append("")

        #
        # IMPORTANT LABELS
        #
        important_labels = [
            ("Severity", severity),
            ("Instance", labels.get("instance")),
            ("Node", labels.get("nodename")),
            ("Namespace", labels.get("namespace")),
            ("Pod", labels.get("pod")),
            ("Container", labels.get("container")),
            ("Job", labels.get("job")),
            ("Cluster", labels.get("cluster")),
            ("Team", labels.get("team")),
            ("Service", labels.get("service")),
            ("Name", labels.get("name"))
        ]

        for field_name, field_value in important_labels:

            add_field(
                message,
                field_name,
                field_value
            )

        #
        # ANNOTATIONS
        #
        summary = annotations.get("summary")
        description = annotations.get("description")

        if valid(summary):

            message.append("")
            message.append(f"📋 **Summary:** {summary}")

        if valid(description):

            message.append("")
            message.append(f"📝 **Description:** {description}")

        #
        # OPTIONAL LINKS
        #
        runbook_url = annotations.get("runbook_url")
        dashboard_url = annotations.get("dashboard")
        generator_url = alert.get("generatorURL")

        if valid(runbook_url):

            message.append("")
            message.append(
                f"📚 **Runbook:** {runbook_url}"
            )

        if valid(dashboard_url):

            message.append("")
            message.append(
                f"📊 **Dashboard:** {dashboard_url}"
            )

        if valid(generator_url):

            message.append("")
            message.append(
                f"🔍 **Source:** {generator_url}"
            )

        #
        # TIMESTAMPS
        #
        starts_at = alert.get("startsAt")
        ends_at = alert.get("endsAt")

        if valid(starts_at):

            add_field(
                message,
                "StartsAt",
                starts_at
            )

        if (
            valid(ends_at)
            and status == "resolved"
        ):

            add_field(
                message,
                "EndsAt",
                ends_at
            )

        #
        # FINGERPRINT
        #
        fingerprint = alert.get("fingerprint")

        if valid(fingerprint):

            add_field(
                message,
                "Fingerprint",
                fingerprint
            )

        #
        # MULTI ALERT SEPARATOR
        #
        if index != len(alerts):

            message.append("")
            message.append("----------")
            message.append("")

    #
    # LIMIT VERY LARGE MESSAGES
    #
    final_message = "\n".join(message)

    max_size = 14000

    if len(final_message) > max_size:

        final_message = (
            final_message[:max_size]
            + "\n\n⚠️ Message truncated due to size."
        )

    return final_message.strip()
