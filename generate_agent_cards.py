from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap

def create_agent_card(agent_id, name, role, desc, theme_color=(14, 165, 233)): # Sky/Cyan 500
    # Card Config
    width, height = 400, 250
    card_bg = (255, 255, 255) # White card
    text_color = (30, 41, 59) # Slate 800
    
    img = Image.new('RGBA', (width, height), (0,0,0,0))
    
    # Inset the card significantly so glow is visible around edges
    # Card size effectively becomes 330x180 (400-70, 250-70)
    inset = 35
    
    # Draw Glow/Shadow
    # Create a larger canvas for the glow to sit on (relative to card size)
    shadow = Image.new('RGBA', (width, height), (0,0,0,0))
    s_draw = ImageDraw.Draw(shadow)
    
    # Draw a filled rect with the theme color, but transparent
    # This creates a colored glow
    glow_color = theme_color + (180,) # Increased alpha for stronger glow
    
    # Glow rect should be slightly larger than the card itself (which is at [inset, inset...])
    # Let's make it start 5px outside the card
    glow_inset = inset - 5
    s_draw.rounded_rectangle([glow_inset, glow_inset, width-glow_inset, height-glow_inset], radius=15, fill=glow_color)
    
    # Blur it significantly
    shadow = shadow.filter(ImageFilter.GaussianBlur(25))
    
    # Composite: Draw shadow first, then card on top
    # We need to paste shadow onto 'img', but 'img' is currently transparent.
    # Actually, we should paste the shadow onto the final grid, or compose here.
    # Let's compose here:
    final_card = Image.new('RGBA', (width, height), (0,0,0,0))
    final_card.paste(shadow, (0, 0), shadow)
    
    # Now draw the main card content
    card_face = Image.new('RGBA', (width, height), (0,0,0,0))
    c_draw = ImageDraw.Draw(card_face)
    
    c_draw.rounded_rectangle([inset, inset, width-inset, height-inset], radius=15, fill=card_bg, outline=theme_color, width=2)
    
    # Header Band
    c_draw.rounded_rectangle([inset, inset, width-inset, 50+inset], radius=15, corners=(True, True, False, False), fill=theme_color)
    
    # Fonts
    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_role = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 16)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_header = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_role = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Draw Header (Agent ID)
    c_draw.text((15+inset, 13+inset), f"AGENT {agent_id}", font=font_header, fill=(255, 255, 255))
    
    # Name
    c_draw.text((15+inset, 65+inset), name, font=font_title, fill=text_color)
    
    # Role (The Scribe)
    c_draw.text((15+inset, 95+inset), role, font=font_role, fill=theme_color)
    
    # Description (Wrapped)
    # Adjust width for wrapping due to inset
    lines = textwrap.wrap(desc, width=35)
    y_text = 130+inset
    for line in lines:
        c_draw.text((15+inset, y_text), line, font=font_body, fill=(71, 85, 105)) # Slate 600
        y_text += 20
        
    final_card.paste(card_face, (0,0), card_face)
    return final_card

def create_grid():
    # Palette from README badges
    colors = [
        (93, 104, 138),   # Slate Blue #5D688A
        (247, 165, 165),  # Soft Red #F7A5A5
        (255, 219, 182)   # Soft Orange #FFDBB6
    ]

    agents = [
        ("1", "Forensic Analyst", "The Auditor", "Calculates 29+ forensic ratios (Beneish M-Score, Altman Z) to detect anomalies."),
        ("2", "Shell Hunter", "The Detective", "Uses Graph Theory to detect circular trading rings and shell companies."),
        ("3", "Risk Scorer", "The Judge", "Synthesizes all outputs into a unified Risk Score (0-100) with explainability."),
        ("4", "Compliance Agent", "The Enforcer", "Validates compliance with SEBI LODR, Ind AS, and Companies Act."),
        ("5", "Report Generator", "The Scribe", "Compiles complex findings into executive-grade PDF and Excel reports."),
        ("6", "Orchestrator", "The Manager", "Coordinates tasks and data flow between all agents."),
        ("7", "QA RAG System", "The Librarian", "Vector-based 'Chat with Data' for querying annual reports instantly."),
        ("8", "Market Sentinel", "The Watcher", "Monitors news & search trends for sentiment and pump-and-dump signals."),
        ("9", "Network Analysis", "Back-end Logic", "Powers the RPT graph construction and cycle detection algorithms."),
        ("10", "Auditor", "The Reviewer", "Deep analyzes text in annual reports for governance red flags."),
        ("11", "Exchange Agent", "The Source", "Fetches official shareholding patterns from exchanges/screeners."),
        ("12", "Cartographer", "The Mapper", "Tracks cross-border financial flows and jurisdictional risks.")
    ]
    
    # Grid Config
    cols = 3
    rows = 4
    card_w, card_h = 400, 250
    padding = 20
    
    grid_w = cols * card_w + (cols + 1) * padding
    grid_h = rows * card_h + (rows + 1) * padding
    
    # Transparent background for the grid itself
    grid_img = Image.new('RGBA', (grid_w, grid_h), (0,0,0,0))
    
    for idx, (aid, name, role, desc) in enumerate(agents):
        # Cycle through colors: 0, 1, 2, 0, 1, 2...
        theme_color = colors[idx % len(colors)]
        
        card = create_agent_card(aid, name, role, desc, theme_color=theme_color)
        
        col = idx % cols
        row = idx // cols
        
        x = padding + col * (card_w + padding)
        y = padding + row * (card_h + padding)
        
        grid_img.paste(card, (x, y), card)
        
    ensure_dir('assets')
    grid_img.save('assets/council_of_agents_grid.png')
    print("Generated assets/council_of_agents_grid.png")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == "__main__":
    create_grid()
