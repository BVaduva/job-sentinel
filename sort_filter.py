def clean_and_sort_filter_file(filename="files/words_to_filter.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            words = [line.strip().lower() for line in file if line.strip()]

        unique_sorted_words = sorted(list(set(words)))

        with open(filename, "w", encoding="utf-8") as file:
            for word in unique_sorted_words:
                file.write(f"{word}\n")

        print(f"Done! {len(unique_sorted_words)} unique words sorted alphabetically.")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

if __name__ == "__main__":
    clean_and_sort_filter_file()