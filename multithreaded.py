import os
import re
from threading import Thread, RLock
from queue import Queue
from time import time


def search_files(file_queue, search_words, result_dict, lock):
    while not file_queue.empty():
        file_path = file_queue.get()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                for word in search_words:
                    if re.search(word, content, re.IGNORECASE):
                        with lock:
                            if file_path not in result_dict[word]:
                                result_dict[word].append(file_path)
        except Exception as e:
            print(f"Error processing file: {file_path}. Error: {e}")
        file_queue.task_done()


def main(directory, search_words, num_threads):
    start_time = time()
    file_queue = Queue()
    result_dict = {word: [] for word in search_words}
    lock = RLock()

    # Collect file paths from the given directory
    file_paths = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.txt')]
    for file_path in file_paths:
        file_queue.put(file_path)

    # Collect file paths from subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.txt'):
                file_queue.put(file_path)

    # Start threads
    threads = []
    for _ in range(num_threads):
        thread = Thread(target=search_files, args=(file_queue, search_words, result_dict, lock))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    file_queue.join()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    end_time = time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    return result_dict


if __name__ == "__main__":
    directory = "files"
    search_words = ["import", "from", "bla-bla-bla"]
    num_threads = 4
    result = main(directory, search_words, num_threads)
    print(result)
