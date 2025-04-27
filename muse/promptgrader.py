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
        self.human_details = {}
        self.human_notes = []
        self.sage_details = {}
        self.sage_notes = []
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def manual_numeric_grade(self, question):
        while True:
            print(f"\n{Fore.CYAN}{question}")
            print("[1] Very Poor | [2] Poor | [3] Fair | [4] Good | [5] Excellent")
            print(f"{Fore.YELLOW}Or type 'Q' to quit grading and save progress.")
            user_input = input(f"{Fore.YELLOW}Enter your score (1-5) or Q: ").strip().lower()
            if user_input == 'q':
                raise KeyboardInterrupt  # We will catch this in main() to trigger save
            try:
                score = int(user_input)
                if 1 <= score <= 5:
                    return score
                else:
                    print(f"{Fore.RED}Invalid number. Enter between 1 and 5.")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Numbers only or 'Q' to quit.")
    def manual_binary_grade(self, question):
        while True:
            print(f"\n{Fore.CYAN}{question}")
            print("[0] No | [1] Yes")
            print(f"{Fore.YELLOW}Or type 'Q' to quit grading and save progress.")
            user_input = input(f"{Fore.YELLOW}Enter 1 or 0: ").strip().lower()
            if user_input == 'q':
                raise KeyboardInterrupt  # We will catch this in main() to trigger save
            try:
                score = int(user_input)
                if score == 1:
                    return 1
                return 0
            except ValueError:
                return 0

    def sage_title_length(self):
        title_words = len(self.prompt['title'].split())
        if 2 <= title_words <= 6:
            self.sage_details["title_length"] = 5
            self.sage_notes.append("✅ Title length ideal (2–6 words).")
        elif 1 <= title_words <= 8:
            self.sage_details["title_length"] = 4
            self.sage_notes.append("⚠️ Title slightly unusual but acceptable.")
        else:
            self.sage_details["title_length"] = 2
            self.sage_notes.append("❌ Title length poor.")

    def sage_title_originality(self):
            spark_title = self.prompt['muse_spark']['name']
            inspiration_title = self.prompt.get('inspiration_title', '')
            generated_title = self.prompt['title']

            max_similarity = max(
                SequenceMatcher(None, spark_title.lower(), generated_title.lower()).ratio(),
                SequenceMatcher(None, inspiration_title.lower(), generated_title.lower()).ratio()
            )

            if max_similarity < 0.5:
                self.sage_details["title_originality"] = 5
                self.sage_notes.append("✅ Title highly original.")
            elif max_similarity < 0.7:
                self.sage_details["title_originality"] = 4
                self.sage_notes.append("⚠️ Title moderately original.")
            else:
                self.sage_details["title_originality"] = 2
                self.sage_notes.append("❌ Title too similar to inspiration.")


    def sage_lyrical_originality(self):
        inspiration = self.prompt['muse_spark']['inspiration']
        lyrical_sample = self.prompt['lyrical_sample']

        embeddings = self.embedder.encode([inspiration, lyrical_sample])
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

        if similarity < 0.5:
            self.sage_details["lyrical_originality"] = 5
            self.sage_notes.append("✅ Lyrics highly original.")
        elif similarity < 0.7:
            self.sage_details["lyrical_originality"] = 4
            self.sage_notes.append("⚠️ Lyrics moderately original.")
        else:
            self.sage_details["lyrical_originality"] = 2
            self.sage_notes.append("❌ Lyrics too close to inspiration.")


    def grade(self):
        self.human_details["title_length"] = self.manual_numeric_grade("🎵 Title Length: (2–6 words ideal?)")
        self.human_details["title_originality"] = self.manual_numeric_grade("🎵 Title Originality: (Is the title original?)")
        self.human_details["lyrical_originality"] = self.manual_numeric_grade("🎵 Lyrical Originality: (Are the lyrics original?)")
        self.human_details["lyrical_quality"] = self.manual_numeric_grade("🎵 Lyrical Quality: (Are the lyrics poetic and well-crafted?)")
        self.human_details["ai_imagery"] = self.manual_numeric_grade("🎵 AI Imagery: (Is the imagery fitting for an AI character?)")
        self.human_details["hall_of_fame"] = self.manual_binary_grade("🎵 Integrate into hall of fame?")

        for key, score in self.human_details.items():
            if score >= 4:
                self.human_notes.append(f"✅ {key.replace('_', ' ').capitalize()} good.")
            elif score == 3:
                self.human_notes.append(f"⚠️ {key.replace('_', ' ').capitalize()} fair.")
            else:
                self.human_notes.append(f"❌ {key.replace('_', ' ').capitalize()} poor.")

        # Sage grading (optional for later)
        self.sage_title_length()
        self.sage_title_originality()
        self.sage_lyrical_originality()

        return {
            "human": {
                "details": self.human_details,
                "total_score": sum(self.human_details.values()),
                "notes": self.human_notes
            },
            "sage": {
                "details": self.sage_details,
                "total_score": sum(self.sage_details.values()),
                "notes": self.sage_notes
            }
        }


def main():
    grades = []
    prompt_folder = "log"  # assumes JSON logs are here
    prompt_files = [f for f in os.listdir(prompt_folder) if f.startswith('prompt') and f.endswith('log.json')]

    grader_name = input(f"{Fore.CYAN}Enter your grader name (example: beau): ").strip().lower()

    print(f"\n{Fore.CYAN}🌟 PromptGrader ready, grading as {grader_name.upper()}! {len(prompt_files)} log files found.\n")

    for file in prompt_files:
        with open(os.path.join(prompt_folder, file), 'r') as f:
            prompts = json.load(f)

        modified = False
        graded_count = 0
        for prompt in prompts:
            graded_count += 1
            if 'grades' in prompt and grader_name in prompt['grades']:
                continue
            remaining = len(prompts) - graded_count 
            print(f"{Fore.WHITE}\n🚀 {Style.BRIGHT}{remaining} prompts remain!{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}\n📜 Title: {Style.BRIGHT}{prompt['title']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🌟 Muse Spark: {Style.RESET_ALL}\n{prompt['muse_spark']}\n")
            print(f"{Fore.BLUE}🎵 Lyrics Sample:{Style.RESET_ALL}\n{prompt['lyrical_sample']}\n")
            print(f"{Fore.YELLOW}🧭 Inspired by: {Style.BRIGHT}{prompt.get('inspiration_title', 'N/A')}{Style.RESET_ALL}\n")
            print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")
            existing_graders = list(prompt.get('grades', {}).keys())
            if existing_graders:
                print(f"{Fore.CYAN}Existing graders: {existing_graders}")

            grader = PromptGrader(prompt, grader_name)
            try:
                grader = PromptGrader(prompt, grader_name)
                grading_result = grader.grade()
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️ Quitting early — saving progress now!")
                break
            human_grade = grading_result["human"]
            sage_grade = grading_result["sage"]

            prompt.setdefault('grades', {})
            prompt['grades'][grader_name] = {
                "total_score": human_grade["total_score"],
                "details": human_grade["details"],
                "notes": human_grade["notes"]
            }
            prompt['grades']['sage'] = {
                "total_score": sage_grade["total_score"],
                "details": sage_grade["details"],
                "notes": sage_grade["notes"]
            }

            grades.append({
                "title": prompt['title'],
                "score": human_grade["total_score"],
                "notes": human_grade["notes"]
            })
            modified = True

        # If file modified, save it
        if modified:
            with open(os.path.join(prompt_folder, file), 'w') as f:
                json.dump(prompts, f, indent=2)

    # End of session report
    if grades:
        total_score = sum(g['score'] for g in grades)
        average_score = total_score / len(grades)

        print(f"\n{Fore.CYAN}🎉 Grading session complete!")
        print(f"{Fore.YELLOW}⭐ Grader: {grader_name.upper()}")
        print(f"📚 Prompts graded: {len(grades)}")
        print(f"⚖️ Average Score: {Fore.GREEN}{average_score:.2f}/25.0")
    else:
        print(f"{Fore.RED}⚠️ No prompts graded in this session.")

if __name__ == "__main__":
    main()
