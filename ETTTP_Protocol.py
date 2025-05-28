import re
from ipaddress import ip_address

__all__ = ["ETTTPProtocol", "ETTTPError"]


class ETTTPError(RuntimeError):
    """Raised when a protocol-level violation is detected."""


class ETTTPProtocol:
    _VERSION = "ETTTP/1.0"
    _CRLF = "\r\n"
    _EMPTY_LINE = _CRLF

    def __init__(self, my_ip: str, peer_ip: str) -> None:

        self.my_ip = str(ip_address(my_ip))
        self.peer_ip = str(ip_address(peer_ip))

    def create_send_first_move(self, first_move: str) -> str:

        if first_move not in ("ME", "YOU"):
            raise ETTTPError("First-Move must be 'ME' or 'YOU'")
        body = f"First-Move: {first_move}"
        return self._build("SEND", body)

    def create_send_move(self, row: int, col: int) -> str:
        if not (0 <= row <= 2 and 0 <= col <= 2):
            raise ETTTPError("row/col must be in range 0-2")
        body = f"New-Move: ({row},{col})"
        return self._build("SEND", body)

    def create_ack(self, original_method: str, body: str) -> str:

        if original_method != "SEND":
            raise ETTTPError("ACK can currently reply only to SEND")
        return self._build("ACK", body)

    def create_result(self, winner: str) -> str:
        if winner not in ("ME", "YOU", "DRAW"):
            raise ETTTPError("Winner must be 'ME' | 'YOU' | 'DRAW'")
        body = f"Winner: {winner}"
        return self._build("RESULT", body)


    def parse_message(self, raw: str) -> tuple[str, dict]:

        if not raw.endswith(self._EMPTY_LINE):
            raise ETTTPError("Message must end with CRLF-CRLF")

        lines = raw.strip().split(self._CRLF)
        if len(lines) < 2:
            raise ETTTPError("Not enough header lines")

        first_tokens = lines[0].split()
        if len(first_tokens) != 2:
            raise ETTTPError("Malformed first line")
        method, version = first_tokens
        if version != self._VERSION:
            raise ETTTPError("Unsupported protocol version")


        fields: dict[str, str] = {}
        for ln in lines[1:]:
            if not ln:
                continue  
            try:
                key, val = ln.split(":", 1)
            except ValueError:
                raise ETTTPError(f"Bad header line: {ln}")
            fields[key.strip()] = val.strip()


        host = fields.get("Host")
        if host is None or host not in (self.my_ip, self.peer_ip):
            raise ETTTPError("Host field missing or invalid")

        return method, fields


    def check_format(self, raw: str, expected_type: str | None = None) -> bool:

        try:
            method, _ = self.parse_message(raw)
        except ETTTPError:
            return False
        return expected_type is None or method == expected_type


    def _build(self, method: str, body_line: str) -> str:

        hdr = (
            f"{method} {self._VERSION}{self._CRLF}"
            f"Host: {self.peer_ip}{self._CRLF}"
            f"{body_line}{self._CRLF}"
            f"{self._CRLF}"  
        )
        return hdr
