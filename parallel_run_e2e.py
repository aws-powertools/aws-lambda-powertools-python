""" Calculate how many parallel workers are needed to complete E2E infrastructure jobs across available CPU Cores """
import subprocess
from pathlib import Path


def main():
    features = Path("tests/e2e").rglob("infrastructure.py")
    workers = len(list(features)) - 2  # NOTE: Return to 1 once Lambda Layer infra is removed

    command = f"poetry run pytest -n {workers} --dist loadfile -o log_cli=true tests/e2e"
    print(f"Running E2E tests with: {command}")
    subprocess.run(command.split(), shell=False)


if __name__ == "__main__":
    main()
