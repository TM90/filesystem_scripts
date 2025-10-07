from argparse import ArgumentParser
from io import StringIO
from pathlib import Path
import sys
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


def create_checksum_filelist(
    path: Path,
) -> dict[str, list[Path]]:
    result = subprocess.check_output(
        f"find {str(path)} -type f | xargs -d '\n' sha256sum",
        shell=True,
    )
    return parse_to_dict(result.decode("utf-8"))


def find_dupes(path: Path, _result_page: StringIO) -> None:
    filelist = create_checksum_filelist(path)
    reduced_list = {key: value for key, value in filelist.items() if len(value) > 1}
    for checksum, files in reduced_list.items():
        print(f"{checksum}:")
        for file in files:
            print(f"\t - {file}")


def find_set_b_files_already_in_set_a(
    file_path_dataset_a: Path,
    file_path_dataset_b: Path,
    dry_run: bool,
) -> None:
    filelist = create_checksum_filelist(
        file_path_dataset_a,
    )
    reduced_list = {key: value for key, value in filelist.items() if len(value) > 1}

    for checksum, files in reduced_list.items():
        matches = len(
            [file for file in files if str(file).startswith(str(file_path_dataset_b))]
        )
        if matches > 0 and matches != len(files):
            print(f"{checksum}:")
            for file in files:
                if str(file).startswith(str(file_path_dataset_b)):
                    print(f"deleting {str(file)}")
                    if not dry_run:
                        file.unlink()
                print(f"- {str(file)}")


if __name__ == "__main__":
    parser = ArgumentParser(description="list duplicated files")
    _ = parser.add_argument(
        "filepath",
        type=Path,
        help="dataset A in which to search for duplicates",
    )
    _ = parser.add_argument(
        "-D",
        "--delete_duplicates_in",
        type=Path,
        required=False,
        help="folder to delete duplicates which are within filepath in ...",
    )
    _ = parser.add_argument(
        "-dry",
        "--dry-run",
        help="dry-run only report filesystem changes...",
        action="store_true",
    )
    args = parser.parse_args()
    dry_run = False
    if args.dry_run:
        dry_run = True

    if not args.delete_duplicates_in:
        fp = StringIO()
        find_dupes(args.filepath, fp)
        sys.exit(0)
    else:
        find_set_b_files_already_in_set_a(
            args.filepath,
            args.delete_duplicates_in,
            dry_run,
        )
        sys.exit(0)
