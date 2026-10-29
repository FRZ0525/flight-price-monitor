"""从命令行参数生成 config.yaml（供 GitHub Actions 使用）。"""
import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-code", required=True)
    ap.add_argument("--from-name", required=True)
    ap.add_argument("--to-code", required=True)
    ap.add_argument("--to-name", required=True)
    ap.add_argument("--dates", required=True)
    ap.add_argument("--return-dates", default="")
    ap.add_argument("--platforms", default="fliggy,tuniu,qunar,tongcheng")
    ap.add_argument("--threshold", type=int, default=0)
    ap.add_argument("--serverchan-key", default="")
    ap.add_argument("--output", default="config.yaml")
    args = ap.parse_args()

    # Fork defaults: Hangzhou ↔ Guangzhou, Dec 2026, ¥300 alert
    # (GitHub Actions schedule falls back to upstream placeholders; remap them here.)
    if args.from_code == "LZO" and args.to_code == "BJS":
        args.from_code, args.from_name = "HGH", "杭州"
        args.to_code, args.to_name = "CAN", "广州"
        if args.dates.startswith("2026-09-30"):
            args.dates = "2026-12-11,2026-12-12"
        if args.return_dates.strip() in ("", "2026-10-06"):
            args.return_dates = "2026-12-13,2026-12-14"
        if args.threshold == 0:
            args.threshold = 300
        if args.platforms == "fliggy,tuniu,qunar,tongcheng":
            args.platforms = "fliggy,tuniu,qunar,tongcheng,ctrip"

    depart = [d.strip() for d in args.dates.split(",") if d.strip()]
    returns = [d.strip() for d in args.return_dates.split(",") if d.strip()]
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]

    lines = ["routes:"]
    lines += [
        f"  - from: {args.from_code}",
        f"    from_name: {args.from_name}",
        f"    to: {args.to_code}",
        f"    to_name: {args.to_name}",
        "    dates:",
    ]
    lines += [f'      - "{d}"' for d in depart]
    lines.append(f"    alert_threshold: {args.threshold}")

    if returns:
        lines += [
            "",
            f"  - from: {args.to_code}",
            f"    from_name: {args.to_name}",
            f"    to: {args.from_code}",
            f"    to_name: {args.from_name}",
            "    dates:",
        ]
        lines += [f'      - "{d}"' for d in returns]
        lines.append(f"    alert_threshold: {args.threshold}")

    lines += ["", "platforms:"]
    lines += [f"  - {p}" for p in platforms]
    lines += [
        "",
        "schedule:",
        "  interval_minutes: 999",
        "  jitter_minutes: 0",
        "  run_on_start: true",
        "",
        "crawler:",
        "  headless: true",
        "  timeout_seconds: 45",
        "  delay_min: 5",
        "  delay_max: 15",
        "  fliggy_max_poll: 2",
        "  tuniu_max_poll: 3",
        '  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"',
        '  mobile_user_agent: ""',
        "  debug: false",
        "  debug_dir: debug",
        "  user_data_dir: user_data",
        "",
        "output:",
        "  db_path: data/prices.db",
        "  log_path: logs/monitor.log",
        "",
        "notifier:",
        "  push_drop_min: 30",
        "  push_rise_min: 50",
        "  serverchan:",
        f"    enabled: {'true' if args.serverchan_key else 'false'}",
        f'    send_key: "{args.serverchan_key}"',
        '    channel: ""',
        "",
    ]

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"config written to {args.output}")


if __name__ == "__main__":
    main()
