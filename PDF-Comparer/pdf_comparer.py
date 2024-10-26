import fitz
from PIL import Image, ImageDraw
import difflib
import re
import os
import argparse
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class TextBlock:
    """Data class to store text block information with enhanced attributes"""
    bbox: Tuple[float, float, float, float]
    text: str
    page: int
    font: str = ""
    size: float = 0
    color: Tuple[float, float, float] = (0, 0, 0)

class PDFComparer:
    def __init__(self, 
                 similarity_threshold: float = 0.8,
                 position_threshold: float = 5.0,
                 check_formatting: bool = True):
        """
        Initialize PDF comparer with enhanced configuration
        
        Args:
            similarity_threshold: Float between 0 and 1, higher means more similar text
            position_threshold: Maximum allowed position difference in points
            check_formatting: Whether to check formatting changes (font, size, color)
        """
        self.similarity_threshold = similarity_threshold
        self.position_threshold = position_threshold
        self.check_formatting = check_formatting

    # [Previous methods remain unchanged...]
    def get_color_tuple(self, span: dict) -> Tuple[float, float, float]:
        """
        Safely extract color information from span
        """
        try:
            color = span.get("color", 0)
            # Handle integer color values
            if isinstance(color, int):
                # Convert to RGB tuple (assuming black if 0)
                return (0, 0, 0)
            # Handle tuple/list color values
            elif isinstance(color, (tuple, list)):
                return tuple(float(c) for c in color[:3])
            else:
                return (0, 0, 0)
        except:
            return (0, 0, 0)

    def get_text_blocks(self, pdf_path: str) -> Dict[int, List[TextBlock]]:
        """
        Extract text blocks with enhanced positioning and formatting information
        """
        doc = fitz.open(pdf_path)
        pages_blocks = defaultdict(list)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get detailed text information including formatting
            text_page = page.get_textpage()
            text_dict = text_page.extractDICT()
            
            for block in text_dict["blocks"]:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            bbox = tuple(span["bbox"])
                            # Extract formatting information safely
                            font = span.get("font", "")
                            size = float(span.get("size", 0))
                            color = self.get_color_tuple(span)
                            
                            text_block = TextBlock(
                                bbox=bbox,
                                text=text,
                                page=page_num,
                                font=font,
                                size=size,
                                color=color
                            )
                            pages_blocks[page_num].append(text_block)
            
            # Sort blocks by vertical position for more accurate comparison
            pages_blocks[page_num].sort(key=lambda x: (x.bbox[1], x.bbox[0]))
        
        doc.close()
        return dict(pages_blocks)

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity ratio between two text strings with improved accuracy
        """
        text1 = re.sub(r'\s+', ' ', text1.lower().strip())
        text2 = re.sub(r'\s+', ' ', text2.lower().strip())
        
        sequence_matcher = difflib.SequenceMatcher(None, text1, text2)
        return sequence_matcher.ratio()

    def blocks_are_similar(self, block1: TextBlock, block2: TextBlock) -> bool:
        """
        Compare two blocks considering both content and positioning
        """
        text_similar = self.calculate_text_similarity(block1.text, block2.text) >= self.similarity_threshold
        
        position_similar = all(
            abs(b1 - b2) <= self.position_threshold
            for b1, b2 in zip(block1.bbox, block2.bbox)
        )
        
        if self.check_formatting:
            formatting_similar = (
                block1.font == block2.font and
                abs(block1.size - block2.size) < 0.1 and
                block1.color == block2.color
            )
            return text_similar and position_similar and formatting_similar
        
        return text_similar and position_similar

    def find_differences(self, original_blocks: Dict[int, List[TextBlock]], 
                        modified_blocks: Dict[int, List[TextBlock]]) -> List[TextBlock]:
        """
        Find differences between original and modified PDFs with comprehensive checking
        """
        differences = []
        processed_pages = set()
        
        all_pages = set(original_blocks.keys()) | set(modified_blocks.keys())
        
        for page_num in all_pages:
            orig_page_blocks = original_blocks.get(page_num, [])
            mod_page_blocks = modified_blocks.get(page_num, [])
            
            if not orig_page_blocks:
                differences.extend(mod_page_blocks)
                continue
            if not mod_page_blocks:
                continue  
                
            unmatched_orig = set(range(len(orig_page_blocks)))
            unmatched_mod = set(range(len(mod_page_blocks)))
            
            for i in list(unmatched_mod):
                mod_block = mod_page_blocks[i]
                
                for j in list(unmatched_orig):
                    orig_block = orig_page_blocks[j]
                    
                    if self.blocks_are_similar(mod_block, orig_block):
                        unmatched_mod.remove(i)
                        unmatched_orig.remove(j)
                        break
            
            differences.extend(mod_page_blocks[i] for i in unmatched_mod)
            
            processed_pages.add(page_num)
        
        return differences

    def highlight_differences(self, pdf_path: str, differences: List[TextBlock], 
                            output_dir: str) -> None:
        """
        Create accurate highlighting of differences, skipping pages with no changes
        """
        os.makedirs(output_dir, exist_ok=True)
        doc = fitz.open(pdf_path)
        
        page_differences = defaultdict(list)
        for diff in differences:
            page_differences[diff.page].append(diff)
        
        # Process only pages with differences
        pages_with_changes = page_differences.keys()
        if pages_with_changes:
            print(f"Processing {len(pages_with_changes)} pages with changes...")
            
            for page_num in range(len(doc)):
                if page_num not in page_differences:
                    continue  
                    
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(3, 3)) 
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img = img.convert('RGBA')
                
                highlight_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(highlight_layer)
                
                scale = 3 
                
                for diff in page_differences[page_num]:
                    x0, y0, x1, y1 = [coord * scale for coord in diff.bbox]
                    
                    draw.rectangle(
                        [x0, y0, x1, y1],
                        fill=(255, 255, 0, 80),  # Semi-transparent yellow
                        outline=(255, 0, 0, 255),  # Red border
                        width=3
                    )
                
                img = Image.alpha_composite(img, highlight_layer)
                
                output_path = os.path.join(output_dir, f"page_{page_num + 1}_differences.png")
                img.convert('RGB').save(output_path, 'PNG', quality=95)
                print(f"Saved highlighted differences for page {page_num + 1}")
        
        doc.close()

def compare_pdfs(original_path: str, modified_path: str, output_dir: str,
                similarity_threshold: float = 0.8,
                position_threshold: float = 5.0,
                check_formatting: bool = True):
    """
    Main function to compare PDFs with enhanced configuration options
    """
    try:
        comparer = PDFComparer(
            similarity_threshold=similarity_threshold,
            position_threshold=position_threshold,
            check_formatting=check_formatting
        )
        
        print("Extracting text from original PDF...")
        original_blocks = comparer.get_text_blocks(original_path)
        
        print("Extracting text from modified PDF...")
        modified_blocks = comparer.get_text_blocks(modified_path)
        
        print("Finding differences...")
        differences = comparer.find_differences(original_blocks, modified_blocks)
        
        if differences:
            print(f"Found {len(differences)} differences across {len(set(d.page for d in differences))} pages")
            print("Highlighting differences...")
            comparer.highlight_differences(modified_path, differences, output_dir)
            print("Comparison completed successfully!")
        else:
            print("No differences found between the PDFs")
            
    except Exception as e:
        print(f"Error during PDF comparison: {str(e)}")
        raise

def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Compare two PDF files and highlight differences')
    
    parser.add_argument('original_pdf', type=str, help='Path to the original PDF file')
    parser.add_argument('modified_pdf', type=str, help='Path to the modified PDF file')
    parser.add_argument('output_dir', type=str, help='Directory to save the difference images')
    
    # Optional arguments
    parser.add_argument('--similarity', type=float, default=0.8,
                        help='Similarity threshold (0.0-1.0, default: 0.8)')
    parser.add_argument('--position', type=float, default=5.0,
                        help='Position threshold in points (default: 5.0)')
    parser.add_argument('--ignore-formatting', action='store_true',
                        help='Ignore formatting changes (font, size, color)')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if not os.path.exists(args.original_pdf):
        raise FileNotFoundError(f"Original PDF not found: {args.original_pdf}")
    if not os.path.exists(args.modified_pdf):
        raise FileNotFoundError(f"Modified PDF not found: {args.modified_pdf}")
    
    compare_pdfs(
        args.original_pdf,
        args.modified_pdf,
        args.output_dir,
        similarity_threshold=args.similarity,
        position_threshold=args.position,
        check_formatting=not args.ignore_formatting
    )