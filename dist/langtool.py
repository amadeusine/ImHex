from pathlib import Path
import sys
import json

DEFAULT_LANG = "en_US"


def handle_missing_key(command, lang_data, key, value):
    if command == "check":
        print(f"Error: Translation {lang_data['code']} is missing translation for key '{key}'")
        exit(2)
    elif command == "translate":
        print(f"Key \033[1m'{key}': '{value}'\033[0m is missing in translation '{lang_data['code']}'")
        new_value = input("Enter translation: ")
        lang_data["translations"][key] = new_value
    elif command == "update":
        lang_data["translations"][key] = "***** MISSING TRANSLATION *****"


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {Path(sys.argv[0]).name} <check|translate|update> <lang folder path> <language>")
        return 1

    command = sys.argv[1]
    if command not in ["check", "translate", "update"]:
        print(f"Unknown command: {command}")
        return 1

    print(f"Using langtool in {command} mode")

    lang_folder_path = Path(sys.argv[2])
    if not lang_folder_path.exists():
        print(f"Error: {lang_folder_path} does not exist")
        return 1

    if not lang_folder_path.is_dir():
        print(f"Error: {lang_folder_path} is not a folder")
        return 1

    lang = sys.argv[3] if len(sys.argv) > 3 else ""

    print(f"Processing language files in {lang_folder_path}...")

    default_lang_file_path = lang_folder_path / Path(DEFAULT_LANG + ".json")
    if not default_lang_file_path.exists():
        print(f"Error: Default language file {default_lang_file_path} does not exist")
        return 1

    print(f"Using file '{default_lang_file_path.name}' as template language file")

    with default_lang_file_path.open("r", encoding="utf-8") as default_lang_file:
        default_lang_data = json.load(default_lang_file)

        for additional_lang_file_path in lang_folder_path.glob("*.json"):
            if not lang == "" and not additional_lang_file_path.stem == lang:
                continue

            if additional_lang_file_path.name.startswith(DEFAULT_LANG):
                continue

            print(f"\nProcessing file '{additional_lang_file_path.name}'\n----------------------------\n")

            with additional_lang_file_path.open("r+", encoding="utf-8") as additional_lang_file:
                additional_lang_data = json.load(additional_lang_file)

                for key, value in default_lang_data["translations"].items():
                    if key not in additional_lang_data["translations"]:
                        handle_missing_key(command, additional_lang_data, key, value)

                keys_to_remove = []
                for key, value in additional_lang_data["translations"].items():
                    if key not in default_lang_data["translations"]:
                        keys_to_remove.append(key)

                for key in keys_to_remove:
                    additional_lang_data["translations"].pop(key)
                    print(f"Removed unused key '{key}' from translation '{additional_lang_data['code']}'")

                additional_lang_file.seek(0)
                additional_lang_file.truncate()
                json.dump(additional_lang_data, additional_lang_file, indent=4, sort_keys=True, ensure_ascii=False)


if __name__ == '__main__':
    exit(main())
