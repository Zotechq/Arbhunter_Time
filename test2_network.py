from network import fetch_page

soup = fetch_page("https://www.flashscore.com/football/kenya/premier-league", 1)
print("Success!" if soup else "Failed")
if soup:
    print(f"HTML length: {len(str(soup))} chars")