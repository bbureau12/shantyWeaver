import json
import os
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer, util
from colorama import init, Fore, Style

init(autoreset=True)

class PromptGrader:
    def __init__(self, prompt, grader_name):
        self.prompt = prompt
        self.grader_name = grader_name
        self.score = 0.0
        self.notes = []
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def grade_title_length(self):
        title_words = len(self.prompt['title'].split())
        if 2 <= title_words <= 6:
            self.score += 1.0
            self.notes.append(f"{Fore.GREEN}✅ Title length OK ({title_words} words).")
        else:
            self.score -= 0.5
            self.notes.append(f"{Fore.YELLOW}⚠️ Title length unusual ({title_words} words).")

    def grade_title_plagiarism(self):
        spark_title = self.prompt['muse_spark']['name']
        inspiration_title = self.prompt.get('inspiration_title', '')
        generated_title = self.prompt['title']

        max_similarity = max(
            SequenceMatcher(None, spark_title.lower(), generated_title.lower()).ratio(),
            SequenceMatcher(None, inspiration_title.lower(), generated_title.lower()).ratio()
        )

        if max_similarity > 0.8:
            self.score -= 1.0
            self.notes.append(f"{Fore.RED}⚠️ Title very similar to source (similarity {max_similarity:.2f}).")
        else:
            self.score += 1.0
            self.notes.append(f"{Fore.GREEN}✅ Title original enough (similarity {max_similarity:.2f}).")

    def grade_lyrical_plagiarism(self):
        inspiration = self.prompt['muse_spark']['inspiration']
        lyrical_sample = self.prompt['lyrical_sample']

        embeddings = self.embedder.encode([inspiration, lyrical_sample])
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

        if similarity > 0.8:
            self.score -= 1.0
            self.notes.append(f"{Fore.RED}⚠️ Lyrical sample too close to inspiration (similarity {similarity:.2f}).")
        else:
            self.score += 1.0
            self.notes.append(f"{Fore.GREEN}✅ Lyrics show good originality (similarity {similarity:.2f}).")

    def grade(self):
        self.grade_title_length()
        self.grade_title_plagiarism()
        self.grade_lyrical_plagiarism()
        return self.score, self.notes

def main():
    grades = []
    prompt_folder = "log"  # assumes JSON files are here
    prompt_files = [f for f in os.listdir(prompt_folder) if f.startswith('prompt') and f.endswith('log.json')]

    grader_name = input(f"{Fore.CYAN}Enter your grader name (example: beau): ").strip().lower()

    print(f"\n{Fore.CYAN}🌟 PromptGrader ready, grading as {grader_name.upper()}! {len(prompt_files)} prompts found.\n")

    for file in prompt_files:
        with open(os.path.join(prompt_folder, file), 'r') as f:
            prompt = json.load(f)

        # Skip if already graded
        if 'grades' in prompt and grader_name in prompt['grades']:
            continue

        grader = PromptGrader(prompt, grader_name)
        score, notes = grader.grade()

        print(f"{Fore.MAGENTA}📜 Grading prompt: {Style.BRIGHT}{prompt['title']}{Style.RESET_ALL}")
        for note in notes:
            print(note)
        print(f"{Fore.YELLOW}⚖️ Final Score: {Fore.GREEN}{score:.2f}/3.0\n")

        # Save grading info into the prompt
        if 'grades' not in prompt:
            prompt['grades'] = {}
        prompt['grades'][grader_name] = {
            "score": score,
            "notes": [n.replace(Fore.GREEN, '').replace(Fore.RED, '').replace(Fore.YELLOW, '').replace(Fore.CYAN, '').replace(Fore.MAGENTA, '').replace(Style.RESET_ALL, '') for n in notes]
        }

        # Write prompt back
        with open(os.path.join(prompt_folder, file), 'w') as f:
            json.dump(prompt, f, indent=2)

        # Add to session grades
        grades.append({
            "title": prompt['title'],
            "score": score,
            "notes": [n.replace(Fore.GREEN, '').replace(Fore.RED, '').replace(Fore.YELLOW, '').replace(Fore.CYAN, '').replace(Fore.MAGENTA, '').replace(Style.RESET_ALL, '') for n in notes]
        })

        # Continue or Quit
        user_input = input(f"{Fore.CYAN}Press Enter to continue or [Q] to quit grading: ").strip().lower()
        if user_input == 'q':
            break

    # Final Report
    if grades:
        total_score = sum(g['score'] for g in grades)
        average_score = total_score / len(grades)

        print(f"\n{Fore.CYAN}🎉 Grading session complete!")
        print(f"{Fore.YELLOW}⭐ Grader: {grader_name.upper()}")
        print(f"📚 Prompts graded: {len(grades)}")
        print(f"⚖️ Average Score: {Fore.GREEN}{average_score:.2f}/3.0")

        # Fun medals!
        if average_score > 2.5:
            print(f"{Fore.GREEN}🏅 Rank: GOLD SINGER")
        elif average_score > 2.0:
            print(f"{Fore.CYAN}🥈 Rank: SILVER SAILOR")
        elif average_score > 1.0:
            print(f"{Fore.YELLOW}🥉 Rank: BRONZE BUCCANEER")
        else:
            print(f"{Fore.RED}⚓ Rank: DECKHAND IN TRAINING")

        # Save grades to session log
        with open("grades.json", "w") as gfile:
            json.dump({"grader": grader_name, "grades": grades}, gfile, indent=2)
    else:
        print(f"{Fore.RED}⚠️ No prompts graded in this session.")

if __name__ == "__main__":
    main()
