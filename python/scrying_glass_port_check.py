"""Check before start-up that the Admin, Client Display and Statblock ports can be opened."""
import errno
import socket

REASONS = {
    errno.EADDRINUSE: "is already in use",
    errno.EACCES: "needs extra permissions (ports below 1024 usually do)",
    errno.EADDRNOTAVAIL: "cannot be opened: the bind address is not on this machine",
}


DUPLICATE = "is configured for more than one listener"
INVALID = "is not a port number from 1 to 65535"


def port_problems(bind, ports):
    """Return (label, port, reason) for every port that is invalid, shared or cannot be opened on `bind`."""
    problems, seen = [], {}
    for label, port in ports:
        if type(port) is not int or not 1 <= port <= 65535:
            problems.append((label, port, INVALID))
            continue
        if port in seen:
            problems.append((label, port, f"{DUPLICATE} ({seen[port]} and {label})"))
            continue
        seen[port] = label
    if problems:
        return problems
    for label, port in ports:
        try:
            with socket.create_server((bind, port)):
                pass
        except OSError as exc:
            problems.append((label, port, REASONS.get(exc.errno, f"cannot be opened ({exc.strerror or exc})")))
    return problems


def port_message(bind, problems):
    """One plain message for the console; no traceback."""
    lines = [f"Scrying Glass cannot start on {bind}:"]
    lines += [f"  - port {port} ({label}) {reason}" for label, port, reason in problems]
    if any(reason == REASONS[errno.EADDRINUSE] for _, _, reason in problems):
        lines.append("Scrying Glass (or another program) may already be running. Stop it first, or choose other "
                     "ports with --admin-port, --client-port and --statblock-port or network.admin_port/client_port/"
                     "statblock_port in the config file.")
    if any(reason == INVALID or reason.startswith(DUPLICATE) for _, _, reason in problems):
        lines.append("Give each listener its own port with --admin-port, --client-port and --statblock-port or "
                     "network.admin_port/client_port/statblock_port in the config file.")
    return "\n".join(lines)
