# PDF_Comparer

A Python tool for comparing two PDF documents and highlighting their differences. This tool identifies text changes, formatting differences, and generates visual output highlighting the changes.

## Features

- Compares text content between two PDF files
- Detects formatting changes (font, size, color)
- Highlights differences using color overlays
- Generates output images for pages with changes only
- Configurable similarity and position thresholds
- Command-line interface for easy integration

## Requirements

- Python 3.8 or newer
- Dependencies listed in `requirements.txt`:
  - PyMuPDF (fitz) 1.23.8
  - Pillow 10.2.0

## Installation

1. Clone the repository or download the source code:
```bash
git clone [repository-url]
cd pdf-comparer
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### System-Specific Dependencies

#### Windows
- No additional dependencies required

#### Linux
```bash
sudo apt-get update
sudo apt-get install python3-dev
sudo apt-get install libjpeg-dev
sudo apt-get install zlib1g-dev
```

#### macOS
```bash
brew install libjpeg
```

## Usage

### Basic Usage
```bash
python pdf_comparer.py original.pdf modified.pdf output_directory
```

### Advanced Usage
```bash
python pdf_comparer.py original.pdf modified.pdf output_directory --similarity 0.9 --position 3.0 --ignore-formatting
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `original_pdf` | Path to the original PDF file | Required |
| `modified_pdf` | Path to the modified PDF file | Required |
| `output_dir` | Directory to save difference images | Required |
| `--similarity` | Text similarity threshold (0.0-1.0) | 0.8 |
| `--position` | Position matching tolerance in points | 5.0 |
| `--ignore-formatting` | Ignore formatting changes | False |

### Help
```bash
python pdf_comparer.py --help
```

## Output

The tool generates:
- PNG images for pages with detected differences
- Yellow highlighting for changed text
- Red borders around changed areas
- Console output showing progress and statistics

## Example Output Directory Structure
```
output_directory/
├── page_1_differences.png
├── page_4_differences.png
└── page_7_differences.png
```
Note: Only pages with detected differences will have corresponding output files.

## Performance Considerations

- Memory Usage: 
  - Minimum: 4GB RAM
  - Recommended: 8GB+ RAM for large PDFs
- Processing Time:
  - Depends on PDF size and complexity
  - Larger PDFs may take several minutes to process

## Troubleshooting

### Common Issues

1. ModuleNotFoundError
```bash
# Verify virtual environment is activated
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

2. Permission Errors
- Run terminal as administrator (Windows)
- Use sudo for installation commands (Linux/Mac)
- Check file and directory permissions

3. PDF Reading Errors
- Ensure PDFs are not password-protected
- Verify PDFs are not corrupted
- Check PDF permissions

4. Image Processing Errors
- Ensure sufficient disk space
- Verify Pillow installation
- Check output directory permissions

## Limitations

- Cannot process password-protected PDFs
- May not detect some complex formatting changes
- Processing time increases with PDF size
- Memory usage scales with PDF complexity

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please create an issue in the project repository.

## Acknowledgments

- PyMuPDF team for the PDF processing capabilities
- Pillow team for image processing functionality

---
