"""Single-file hardware recommender GUI (checkbox -> spec)."""

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
from typing import List, Dict
import platform
import textwrap


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
    """Minimal, cleaner UI for workload selection & spec output."""

    def __init__(self):
        super().__init__()
        self.title("Hardware Recommender")
        self.minsize(640, 520)
        self.geometry("720x560")
        if platform.system() == "Windows":
            try:
                self.iconbitmap(default="")  # no external icon; keep minimal
            except Exception:
                pass
        self.vars: Dict[str, tk.BooleanVar] = {}
        self._configure_style()
        self._build()
        self.bind("<Return>", lambda _e: self.on_recommend())
        self.bind("<Control-l>", lambda _e: self.on_clear())
        self.bind("<Control-r>", lambda _e: self.on_recommend())

    # ---------------- UI construction -----------------
    def _configure_style(self):
        style = ttk.Style(self)
        # Use a platform neutral theme with modern-ish look
        preferred = "clam"
        if preferred in style.theme_names():
            style.theme_use(preferred)
        style.configure("TLabel", padding=(0, 2))
        style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Status.TLabel", foreground="#555")
        style.configure("Outlined.TFrame", borderwidth=1, relief="solid")
        style.map(
            "TCheckbutton",
            background=[("active", "#eef"), ("selected", "#eef")],
        )

    def _build(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=12, pady=10)

        # Header
        ttk.Label(container, text="Hardware Recommender", style="Heading.TLabel").pack(
            anchor="w"
        )
        sub = (
            "Select the workloads you care about. Recommendations update automatically."
        )
        ttk.Label(container, text=sub, wraplength=640).pack(anchor="w", pady=(0, 6))

        body = ttk.Frame(container)
        body.pack(fill="both", expand=True)

        # Left: workload selection (scrollable)
        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=(0, 12))

        ttk.Label(left, text="Workloads:").pack(anchor="w")
        scroll_frame = self._scrollable_checkbox_frame(left, height=270)
        self._populate_workloads(scroll_frame.inner)

        btn_bar = ttk.Frame(left)
        btn_bar.pack(fill="x", pady=(6, 0))
        ttk.Button(btn_bar, text="Recommend", command=self.on_recommend).pack(
            side="left"
        )
        ttk.Button(btn_bar, text="Clear", command=self.on_clear).pack(
            side="left", padx=4
        )
        ttk.Button(btn_bar, text="Copy", command=self.on_copy).pack(side="left")

        self.status_var = tk.StringVar(value="0 selected")
        ttk.Label(left, textvariable=self.status_var, style="Status.TLabel").pack(
            anchor="w", pady=(4, 0)
        )

        # Right: output panel
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True)
        ttk.Label(right, text="Suggested Spec:").pack(anchor="w")
        self.out = tk.Text(
            right,
            height=14,
            wrap="word",
            state="disabled",
            background="#f5f6f7",
            relief="flat",
            padx=8,
            pady=6,
        )
        self.out.pack(fill="both", expand=True, pady=(2, 0))

        self._update_output_live()  # initial default

    # ---------------- workload list helpers -----------------
    def _scrollable_checkbox_frame(self, parent, height=260):
        outer = ttk.Frame(parent)
        outer.pack(fill="y", expand=False)
        canvas = tk.Canvas(outer, borderwidth=0, height=height, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_config(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner.bind("<Configure>", _on_inner_config)
        # Basic mousewheel support
        def _wheel(evt):
            delta = -1 * (evt.delta // 120 if evt.delta else (1 if evt.num == 5 else -1))
            canvas.yview_scroll(delta, "units")

        canvas.bind_all("<MouseWheel>", _wheel)
        # Simple named object with attributes for clarity
        class _ScrollFrame:
            def __init__(self, outer, inner):
                self.outer = outer
                self.inner = inner

        return _ScrollFrame(outer, inner)

    def _populate_workloads(self, parent):
        # Two-column grid inside scroll area (responsive) keeping minimalistic look
        cols = 1 if len(RULES) <= 10 else 2
        for idx, (wid, label, _spec, _meta) in enumerate(RULES):
            v = tk.BooleanVar(value=False)
            self.vars[wid] = v
            cb = ttk.Checkbutton(parent, text=label, variable=v, command=self._update_output_live)
            r = idx // cols
            c = idx % cols
            cb.grid(row=r, column=c, sticky="w", padx=(0, 12), pady=1)
        for c in range(cols):
            parent.grid_columnconfigure(c, weight=1)

    # ---------------- status & output -----------------
    def _update_status(self):
        count = sum(1 for v in self.vars.values() if v.get())
        self.status_var.set(f"{count} selected")

    def _format_spec(self, ids, spec: Spec) -> str:
        labels = [l for wid, l, _s, _m in RULES if wid in ids]
        wl = ", ".join(labels) if labels else "(none)"
        notes = textwrap.fill(spec.notes, width=76) if spec.notes else ""
        return (
            f"Workloads: {wl}\n"
            f"CPU      : {spec.cpu}\n"
            f"RAM      : {spec.ram_gb} GB\n"
            f"Storage  : {spec.storage}\n"
            f"GPU      : {spec.gpu}\n"
            f"Notes    : {notes}"
        )

    def _update_output_live(self):
        self._update_status()
        self.on_recommend(auto=True)

    # ---------------- actions -----------------
    def on_clear(self):
        for v in self.vars.values():
            v.set(False)
        self._update_output_live()

    def on_recommend(self, auto: bool = False):
        ids = [wid for wid, v in self.vars.items() if v.get()]
        spec = recommend(ids)
        text = self._format_spec(ids, spec)
        prefix = "" if auto else ""  # reserved for future labels
        self._out(prefix + text)

    def on_copy(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.out.get("1.0", tk.END).strip())
        except Exception:
            pass

    def _out(self, text: str):
        self.out.configure(state="normal")
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, text)
        self.out.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()
