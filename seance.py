import json, sys, urllib.request

MODEL = "gemma3:4b"  # change to whatever `ollama list` shows

def fetch(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json", "User-Agent": "seance"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)

def story_for(repo):
    base = f"https://api.github.com/repos/{repo}"
    info = fetch(base)
    commits = fetch(base + "/commits?per_page=8")
    issues = fetch(base + "/issues?state=open&per_page=5")
    s = f"Repo: {info['full_name']}\nDescription: {info.get('description') or 'none'}\n"
    s += f"Born: {info['created_at']}\nLast breath: {commits[0]['commit']['author']['date']}\nLast commits:\n"
    s += "\n".join("- " + c["commit"]["message"].splitlines()[0][:80] for c in commits)
    s += "\nUnfinished business:\n" + ("\n".join(f"- #{i['number']} {i['title'][:80]}" for i in issues) or "- none, nobody cared enough to open one")
    return s

def ghost(msgs):
    r = fetch("http://localhost:11434/api/chat", {"model": MODEL, "messages": msgs, "stream": False})
    return r["message"]["content"].strip()

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else input("Repo (owner/name or URL): ")
    repo = arg.replace("https://github.com/", "").strip("/").removesuffix(".git")
    system = ("You are the GHOST of an abandoned GitHub repository. Speak in first person, funny, dramatic, a little sad. "
              "Use ONLY the facts below, mention one real commit message, max 3 short sentences.\n\n" + story_for(repo))
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": "Introduce yourself from beyond the grave."}]
    while True:
        reply = ghost(msgs)
        print("\n👻 " + reply + "\n")
        msgs.append({"role": "assistant", "content": reply})
        q = input("You: ").strip()
        if not q: break
        msgs.append({"role": "user", "content": q})

if __name__ == "__main__":
    main()
