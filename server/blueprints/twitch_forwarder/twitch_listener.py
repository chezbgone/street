from typing import Callable

import re
import socket

from common.models import TwitchMessage

class TwitchChatListener:
    TWITCH_IRC_ADDRESS = ("irc.chat.twitch.tv", 6667)
    MESSAGE_PATTERN = re.compile(rb'@(.+?(?=\s+:)).*PRIVMSG[^:]*:([^\r\n]*)')

    def __init__(self, channel: str, message_timeout: float = 1.0) -> None:
        self._socket = socket.socket()
        self._socket.connect(self.TWITCH_IRC_ADDRESS)
        self._send_raw('CAP REQ :twitch.tv/tags')
        self._send_raw('PASS :oauth:')
        # 'justinfan[numbers]' creates an anonymous connection
        self._send_raw('NICK justinfan5')

        self._socket.settimeout(message_timeout)

        self._channel = channel

    def _send_raw(self, msg: str) -> None:
        self._socket.send(f"{msg}\r\n".encode())

    def _recv_all(self, buffer_size: int = 4096) -> bytes:
        data = bytearray()
        while True:
            part = self._socket.recv(buffer_size)
            data.extend(part)
            if len(part) < buffer_size:
                break
        return data

    def listen(
        self,
        on_message: Callable[[TwitchMessage], object],
        timeout: float | None = None,
        buffer_size: int = 4096
    ) -> None:
        self._send_raw(f"JOIN #{self._channel}")

        def parse_match(match: re.Match[bytes]) -> TwitchMessage:
            metadata: dict[str, str] = {}
            for item in match.group(1).split(b';'):
                k, v = item.split(b'=',1)
                metadata[k.decode()] = v.decode()
            if 'display-name' not in metadata:
                raise ValueError('could not find display-name in twitch message')
            user = metadata['display-name']
            del metadata['display-name']
            return TwitchMessage(metadata, user, match.group(2).decode())

        time_since_last_message = 0.0
        unprocessed = bytearray()
        try:
            while True:
                try:
                    block = self._recv_all(buffer_size)
                    unprocessed.extend(block)
                    if b'PING :tmi.twitch.tv' in unprocessed:
                        self._send_raw('PONG :tmi.twitch.tv')

                    matches = list(self.MESSAGE_PATTERN.finditer(unprocessed))
                    if len(matches) == 0:
                        continue
                    time_since_last_message = 0
                    if len(matches) > 1:
                        matches = matches[:-1] # assume last match is incomplete

                    assert(len(matches) > 0)
                    _, last_processed_byte_index = matches[-1].span()
                    unprocessed = unprocessed[last_processed_byte_index:]

                    for match in matches:
                        msg = parse_match(match)
                        on_message(msg)
                except socket.timeout as e:
                    if timeout is not None:
                        time_since_last_message += timeout
                        if time_since_last_message >= timeout:
                            print("socket timed out after {timeout} seconds")
                            break
        except KeyboardInterrupt:
            print("Interrupted by user.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise e

if __name__ == "__main__":
    def print_to_string(msg: TwitchMessage):
        print(f'{msg.display_name}: {msg.content}')
    channel = '5treettv'
    print(f'listening to {channel} twitch chat')
    client = TwitchChatListener(channel)
    client.listen(on_message=print_to_string)
