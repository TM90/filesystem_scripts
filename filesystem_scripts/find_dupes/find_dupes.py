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
    path: Path, exclude: Path | None = None
) -> dict[str, list[Path]]:
    if exclude:
        result = subprocess.check_output(
            f"find {str(path)} -type f -not -path {str(exclude)} | xargs -d '\n' sha256sum",
            shell=True,
        )
    else:
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
    file_path_dataset_a: Path, file_path_dataset_b: Path
) -> None:
    print("running with insertion_folder")
    filelist = create_checksum_filelist(
        file_path_dataset_a,
    )
    reduced_list = {key: value for key, value in filelist.items() if len(value) > 1}

    for checksum, files in reduced_list.items():
        matches = len(
            [file for file in files if str(file).startswith(str(file_path_dataset_b))]
        )
        if matches > 0:
            print(f"{checksum}:")
            for file in files:
                print(f"- {str(file)}")


if __name__ == "__main__":
    parser = ArgumentParser(description="list duplicated files")
    _ = parser.add_argument(
        "filepath",
        type=Path,
        help="dataset A in which to search for duplicates",
    )
    _ = parser.add_argument(
        "-I",
        "--insertion_folder",
        type=Path,
        required=False,
        help="data_set_b which should be inserted in dataset A",
    )
    _ = parser.add_argument(
        "-D",
        "--delete",
        help="in insertion mode delete duplicates in data_set_b",
    )
    args = parser.parse_args()
    if not args.insertion_folder:
        fp = StringIO()
        find_dupes(args.filepath, fp)
        sys.exit(0)
    else:
        find_set_b_files_already_in_set_a(args.filepath, args.insertion_folder)
        sys.exit(0)
