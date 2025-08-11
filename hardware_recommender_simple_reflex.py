"""Single-file hardware recommender GUI (checkbox -> spec)."""

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk


@dataclass(frozen=True)
class Spec:
    cpu: str
    ram_gb: int
    storage: str
    gpu: str
    notes: str = ""


RULES = [
    (
        "ml",
        "AI / Machine Learning / Data Science",
        Spec(
            "12+ core modern CPU",
            64,
            "1TB NVMe SSD",
            "High-end NVIDIA (e.g., RTX 4080/4090)",
            "Heavy ML workloads need strong GPU & RAM.",
        ),
    ),
    (
        "video",
        "Video Editing / 3D / Rendering",
        Spec(
            "8+ core CPU",
            32,
            "1TB NVMe SSD",
            "High-mid GPU (e.g., RTX 4070)",
            "GPU VRAM and fast storage matter.",
        ),
    ),
    (
        "gaming",
        "Gaming (AAA)",
        Spec(
            "6-8 core high clock CPU",
            16,
            "1TB NVMe SSD",
            "Mid-high GPU (e.g., RTX 3060/3070)",
            "Balance CPU/GPU; 16GB RAM baseline.",
        ),
    ),
    (
        "dev",
        "Programming / Software Dev",
        Spec(
            "6 core CPU",
            16,
            "512GB SSD",
            "Integrated or entry GPU",
            "RAM helps with IDEs & containers.",
        ),
    ),
    (
        "office",
        "Light Office / Browsing",
        Spec(
            "4 core energy-efficient CPU",
            8,
            "256-512GB SSD",
            "Integrated",
            "Low intensity general tasks.",
        ),
    ),
    (
        "server",
        "Server / Virtualization / Docker",
        Spec(
            "12+ core CPU",
            64,
            "2TB SSD+",
            "Optional",
            "Cores & RAM for many VMs/containers.",
        ),
    ),
]
DEFAULT = Spec(
    "4-6 core CPU",
    16,
    "512GB SSD",
    "Integrated or basic GPU",
    "Default balanced build.",
)


def recommend(ids):
    for wid, _, spec in RULES:
        if wid in ids:
            return spec
    return DEFAULT


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hardware Recommender")
        self.geometry("540x460")
        self.vars = {}
        self._build()

    def _build(self):
        ttk.Label(self, text="Select workload categories:").pack(
            anchor="w", padx=10, pady=(8, 4)
        )
        box = ttk.Frame(self)
        box.pack(fill="x", padx=10)
        left, right = ttk.Frame(box), ttk.Frame(box)
        left.pack(side="left", fill="x", expand=True)
        right.pack(side="left", fill="x", expand=True)
        half = (len(RULES) + 1) // 2
        for i, (wid, label, _spec) in enumerate(RULES):
            v = tk.BooleanVar(value=False)
            self.vars[wid] = v
            ttk.Checkbutton((left if i < half else right), text=label, variable=v).pack(
                anchor="w", pady=1
            )
        bf = ttk.Frame(self)
        bf.pack(fill="x", padx=10, pady=6)
        ttk.Button(bf, text="Recommend", command=self.on_recommend).pack(side="left")
        ttk.Button(bf, text="Clear", command=self.on_clear).pack(side="left", padx=6)
        ttk.Label(self, text="Suggested Specs:").pack(anchor="w", padx=10)
        self.out = tk.Text(
            self, height=12, wrap="word", state="disabled", background="#f7f7f7"
        )
        self.out.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    def on_clear(self):
        [v.set(False) for v in self.vars.values()]
        self._out("")

    def on_recommend(self):
        ids = [wid for wid, v in self.vars.items() if v.get()]
        spec = recommend(ids)
        labels = [l for wid, l, _ in RULES if wid in ids]
        wl = ", ".join(labels) if labels else "(none)"
        self._out(
            f"Workloads: {wl}\n\nCPU: {spec.cpu}\nRAM: {spec.ram_gb} GB\nStorage: {spec.storage}\nGPU: {spec.gpu}\nNotes: {spec.notes}"
        )

    def _out(self, text):
        self.out.configure(state="normal")
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, text)
        self.out.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()
