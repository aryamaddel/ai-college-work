"""Single-file hardware recommender GUI (checkbox -> spec)."""

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
from typing import List, Dict


@dataclass(frozen=True)
class Spec:
    """Human-facing spec description produced by rules.

    This remains a simple container: the *agent* still reacts only to the
    current set of checked workloads (no memory / no learning) -> a reflex.
    """
    cpu: str
    ram_gb: int
    storage: str
    gpu: str
    notes: str = ""


# RULES: (workload_id, label, base human spec, internal numeric meta for aggregation)
# The numeric meta lets the reflex agent combine multiple simultaneous workload
# stimuli into a single recommendation by taking maxima (still stateless input->output).
# Meta keys: cores (int), ram (GB), storage (GB), gpu_rank (1..6)
RULES: List[tuple] = [
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
        {"cores": 12, "ram": 64, "storage": 1000, "gpu_rank": 5},
    ),
    (
        "hpc",
        "Scientific / HPC Simulation",
        Spec(
            "16+ core CPU (multi-socket beneficial)",
            128,
            "2TB NVMe + Scratch SSD",
            "High-end or Multi-GPU",
            "CPU core count & memory bandwidth critical.",
        ),
        {"cores": 16, "ram": 128, "storage": 2000, "gpu_rank": 6},
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
        {"cores": 8, "ram": 32, "storage": 1000, "gpu_rank": 4},
    ),
    (
        "stream",
        "Streaming / Capture",
        Spec(
            "8 core high clock CPU",
            32,
            "1TB NVMe SSD",
            "Mid-high GPU (NVENC capable)",
            "Extra threads help encode + play/produce.",
        ),
        {"cores": 8, "ram": 32, "storage": 1000, "gpu_rank": 4},
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
        {"cores": 8, "ram": 16, "storage": 1000, "gpu_rank": 4},
    ),
    (
        "vr",
        "VR / AR Development",
        Spec(
            "8+ core CPU",
            32,
            "1TB NVMe SSD",
            "High-mid GPU (90+ FPS capable)",
            "Low latency + GPU headroom important.",
        ),
        {"cores": 8, "ram": 32, "storage": 1000, "gpu_rank": 4},
    ),
    (
        "photo",
        "Photography / Graphic Design",
        Spec(
            "6 core CPU",
            32,
            "1TB NVMe SSD",
            "Mid GPU or Integrated",
            "RAM + fast scratch disk help large RAW edits.",
        ),
        {"cores": 6, "ram": 32, "storage": 1000, "gpu_rank": 3},
    ),
    (
        "audio",
        "Audio Production / DAW",
        Spec(
            "6-8 core low-latency CPU",
            32,
            "1TB NVMe SSD",
            "Integrated or entry GPU",
            "Low DPC latency and RAM for sample libraries.",
        ),
        {"cores": 8, "ram": 32, "storage": 1000, "gpu_rank": 2},
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
        {"cores": 6, "ram": 16, "storage": 512, "gpu_rank": 2},
    ),
    (
        "security",
        "Cybersecurity / PenTesting",
        Spec(
            "8 core CPU",
            32,
            "1TB SSD",
            "Optional / entry GPU",
            "RAM & cores for many tools / VMs.",
        ),
        {"cores": 8, "ram": 32, "storage": 1000, "gpu_rank": 2},
    ),
    (
        "office_plus",
        "Heavy Productivity (Many Tabs)",
        Spec(
            "6 core CPU",
            32,
            "1TB SSD",
            "Integrated",
            "Extra RAM keeps multitasking smooth.",
        ),
        {"cores": 6, "ram": 32, "storage": 1000, "gpu_rank": 1},
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
        {"cores": 4, "ram": 8, "storage": 512, "gpu_rank": 1},
    ),
    (
        "homelab",
        "Home Lab / NAS",
        Spec(
            "8-12 core CPU",
            32,
            "4TB+ mixed SSD/HDD",
            "Optional",
            "Consider ECC RAM & redundancy.",
        ),
        {"cores": 12, "ram": 32, "storage": 4000, "gpu_rank": 1},
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
        {"cores": 12, "ram": 64, "storage": 2000, "gpu_rank": 1},
    ),
    (
        "budget",
        "Entry Level / Budget",
        Spec(
            "4-6 core CPU",
            16,
            "512GB SSD",
            "Integrated or basic GPU",
            "Aim for balance; upgrade later.",
        ),
        {"cores": 6, "ram": 16, "storage": 512, "gpu_rank": 1},
    ),
]
DEFAULT = Spec(
    "4-6 core CPU",
    16,
    "512GB SSD",
    "Integrated or basic GPU",
    "Default balanced build.",
)

# Pre-computed dict for quick lookup
_RULE_INDEX: Dict[str, tuple] = {wid: r for r in RULES for wid in [r[0]]}

# Optional explicit combination overrides (frozenset of ids -> Spec)
COMBO_RULES: Dict[frozenset, Spec] = {
    frozenset(["gaming", "stream"]): Spec(
        "8+ core high clock CPU",
        32,
        "1TB NVMe SSD",
        "High-mid GPU (e.g., RTX 4070)",
        "Streaming + gaming benefits from extra threads & RAM.",
    ),
    frozenset(["ml", "server"]): Spec(
        "16+ core CPU",
        128,
        "2TB NVMe SSD",
        "High-end NVIDIA (e.g., RTX 4090)",
        "Combine ML training with virtualization headroom.",
    ),
    frozenset(["gaming", "vr"]): Spec(
        "8+ core high clock CPU",
        32,
        "1TB NVMe SSD",
        "High-mid GPU (High refresh capable)",
        "VR adds latency + frame rate pressure over gaming.",
    ),
}


GPU_RANK_LABEL = {
    1: "Integrated",
    2: "Entry GPU (e.g., GTX 1650)",
    3: "Mid GPU (e.g., RTX 3050/3060)",
    4: "Mid-High GPU (e.g., RTX 3070/4070)",
    5: "High-End GPU (e.g., RTX 4080/4090)",
    6: "High-End Multi-GPU / Pro",
}


def _scale_cpu(cores: int) -> str:
    if cores >= 16:
        return "16+ core modern CPU"
    if cores >= 12:
        return "12+ core modern CPU"
    if cores >= 8:
        return "8 core high clock CPU"
    if cores >= 6:
        return "6 core CPU"
    return "4 core CPU"


def _scale_storage(gb: int) -> str:
    if gb >= 4000:
        return "4TB+ mixed SSD/HDD"
    if gb >= 2000:
        return "2TB NVMe SSD"
    if gb >= 1000:
        return "1TB NVMe SSD"
    if gb >= 512:
        return "512GB SSD"
    return "256-512GB SSD"


def recommend(ids: List[str]) -> Spec:
    """Return a Spec for the (possibly multiple) selected workload ids.

    Logic order (all are stateless reflex steps):
      1. If none selected -> DEFAULT.
      2. If exact combo override exists -> use it.
      3. If single workload -> its base spec.
      4. Else aggregate: take maxima of numeric meta & merge notes.
    """
    if not ids:
        return DEFAULT
    fs = frozenset(ids)
    if fs in COMBO_RULES:
        return COMBO_RULES[fs]
    if len(ids) == 1:
        return _RULE_INDEX[ids[0]][2]
    # Aggregate numeric maxima
    metas = [_RULE_INDEX[i][3] for i in ids if i in _RULE_INDEX]
    if not metas:
        return DEFAULT
    max_cores = max(m["cores"] for m in metas)
    max_ram = max(m["ram"] for m in metas)
    max_storage = max(m["storage"] for m in metas)
    max_gpu = max(m["gpu_rank"] for m in metas)
    # Merge unique notes (short)
    note_parts = []
    seen = set()
    for i in ids:
        note = _RULE_INDEX[i][2].notes
        key = note.split('.')[0]
        if key not in seen:
            seen.add(key)
            note_parts.append(note)
    notes = " | ".join(note_parts[:4])  # cap to avoid very long text
    return Spec(
        cpu=_scale_cpu(max_cores),
        ram_gb=max_ram,
        storage=_scale_storage(max_storage),
        gpu=GPU_RANK_LABEL[max_gpu],
        notes=notes,
    )
    


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hardware Recommender")
        # Dynamic height based on number of workloads (rough heuristic)
        base_h = 300 + 20 * len(RULES)
        self.geometry(f"600x{min(base_h, 760)}")
        self.vars: Dict[str, tk.BooleanVar] = {}
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
        for i, (wid, label, _spec, _meta) in enumerate(RULES):
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
        for v in self.vars.values():
            v.set(False)
        self._out("")

    def on_recommend(self):
        ids = [wid for wid, v in self.vars.items() if v.get()]
        spec = recommend(ids)
        labels = [l for wid, l, _s, _m in RULES if wid in ids]
        wl = ", ".join(labels) if labels else "(none)"
        self._out(
            f"Workloads: {wl}\n\nCPU: {spec.cpu}\nRAM: {spec.ram_gb} GB\nStorage: {spec.storage}\nGPU: {spec.gpu}\nNotes: {spec.notes}"
        )

    def _out(self, text: str):
        self.out.configure(state="normal")
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, text)
        self.out.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()
