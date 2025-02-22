import os
import re
import xml.etree.ElementTree as ET


def sanitize_filename(title: str, replacement=" ") -> str:
	"""
	Sanitizes the given title to create a valid filename by removing or replacing
	any characters that are not allowed in file names.

	Parameters:
	title (str): The title string to be sanitized.
	replacement (str): The string to replace invalid characters with (default is a space).

	Returns:
	str: The sanitized title, safe to be used as a filename.
	"""
	# Remove or replace any invalid characters for file names (e.g., /, \, *, ?, :, ", <, >, |)
	return re.sub(r'[\\/*?:"<>|]', replacement, title)


def extract_pages_from_wikidump(path: str, output_dir: str = ".", n_pages: int = None, start: int = 0, skip_redirects: bool = True, verbose: bool = False) -> int:
	"""
	Extracts pages from a Wikipedia dump (in XML format), processes them, and writes the text
	of each page to a separate file named after the page title.

	Parameters:
	path (str): Path to the Wikipedia XML dump file.
	output_dir (str): Directory where the extracted pages should be saved (default is current directory).
	n_pages (int): Maximum number of pages to process (optional, default is to process all pages).
	start (int): The page number to start processing from (default is 0).
	skip_redirects (bool): If True, redirects (pages that point to another page) will be skipped (default is True).
	verbose (bool): If True, additional information will be printed during processing (default is False).

	Returns:
	page_idx (int): The index of the last processed page.
	"""
	# Create the output directory if it doesn't exist
	os.makedirs(output_dir, exist_ok=True)

	page_idx = -1  # Track the current page number
	n_skipped_pages = 0  # Track the number of skipped pages due to redirects

	# Iterate over the elements in the XML file
	for event, elem in ET.iterparse(path, events=("end",)):
		if elem.tag.endswith("page"):  # Process the 'page' elements

			page_idx += 1

			if page_idx < start:  # Skip pages before the 'start' page
				continue

			# Find the title, revision, and text elements
			title_elem = elem.find("{*}title")
			revision_elem = elem.find("{*}revision")
			text_elem = revision_elem.find("{*}text") if revision_elem is not None else None

			# Skip pages that are redirects, if required
			if skip_redirects and elem.find("{*}redirect") is not None:
				if verbose:
					print(f'[*] Skipping page number {page_idx}, title: "{title_elem.text}" due to redirect')
				n_skipped_pages += 1
				continue

			# Proceed if the title and text elements are present
			if title_elem is not None and text_elem is not None:
				# Sanitize the title to create a valid file name
				file_path = os.path.join(output_dir, sanitize_filename(title_elem.text) + ".txt")
				if verbose:
					print(f'[*] Writing page number {page_idx}, title: "{title_elem.text}" to {file_path}...')

				# Write the text content of the page to a file
				with open(file_path, "w+", encoding="utf-8") as f:
					f.write(text_elem.text)

		# Stop processing if the maximum number of pages has been reached
		if n_pages is not None and page_idx - start >= n_pages + n_skipped_pages:
			break

	# Print summary if verbose mode is enabled
	if verbose:
		print('\n' + '-' * 25 + "Summery" + '-' * 25)
		print(f'[*] Finished processing {page_idx - start} pages')
		print(f'[*] Started at page {start}')
		print(f'[*] Wrote {page_idx - start - n_skipped_pages} pages')
		print(f'[*] Skipped {n_skipped_pages} pages')

	return page_idx


if __name__ == "__main__":
	path = "hewiki-latest-pages-articles.xml"
	extract_pages_from_wikidump(path, "../data", n_pages=10, start=100, verbose=True)
