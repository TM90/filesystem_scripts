from argparse import ArgumentParser
from io import StringIO
from pathlib import Path
import subprocess


def parse_to_dict(raw: str) -> dict[str, list[Path]]:
    raw_list = raw.split("\n")
    sha_list = [element.split("  ", 1) for element in raw_list]
    result_dict: dict[str, list[Path]] = {}
    for checksum, filepath in sha_list[:-1]:
        if checksum not in result_dict.keys():
            result_dict[checksum] = [Path(filepath)]
        else:
            result_dict[checksum].append(Path(filepath))
    return result_dict


def create_checksum_filelist(path: Path) -> dict[str, list[Path]]:
    result = subprocess.check_output(
        f"find {str(path)} -type f | xargs -d '\n' sha256sum", shell=True
    )
    return parse_to_dict(result.decode("utf-8"))


def find_dupes(path: Path, _result_page: StringIO) -> None:
    filelist = create_checksum_filelist(path)
    reduced_list = {key: value for key, value in filelist.items() if len(value) > 1}
    for checksum, files in reduced_list.items():
        print(f"{checksum}:")
        for file in files:
            print(f"\t - {file}")


if __name__ == "__main__":
    parser = ArgumentParser(prog="find_dupes", description="list duplicated files")
    _ = parser.add_argument("filepath")
    args = parser.parse_args()
    fp = StringIO()
    find_dupes(Path(Path(args.filepath)), fp)
