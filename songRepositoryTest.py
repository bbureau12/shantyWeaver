from songRepository import ShantyRepository

repo = ShantyRepository("shanties.json")

print("\n🔍 Searching by prompt:")
results = repo.search_by_prompt(
    text="calm seas and a weary crew under twilight",
    tone="sad",
    k=2,
    add_random=True
)

for song in results:
    print(f"\n🎵 {song['title']} — {song['tone']}")
    print(song['lines'][:250], "...\n")
