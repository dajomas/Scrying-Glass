"""Check before start-up that the Admin and Client Display ports can be opened."""
import errno
import socket

REASONS = {
    errno.EADDRINUSE: "is already in use",
    errno.EACCES: "needs extra permissions (ports below 1024 usually do)",
    errno.EADDRNOTAVAIL: "cannot be opened: the bind address is not on this machine",
}


def port_problems(bind, ports):
    """Return (label, port, reason) for every port that cannot be opened on `bind`."""
    problems = []
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
                     "ports with --admin-port and --client-port or network.admin_port/client_port in the config file.")
    return "\n".join(lines)
