# Pull the pen / pop / board-push times out of hf/index.html for the SFX mix
import re, json, os
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(f"{P}/hf/index.html").read()
pen = [[float(a), float(a) + float(b), k] for k, a, b in re.findall(r'\b(write|hl|draw)\("\w+", ([\d.]+), ([\d.]+)\)', s)]
pops = [float(t) for t in re.findall(r'\bpop\("\w+", ([\d.]+)', s)]
kf = re.search(r'kf\.forEach\(\(_, i\) => pop\("b5k" \+ i, ([\d.]+) \+ i \* ([\d.]+)', s)
pops += [float(kf.group(1)) + i * float(kf.group(2)) for i in range(13)]
pops += [42.9 + i * 0.14 for i in range(3)] + [55.35]
boards = [float(t) for t in re.findall(r'\["b\d+", ([\d.]+), \w+\]', s)]
ev = {"pen": sorted(pen), "pop": sorted(pops), "push": [b - 0.6 for b in boards[1:]]}
json.dump(ev, open(f"{P}/scripts/events.json", "w"))
print(len(pen), "pen", len(pops), "pops", len(ev["push"]), "pushes")
