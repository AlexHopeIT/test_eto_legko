import argparse
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT = 30


def download(url: str) -> tuple[int, float]:
    """Скачивает ответ полностью и возвращает объём в байтах и время в секундах"""
    request = Request(
        url,
        headers={
            "User-Agent": "DownloadSpeedTest/1.0",
            "Accept-Encoding": "identity",
        },
    )

    downloaded_bytes = 0
    started_at = time.perf_counter()

    with urlopen(request, timeout=TIMEOUT) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break

            downloaded_bytes += len(chunk)

    elapsed = time.perf_counter() - started_at
    return downloaded_bytes, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Измеряет скорость скачивания по результатам 10-ти запросов."
    )
    parser.add_argument("url", help="HTTP- или HTTPS-адрес файла")
    args = parser.parse_args()

    if not args.url.lower().startswith(("http://", "https://")):
        parser.error("Адрес должен начинаться с http:// или https://")

    total_bytes = 0
    total_time = 0.0

    for number in range(1, REQUEST_COUNT + 1):
        try:
            downloaded_bytes, elapsed = download(args.url)
        except (URLError, OSError, ValueError) as error:
            print(
                f"Ошибка запроса {number}/{REQUEST_COUNT}: {error}",
                file=sys.stderr,
            )
            return 1

        total_bytes += downloaded_bytes
        total_time += elapsed

        print(
            f"[{number}/{REQUEST_COUNT}] "
            f"Скачано: {downloaded_bytes} байт; время: {elapsed:.3f} с"
        )

    average_time = total_time / REQUEST_COUNT
    speed_mib_s = total_bytes / total_time / (1024 ** 2)

    print("\nРезультат:")
    print(f"Среднее время запроса: {average_time:.3f} с")
    print(f"Общий объём: {total_bytes} байт")
    print(f"Скорость скачивания: {speed_mib_s:.3f} МиБ/с")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nИзмерение прервано пользователем.", file=sys.stderr)
        sys.exit(130)
