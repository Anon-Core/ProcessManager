import os
import time
from datetime import datetime

import psutil
from colorama import Fore, Style, init

init(autoreset=True)

REFRESH_INTERVAL = 2
TOP_N = 20


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def color_cpu(cpu: float) -> str:
    if cpu >= 70:
        return Fore.RED
    elif cpu >= 30:
        return Fore.YELLOW
    return Fore.GREEN


def color_mem(mem: float) -> str:
    if mem >= 20:
        return Fore.RED
    elif mem >= 10:
        return Fore.YELLOW
    return Fore.CYAN


def color_status(status: str) -> str:
    s = status.lower()
    if s == "running":
        return Fore.GREEN
    elif s in ("sleeping", "idle"):
        return Fore.CYAN
    elif s in ("stopped", "suspended"):
        return Fore.YELLOW
    elif s in ("zombie", "dead"):
        return Fore.RED
    return Fore.WHITE


def collect_processes():
    processes = []

    for proc in psutil.process_iter(
        ['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent']
    ):
        try:
            info = proc.info
            processes.append({
                "pid": info.get("pid", 0),
                "name": info.get("name") or "-",
                "user": info.get("username") or "-",
                "status": info.get("status") or "-",
                "cpu": info.get("cpu_percent") or 0.0,
                "mem": info.get("memory_percent") or 0.0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda x: x["cpu"], reverse=True)
    return processes[:TOP_N]


def print_header():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_cpu = psutil.cpu_percent(interval=None)
    total_mem = psutil.virtual_memory()

    print(Fore.CYAN + Style.BRIGHT + "=" * 100)
    print(
        Fore.CYAN + Style.BRIGHT +
        f" Process Monitor    Time: {now}    CPU: {total_cpu:5.1f}%    "
        f"RAM: {total_mem.percent:5.1f}%"
    )
    print(Fore.CYAN + Style.BRIGHT + "=" * 100)

    print(
        Style.BRIGHT +
        f"{'PID':<8} {'USER':<18} {'NAME':<28} {'STATUS':<14} {'CPU %':>8} {'MEM %':>8}"
    )
    print("-" * 100)


def print_processes(processes):
    for p in processes:
        cpu_c = color_cpu(p["cpu"])
        mem_c = color_mem(p["mem"])
        st_c = color_status(p["status"])

        print(
            f"{Fore.MAGENTA}{str(p['pid']):<8} "
            f"{Fore.BLUE}{p['user'][:17]:<18} "
            f"{Fore.WHITE}{p['name'][:27]:<28} "
            f"{st_c}{p['status'][:13]:<14} "
            f"{cpu_c}{p['cpu']:>7.1f}% "
            f"{mem_c}{p['mem']:>7.1f}%"
        )


def main():
    print("Initializing CPU counters...")
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except Exception:
            pass

    psutil.cpu_percent(interval=None)
    time.sleep(0.5)

    while True:
        try:
            clear()
            print_header()
            processes = collect_processes()
            print_processes(processes)
            print("\n" + Fore.BLACK + Style.DIM + f" Refresh every {REFRESH_INTERVAL}s | Ctrl+C to exit")
            time.sleep(REFRESH_INTERVAL)
        except KeyboardInterrupt:
            print(Fore.RED + "\nStopped.")
            break


if __name__ == "__main__":
    main()
