import os
import time
from datetime import datetime

import psutil
from colorama import Fore, Style, init

init(autoreset=True)


class AnonProcessManager:
    REFRESH_DELAY = 2
    MAX_PROCESSES = 25

    PROCESS_STATES = {
        "running": "RUNNING",
        "sleeping": "WAITING",
        "disk-sleep": "WAITING",
        "idle": "WAITING",
        "stopped": "READ",
        "zombie": "ZOMBIE",
        "dead": "TERMINATING",
    }

    STATE_COLORS = {
        "RUNNING": Fore.GREEN,
        "WAITING": Fore.CYAN,
        "READ": Fore.YELLOW,
        "TERMINATING": Fore.RED,
        "ZOMBIE": Fore.MAGENTA,
        "DAEMON": Fore.BLUE,
    }

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def classify_process(self, process_name, status):
        state = self.PROCESS_STATES.get(status.lower(), "WAITING")

        # daemon detection
        if process_name.endswith("d"):
            return "DAEMON"

        return state

    def cpu_color(self, value):
        if value >= 70:
            return Fore.RED
        elif value >= 30:
            return Fore.YELLOW
        return Fore.GREEN

    def memory_color(self, value):
        if value >= 20:
            return Fore.RED
        elif value >= 10:
            return Fore.YELLOW
        return Fore.CYAN

    def collect_processes(self):
        result = []

        for process in psutil.process_iter([
            "pid",
            "name",
            "username",
            "status",
            "cpu_percent",
            "memory_percent"
        ]):
            try:
                info = process.info

                name = info.get("name") or "unknown"
                status = info.get("status") or "unknown"

                state = self.classify_process(name, status)

                result.append({
                    "pid": info.get("pid", 0),
                    "user": info.get("username") or "system",
                    "name": name,
                    "state": state,
                    "cpu": info.get("cpu_percent") or 0.0,
                    "memory": info.get("memory_percent") or 0.0,
                })

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess
            ):
                continue

        result.sort(key=lambda p: p["cpu"], reverse=True)

        return result[:self.MAX_PROCESSES]

    def print_header(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_cpu = psutil.cpu_percent(interval=None)
        total_memory = psutil.virtual_memory()

        print(Fore.CYAN + Style.BRIGHT + "=" * 110)

        print(
            Fore.CYAN + Style.BRIGHT +
            f"  AnonProcessManager   "
            f"Time: {now}   "
            f"CPU: {total_cpu:5.1f}%   "
            f"RAM: {total_memory.percent:5.1f}%"
        )

        print(Fore.CYAN + Style.BRIGHT + "=" * 110)

        print(
            Style.BRIGHT +
            f"{'PID':<8}"
            f"{'USER':<18}"
            f"{'PROCESS':<30}"
            f"{'STATE':<16}"
            f"{'CPU':>10}"
            f"{'RAM':>10}"
        )

        print("-" * 110)

    def print_processes(self, processes):
        for proc in processes:
            state_color = self.STATE_COLORS.get(
                proc["state"],
                Fore.WHITE
            )

            cpu_color = self.cpu_color(proc["cpu"])
            mem_color = self.memory_color(proc["memory"])

            print(
                f"{Fore.MAGENTA}{str(proc['pid']):<8}"
                f"{Fore.BLUE}{proc['user'][:17]:<18}"
                f"{Fore.WHITE}{proc['name'][:29]:<30}"
                f"{state_color}{proc['state']:<16}"
                f"{cpu_color}{proc['cpu']:>8.1f}%  "
                f"{mem_color}{proc['memory']:>8.1f}%"
            )

    def initialize_cpu_counters(self):
        print(Fore.YELLOW + "Initializing process counters...\n")

        for process in psutil.process_iter():
            try:
                process.cpu_percent(interval=None)
            except Exception:
                pass

        psutil.cpu_percent(interval=None)
        time.sleep(0.5)

    def run(self):
        self.initialize_cpu_counters()

        while True:
            try:
                self.clear_screen()

                self.print_header()

                processes = self.collect_processes()

                self.print_processes(processes)

                print(
                    "\n" +
                    Fore.WHITE +
                    Style.DIM +
                    f"refresh interval: {self.REFRESH_DELAY}s | Ctrl+C to exit"
                )

                time.sleep(self.REFRESH_DELAY)

            except KeyboardInterrupt:
                print(Fore.RED + "\nmonitor terminated.")
                break


if __name__ == "__main__":
    manager = AnonProcessManager()
    manager.run()
