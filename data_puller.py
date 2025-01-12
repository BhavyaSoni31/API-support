import requests
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

def fetch_notion_page_blocks(page_id, page_size=100, all_blocks=[]):
    """
    Fetch all blocks (children) of a Notion page by its ID, handling pagination.
    
    Parameters:
        page_id (str): The ID of the Notion page to fetch blocks for.
        page_size (int): The number of blocks to fetch per request (max 100).
        
    Returns:
        list: A list of JSON objects representing each block.
    """
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'
    headers = {
        'Authorization': f'Bearer {NOTION_API_KEY}',
        'Notion-Version': '2022-06-28'
    }

    start_cursor = None
    while True:
        params = {'page_size': page_size}
        if start_cursor:
            params['start_cursor'] = start_cursor
            
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            json_response = response.json()

            all_blocks.extend(json_response.get('results', []))
            print(json_response.get('results', []))
            for block in json_response.get('results', []):
                print(f"{block.get('type')}")
                if block.get("has_children"):
                    print(f"recursive fetch {block.get('type')}")
                    fetch_notion_page_blocks(block.get("id"), page_size=100, all_blocks=all_blocks)
            if not json_response.get('has_more', False):
                break
            start_cursor = json_response.get('next_cursor')
            
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
    return all_blocks


def extract_documents_from_blocks(blocks):
    """
    Extract and format content from Notion blocks into Markdown for structured text processing.
    
    Parameters:
        blocks (list): A list of JSON objects representing each block.
        
    Returns:
        str: A string containing the formatted Markdown text.
    """
    markdown_content = []
    
    for block in blocks:
        block_type = block.get('type')
        
        # Handle text-based blocks with Markdown formatting
        if block_type in ['paragraph']:
            rich_text = block.get('paragraph', {}).get('rich_text', [])
            text_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            if text_content:
                markdown_content.append(text_content)
        
        elif block_type in ['heading_1', 'heading_2', 'heading_3']:
            rich_text = block.get(block_type, {}).get('rich_text', [])
            text_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            if text_content:
                heading_level = int(block_type.split('_')[1])
                markdown_content.append(f"{'#' * heading_level} {text_content}")
        
        elif block_type in ['numbered_list_item']:
            rich_text = block.get('numbered_list_item', {}).get('rich_text', [])
            text_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            if text_content:
                markdown_content.append(f"1. {text_content}")
        
        elif block_type in ['bulleted_list_item']:
            rich_text = block.get('bulleted_list_item', {}).get('rich_text', [])
            text_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            if text_content:
                markdown_content.append(f"- {text_content}")
        
        elif block_type == 'quote':
            rich_text = block.get('quote', {}).get('rich_text', [])
            text_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            if text_content:
                markdown_content.append(f"> {text_content}")
        
        elif block_type == 'code':
            code_block = block.get('code', {})
            rich_text = code_block.get('rich_text', [])
            code_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            language = code_block.get('language', 'plaintext')
            if code_content:
                markdown_content.append(f"```{language}\n{code_content}\n```")
        
        elif block_type == 'child_page':
            title = block.get('child_page', {}).get('title', '')
            markdown_content.append(f"## Child Page: {title}")
        
        elif block_type == 'callout':
            rich_text = block.get('callout', {}).get('rich_text', [])
            text_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            emoji = block.get('callout', {}).get('icon', {}).get('emoji', '')
            markdown_content.append(f"> {emoji} {text_content}")
        
        elif block_type == 'bookmark':
            url = block.get('bookmark', {}).get('url', '')
            markdown_content.append(f"[Bookmark]({url})")
        
        elif block_type == 'table':
            markdown_content.append("| Table | Placeholder |")
            markdown_content.append("|-------|-------------|")
        
        elif block_type == 'table_row':
            cells = block.get('table_row', {}).get('cells', [])
            row_content = " | ".join([''.join([cell.get('text', {}).get('content', '') for cell in cell_group]) for cell_group in cells])
            markdown_content.append(f"| {row_content} |")
    
    return '\n'.join(markdown_content)

try:
    blocks = fetch_notion_page_blocks(NOTION_PAGE_ID)
    documents = extract_documents_from_blocks(blocks)
    f = open("notion_data.txt", "w")
    f.write(documents)
    f.close()
except Exception as ex:
    print(f"Error occurred while pulling notion data. {ex}")