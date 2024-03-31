add  python3.12 newdetectAndSimil.py /home/mukesh/code/ 5

-> where window size ranges from 5 to 20
With these modifications, the code should now be able to handle additional file formats such as .doc, .docx, .rtf, .html, .htm, and .odt, .txt and .pdf alongside.
-> Note for file modified and created.

Introduction to Rolling Hashing:

Rolling hashing is a technique used to break down strings into smaller, fixed-size chunks.
It involves updating hash values incrementally, making it efficient for comparing overlapping segments within strings.
Basic Concept:

Break the input string into smaller chunks or windows of fixed length.
Compute the hash value of the first chunk.
Incremental Update:

To move to the next window, instead of recalculating the hash from scratch, update the hash value based on the previous window.
This update is done in constant time, making it highly efficient.
Usage:

String Matching: Rolling hashing enables efficient substring matching in large texts or documents.
Plagiarism Detection: It helps in identifying similar sections of texts efficiently.
Data Deduplication: Rolling hashing optimizes storage by identifying duplicate chunks of data.
Advantages:

Speed: Rolling hashing allows for fast comparison of overlapping segments.
Efficiency: It reduces the computational overhead compared to recalculating hash values for each segment.
Storage Optimization: By identifying duplicate segments, it aids in reducing storage space in deduplication tasks.
Challenges:

Hash Collisions: Like any hashing technique, rolling hashing may encounter collisions, where different input strings produce the same hash value.
Window Size: Choosing an optimal window size is crucial for balancing speed and accuracy in applications.
Conclusion:

Rolling hashing offers a powerful tool for efficient string processing tasks.
Its incremental update mechanism makes it particularly useful for large-scale applications such as data deduplication and plagiarism detection.

Plain Text (.txt): A simple text format with no formatting or metadata, often used for storing raw text data.

Portable Document Format (.pdf): Widely used for documents that need to be shared or printed while preserving formatting across different platforms.

Microsoft Word Document (.doc, .docx): Standard formats for word processing documents created using Microsoft Word or compatible software.

Rich Text Format (.rtf): A format that supports basic text formatting, such as bold, italics, and font styles, and is compatible with many word processing applications.

Hypertext Markup Language (.html, .htm): Used for creating web pages and documents with formatted text, images, links, and other multimedia content.

Markdown (.md): A lightweight markup language with plain-text formatting syntax, often used for writing documentation, README files, and technical documentation.

Comma-Separated Values (.csv): A plain text format used for tabular data where each line represents a row and columns are separated by commas.

JavaScript Object Notation (.json): A lightweight data-interchange format used for transmitting data between a server and a web application, or between different parts of an application.

Extensible Markup Language (.xml): A markup language that defines a set of rules for encoding documents in a format that is both human-readable and machine-readable.