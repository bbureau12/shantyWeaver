import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

SONGBOOK_PATH = "shanty_songbook.json"

def load_songbook(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_songbook(path, songs):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(songs, f, indent=2, ensure_ascii=False)
    print("✅ Songbook updated.")

console = Console()

def display_song(song):
    console.clear()
    
    header = (
        f"[bold cyan]🎵 Title:[/bold cyan] {song['title']}\n"
        f"[yellow]📝 Tone:[/yellow] {song.get('tone', 'N/A')}\n"
        f"[green]📚 Context:[/green] {song.get('context', 'N/A')}"
    )

    console.print(Panel(header, title="🧾 Song Metadata", border_style="cyan"))

    console.print("\n[bold]🎶 Lyrics:[/bold]")

    lyrics = song.get("lyrics", "").split("\n")
    if not lyrics or lyrics == [""]:
        console.print("[red]⚠️ No lyrics found in this song![/red]")
        return

    for idx, line in enumerate(lyrics, start=1):
        console.print(f"[dim]{idx:>2}[/dim]: {line}")

    print()

def get_rating():
    while True:
        try:
            rating = int(input("⭐ Rate this song (1–5): "))
            if 1 <= rating <= 5:
                return rating
        except ValueError:
            pass
        print("❌ Invalid input. Please enter a number between 1 and 5.")

def get_optional(prompt):
    val = input(prompt)
    return val.strip() if val.strip() else "None"

def get_flagged_lines():
    lines = input("🚩 Flag any lines? (comma-separated line numbers or press enter to skip): ")
    if lines.strip():
        return [int(num.strip()) for num in lines.split(",") if num.strip().isdigit()]
    return []

def grade_next_song(songbook, reviewer):
    for song in songbook:
        if song.get("source") == "ai_generated" and song.get("lyrics") and (not song.get("human_rating") or song.get("human_rating") == "None"):
            display_song(song)
            song["human_rating"] = get_rating()
            song["review_notes"] = get_optional("🗒️  Any notes? (press enter to skip): ")
            song["reviewed_by"] = reviewer
            flagged = get_flagged_lines()
            if flagged:
                song["flagged_lines"] = flagged
            else:
                song.pop("flagged_lines", None)
            return True
    return False

def main():
    reviewer = input("👤 Please enter your reviewer name: ").strip()
    if not reviewer:
        print("❌ Reviewer name is required.")
        return

    if not os.path.exists(SONGBOOK_PATH):
        print("❌ Songbook not found.")
        return

    songbook = load_songbook(SONGBOOK_PATH)

    while True:
        found = grade_next_song(songbook, reviewer)
        if found:
            save_songbook(SONGBOOK_PATH, songbook)
            should_continue = input("➡️  Press Enter to grade the next song or type Q to quit: ").strip().lower()
            if should_continue == "q":
                print("👋 Exiting grader. See you next time.")
                break
        else:
            print("🎉 All songs have already been graded!")
            break

if __name__ == "__main__":
    main()
