import zipfile
import os

def extract_zip_files(zip_path, extract_to, csv_list_file):
    """
    Recursively extracts nested zip files and stores the paths of CSV files in a text file.
    """
    try:
        zip_name = os.path.splitext(os.path.basename(zip_path))[0]
        unique_extract_to = os.path.join(extract_to, zip_name)

        if os.path.exists(unique_extract_to):
            print(f"Skipping extraction: {zip_path} already extracted to {unique_extract_to}")
        else:
            os.makedirs(unique_extract_to, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(unique_extract_to)
                print(f"Extracted: {zip_path} to {unique_extract_to}")

        csv_files = []
        for root, _, files in os.walk(unique_extract_to):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.zip'):
                    print(f"Found nested zip: {file_path}")
                    extract_zip_files(file_path, root, csv_list_file)
                elif file.endswith('.csv'):
                    csv_files.append(file_path)

        # Append extracted CSV file paths to a text file
        with open(csv_list_file, 'a') as f:
            for csv_file in csv_files:
                f.write(csv_file + '/n')

    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid zip file.")
    except Exception as e:
        print(f"Error processing {zip_path}: {e}")

def main():
    initial_zip_path = 'C:/Users/Vaibhav/Downloads/ticks_datas.zip'
    extract_to = 'D:/Project/Company Assignment/true_beacon/project/extractor'
    csv_list_file = 'csv_files.txt'

    # Ensure the CSV list file is cleared before writing new entries
    open(csv_list_file, 'w').close()

    extract_zip_files(initial_zip_path, extract_to, csv_list_file)

if __name__ == "__main__":
    main()
