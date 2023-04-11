import argparse
import gzip
import hashlib
import os
import platform
import tarfile
from pathlib import Path
import sys
from typing import Tuple, Dict, Any

import requests
from pre_commit.store import Store
import subprocess

def get_checksum(s: str) -> str:
    sha = hashlib.sha256()
    sha.update(s.encode('utf-8'))
    return sha.hexdigest()


def get_client_info() -> str:
    return f"{platform.system().lower()}-{platform.machine()}"


def parse() -> tuple[dict[Any, Any], dict[Any, Any], Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='list of configuration parameters', type=str, default={})
    parser.add_argument('files', nargs='*')

    # Parse the arguments
    args, binary_args = parser.parse_known_args()

    # Collect all arguments with -- prefix into a dictionary
    config = {}
    for item in args.config.split(','):
        k, v = item.split('=')
        config[k] = v

    # Collect all binary args into a list
    kwargs = {}
    for arg in binary_args:
        if arg.startswith('--'):
            k, v = arg.split('=')
            kwargs[k[2:]] = v

    # Return the list of files and the dictionary of binary args
    return config, kwargs, args.files


def main() -> None:
    # Get platform and arch
    client_info = get_client_info()

    # Parse args
    config, kwargs, files = parse()

    # Get URL from config
    if not (url := config.get(client_info)):
        raise KeyError(f"'{client_info}' missing from .pre-commit-config.yaml")

    # Compute the SHA-1 checksum of the URL
    checksum = get_checksum(url)

    dir = Path(f"{Store.get_default_directory()}/pre-commit-binaries")

    if not dir.exists():
        print(f"Creating binary cache directory {dir}")
        dir.mkdir()

    cache_path = Path(f"{Store.get_default_directory()}/pre-commit-binaries/{client_info}-{checksum}")

    print(cache_path)

    if not cache_path.exists():
        print(f"Downloading binary for {client_info}")
        cache_path.mkdir()
        response = requests.get(url)
        response.raise_for_status()
        with tarfile.open(fileobj=response.raw, mode="r") as tar:
            tar.extractall(cache_path)
        files = os.listdir(cache_path)
        assert len(files) == 1
        file = files[0]

        binary_commands = []
        for k, v in kwargs.items():
            binary_commands.append(f"--{k}={v}")
        binary_commands += files

        temp = [str(cache_path / file)] + binary_commands
        print(f'{temp=}')
        proc = subprocess.Popen(temp, stdout=subprocess.PIPE, universal_newlines=True)
        for line in proc.stdout:
            print(line, end="")


main()
