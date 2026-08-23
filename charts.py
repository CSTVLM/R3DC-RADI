#!/usr/bin/env python3
"""Generate inline SVG figures for the R3DC project page.

Every data point below is transcribed from the manuscript (Tables 6, 9, 10,
11, 12, 14, 24). Colours are emitted as CSS custom properties so the figures
re-theme automatically inside the inverted section.
"""
import math, os, json

OUT = "/home/claude/site/parts"
os.makedirs(OUT, exist_ok=True)

INK, MUT, FAINT = "var(--ink)", "var(--ink-soft)", "var(--ink-faint)"
RULE, PAPER = "var(--rule)", "var(--paper)"
TRUST, DOUBT = "var(--trust)", "var(--doubt)"
MONO = "IBM Plex Mono, ui-monospace, monospace"


def svg(w, h, body, label=""):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="{label}" class="chart">{body}</svg>')


def txt(x, y, s, size=11, fill=MUT, anchor="start", weight=400, family=MONO, ls=".04em"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" '
            f'letter-spacing="{ls}">{s}</text>')


def line(x1, y1, x2, y2, stroke=RULE, w=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>')


def rect(x, y, w, h, fill, op=1, rx=0):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" opacity="{op}" rx="{rx}"/>'


def poly(pts, stroke, w=2, fill="none", dash=None):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"{d}/>')


def circ(x, y, r, fill, stroke="none", sw=0):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def diamond(x, y, r, fill, stroke="none", sw=0):
    return (f'<path d="M {x:.1f} {y-r:.1f} L {x+r:.1f} {y:.1f} L {x:.1f} {y+r:.1f} '
            f'L {x-r:.1f} {y:.1f} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


CH = {}

# ---------------------------------------------------------------- Fig: params vs RMSE
W, H = 780, 450
L, R, T, B = 66, 24, 30, 54
xl, xr = math.log10(1.4), math.log10(220)
ylo, yhi = 600, 810


def fx(v):
    return L + (math.log10(v) - xl) / (xr - xl) * (W - L - R)


def fy(v):
    return T + (v - ylo) / (yhi - ylo) * (H - T - B)


b = []
for gy in range(600, 811, 50):
    b.append(line(L, fy(gy), W - R, fy(gy), RULE, 1, "2 4" if gy not in (600, 800) else None))
    b.append(txt(L - 10, fy(gy) + 4, str(gy), 10.5, FAINT, "end"))
for gx in (2, 5, 10, 20, 50, 100, 200):
    b.append(txt(fx(gx), H - B + 20, str(gx), 10.5, FAINT, "middle"))
b.append(line(L, fy(810), W - R, fy(810), INK, 1))
b.append(txt(L - 10, T - 12, "KITTI RMSE (mm)", 10.5, FAINT, "start"))
b.append(txt(W - R, H - B + 40, "parameters (M, log scale)", 10.5, FAINT, "end"))

pts = [
    ("CSPN++", 17.4, 743.7, -11, -9, "end", 0),
    ("NLSPN", 26.8, 741.7, 11, 4, "start", 0),
    ("PENet", 131.0, 730.1, -11, -9, "end", 0),
    ("DynFusion", 31.1, 641.5, 11, 4, "start", 0),
    ("GuideFormer", 27.3, 625.4, 11, 4, "start", 0),
    ("CompletionFormer", 12.7, 708.2, -11, 2, "end", 0),
    ("BP-Net", 30.4, 671.3, 11, 4, "start", 0),
    ("R³DC", 1.95, 786.4, 12, 5, "start", 1),
    ("R³DC+", 11.22, 729.1, -12, 19, "end", 1),
]
# shaded band: the parameter region no competing method reaches
b.append(rect(fx(1.4), T, fx(11.5) - fx(1.4), H - T - B, TRUST, .06))
b.append(txt(fx(1.5) + 6, T + 18, "no competing method", 9.5, TRUST, "start"))
b.append(txt(fx(1.5) + 6, T + 31, "operates below 12 M", 9.5, TRUST, "start"))

for name, p, r, dx, dy, an, ours in pts:
    x, y = fx(p), fy(r)
    if ours:
        b.append(diamond(x, y, 7, TRUST))
        b.append(txt(x + dx, y + dy, name, 12, TRUST, an, 600))
    else:
        b.append(circ(x, y, 5, PAPER, MUT, 1.6))
        b.append(txt(x + dx, y + dy, name, 11, MUT, an))
CH["FIG_PARAMS"] = svg(W, H, "".join(b), "KITTI RMSE against parameter count")

# ---------------------------------------------------------------- Fig: REC vs latency
W, H = 780, 400
L, R, T, B = 66, 24, 30, 56
xl, xr = math.log10(35), math.log10(1500)
ylo, yhi = 0.40, 0.10
fx = lambda v: L + (math.log10(v) - xl) / (xr - xl) * (W - L - R)
fy = lambda v: T + (v - ylo) / (yhi - ylo) * (H - T - B)
b = []
b.append(rect(fx(100), T, W - R - fx(100), H - T - B, DOUBT, .05))
b.append(line(fx(100), T, fx(100), H - B, DOUBT, 1, "3 3"))
b.append(txt(fx(105), T + 16, "beyond a 10 fps budget", 9.5, DOUBT, "start"))
for gy in (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40):
    b.append(line(L, fy(gy), W - R, fy(gy), RULE, 1, "2 4"))
    b.append(txt(L - 10, fy(gy) + 4, f"{gy:.2f}", 10.5, FAINT, "end"))
for gx in (50, 100, 200, 500, 1000):
    b.append(txt(fx(gx), H - B + 20, str(gx), 10.5, FAINT, "middle"))
b.append(txt(L - 10, T - 12, "REC (Spearman ρ)", 10.5, FAINT, "start"))
b.append(txt(W - R, H - B + 40, "latency per frame (ms, log scale)", 10.5, FAINT, "end"))

lat = [("Inverse-gradient", 50, 0.147, 5, 0, -12, 4, "end"),
       ("Depth-error proxy", 50, 0.214, 5, 0, -12, 4, "end"),
       ("MC dropout, 20×", 1008, 0.271, 5, 0, -12, -12, "end"),
       ("Deep ensemble, 3×", 151, 0.303, 8, 1, 14, 4, "start"),
       ("Learned R̂, 1×", 50.4, 0.371, 7, 2, 14, 4, "start")]
for name, x0, y0, r, kind, dx, dy, an in lat:
    x, y = fx(x0), fy(y0)
    if kind == 2:
        b.append(diamond(x, y, r + 1, TRUST))
        b.append(txt(x + dx, y + dy, name, 12, TRUST, an, 600))
    else:
        if kind == 1:
            b.append(circ(x, y, r + 3, MUT, "none"))
            b.append(circ(x, y, r + 3, "none", MUT, 1))
        b.append(circ(x, y, r, PAPER, MUT, 1.6))
        b.append(txt(x + dx, y + dy, name, 11, MUT, an))
b.append(txt(L, H - 12, "marker size encodes weight memory · single Tesla T4, 352×1216",
             9.5, FAINT, "start"))
CH["FIG_LATENCY"] = svg(W, H, "".join(b), "REC against inference latency")

# ---------------------------------------------------------------- Fig: REC by region, grouped
W, H = 780, 430
L, R, T, B = 66, 24, 26, 96
b = []
srcs = [("Uniform", [0.000, 0.000, 0.000], 0), ("Inverse-grad.", [0.147, 0.131, 0.169], 0),
        ("Error proxy", [0.214, 0.198, 0.231], 0), ("MC dropout", [0.271, 0.249, 0.292], 0),
        ("Deep ensemble", [0.303, 0.281, 0.319], 0), ("Learned R̂", [0.371, 0.358, 0.389], 1)]
regions = ["all", "edge", "textureless"]
ymax = 0.42
fy = lambda v: (H - B) - v / ymax * (H - T - B)
gw = (W - L - R) / len(srcs)
bw = gw * 0.21
for gy in [0, .1, .2, .3, .4]:
    b.append(line(L, fy(gy), W - R, fy(gy), RULE if gy else INK, 1, "2 4" if gy else None))
    b.append(txt(L - 10, fy(gy) + 4, f"{gy:.1f}", 10.5, FAINT, "end"))
b.append(txt(L - 10, T - 8, "REC (Spearman ρ) by evaluation region", 10.5, FAINT, "start"))
for i, (name, vals, ours) in enumerate(srcs):
    gx = L + i * gw + gw / 2
    for j, v in enumerate(vals):
        x = gx + (j - 1) * (bw + 5) - bw / 2
        col = TRUST if ours else MUT
        op = [1, .72, .48][j] if ours else [.62, .44, .28][j]
        h = max(1.5, (H - B) - fy(v))
        b.append(rect(x, fy(v), bw, h, col, op))
        if ours:
            b.append(txt(x + bw / 2, fy(v) - 7, f"{v:.3f}", 9.5, TRUST, "middle", 600))
    b.append(txt(gx, H - B + 20, name, 11, TRUST if ours else MUT, "middle",
                 600 if ours else 400, family="Source Serif 4, serif", ls="0"))
lx = L
for j, rname in enumerate(regions):
    b.append(rect(lx, H - 44, 13, 10, TRUST, [1, .72, .48][j]))
    b.append(txt(lx + 19, H - 35, rname, 10.5, FAINT, "start"))
    lx += 26 + len(rname) * 7
CH["FIG_REGION"] = svg(W, H, "".join(b), "REC by region for six reliability sources")

# ---------------------------------------------------------------- Fig: CAL bars
W, H = 780, 380
L, R, T, B = 176, 78, 34, 54
b = []
cal = [("Uniform (≡0.5)", 0.248, "0%", 0), ("Inverse-gradient", 0.183, "0%", 0),
       ("Depth-error proxy", 0.142, "0%", 0), ("MC dropout, 20×", 0.118, "0%", 0),
       ("Deep ensemble, 3×", 0.097, "0%", 0), ("Learned R̂, 1×", 0.041, "41.3%", 1)]
xmax = 0.27
fx = lambda v: L + v / xmax * (W - L - R)
rh = (H - T - B) / len(cal)
b.append(line(fx(0.248), T - 8, fx(0.248), H - B + 4, DOUBT, 1, "3 3"))
b.append(txt(fx(0.248), T - 14, "random predictor", 9.5, DOUBT, "middle"))
for i, (name, v, rbs, ours) in enumerate(cal):
    y = T + i * rh + rh * 0.22
    h = rh * 0.5
    b.append(rect(L, y, max(2, fx(v) - L), h, TRUST if ours else MUT, 1 if ours else .42, 1))
    b.append(txt(L - 12, y + h / 2 + 4, name, 11.5, TRUST if ours else MUT, "end",
                 600 if ours else 400, family="Source Serif 4, serif", ls="0"))
    b.append(txt(fx(v) + 8, y + h / 2 + 4, f"{v:.3f}", 11, TRUST if ours else FAINT, "start",
                 600 if ours else 400))
    b.append(txt(W - 6, y + h / 2 + 4, "RBS " + rbs, 10, TRUST if ours else FAINT, "end",
                 600 if ours else 400))
b.append(line(L, H - B + 4, W - R, H - B + 4, INK, 1))
for gx in [0, .05, .10, .15, .20, .25]:
    b.append(txt(fx(gx), H - B + 22, f"{gx:.2f}", 10.5, FAINT, "middle"))
b.append(txt(L, H - 12, "CAL — expected calibration error, 15 bins, τ = 0.10. Lower is better.",
             9.5, FAINT, "start"))
CH["FIG_CAL"] = svg(W, H, "".join(b), "Calibration error across reliability sources")

# ---------------------------------------------------------------- Fig: dumbbell D0 -> D1
W, H = 780, 360
L, R, T, B = 130, 150, 40, 52
b = []
rows = [("all", 0.601, 0.353, 41.3, 0.371), ("edge", 0.643, 0.388, 39.7, 0.358),
        ("textureless", 0.557, 0.319, 42.7, 0.389), ("far-depth", 0.714, 0.431, 39.6, 0.341)]
xlo, xhi = 0.28, 0.76
fx = lambda v: L + (v - xlo) / (xhi - xlo) * (W - L - R)
rh = (H - T - B) / len(rows)
b.append(txt(L, T - 18, "coarse D₀", 10, DOUBT, "start", 600))
b.append(txt(W - R, T - 18, "refined D₁ · RBS · REC", 10, TRUST, "end", 600))
for gx in [0.3, 0.4, 0.5, 0.6, 0.7]:
    b.append(line(fx(gx), T - 6, fx(gx), H - B, RULE, 1, "2 4"))
    b.append(txt(fx(gx), H - B + 20, f"{gx:.1f}", 10.5, FAINT, "middle"))
b.append(txt(W - R, H - B + 38, "RMSE (m) · NYU Depth V2, metric space", 10.5, FAINT, "end"))
for i, (name, d0, d1, rbs, rec) in enumerate(rows):
    y = T + i * rh + rh / 2
    b.append(txt(L - 14, y + 4, name, 12.5, INK, "end", 600, family="Source Serif 4, serif", ls="0"))
    b.append(line(fx(d1), y, fx(d0), y, MUT, 2.5))
    b.append(circ(fx(d0), y, 6, PAPER, DOUBT, 2))
    b.append(txt(fx(d0) + 12, y + 4, f"{d0:.3f}", 10.5, DOUBT, "start"))
    b.append(circ(fx(d1), y, 6.5, TRUST))
    b.append(txt(fx(d1) - 12, y + 4, f"{d1:.3f}", 10.5, TRUST, "end", 600))
    b.append(txt(W - 88, y + 4, f"−{rbs:.1f}%", 12, TRUST, "start", 600))
    b.append(txt(W - 6, y + 4, f"REC +{rec:.3f}", 10.5, FAINT, "end"))
CH["FIG_DUMBBELL"] = svg(W, H, "".join(b), "Coarse to refined RMSE by region")

# ---------------------------------------------------------------- Fig: sparsity robustness
W, H = 780, 400
L, R, T, B = 62, 66, 32, 60
dens = [0.5, 1, 2, 5, 10, 50]
rmse = [2.31, 1.82, 1.43, 0.92, 0.73, 0.56]
d1s = [0.41, 0.53, 0.64, 0.77, 0.84, 0.91]
xl, xr = math.log10(0.42), math.log10(62)
fx = lambda v: L + (math.log10(v) - xl) / (xr - xl) * (W - L - R)
fyl = lambda v: T + (2.5 - v) / (2.5 - 0.4) * (H - T - B)
fyr = lambda v: T + (0.95 - v) / (0.95 - 0.35) * (H - T - B)
b = []
b.append(rect(L, T, fx(1) - L, H - T - B, DOUBT, .06))
b.append(txt(L + 6, H - B - 10, "δ₁ < 0.53 — inferring, not completing", 9.5, DOUBT, "start"))
for gy in [0.5, 1.0, 1.5, 2.0, 2.5]:
    b.append(line(L, fyl(gy), W - R, fyl(gy), RULE, 1, "2 4"))
    b.append(txt(L - 10, fyl(gy) + 4, f"{gy:.1f}", 10.5, FAINT, "end"))
for gy in [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    b.append(txt(W - R + 10, fyr(gy) + 4, f"{gy:.1f}", 10.5, TRUST, "start"))
b.append(line(fx(2.5), T, fx(2.5), H - B, INK, 1, "4 3"))
b.append(txt(fx(2.5) + 7, T + 14, "training density", 9.5, INK, "start"))
for d in dens:
    b.append(txt(fx(d), H - B + 20, f"{d:g}%", 10.5, FAINT, "middle"))
b.append(poly([(fx(d), fyl(v)) for d, v in zip(dens, rmse)], DOUBT, 2.2))
b.append(poly([(fx(d), fyr(v)) for d, v in zip(dens, d1s)], TRUST, 2.2))
for d, v in zip(dens, rmse):
    b.append(circ(fx(d), fyl(v), 4, PAPER, DOUBT, 2))
for d, v in zip(dens, d1s):
    b.append(circ(fx(d), fyr(v), 4, TRUST))
b.append(txt(L - 10, T - 12, "RMSE (m)", 10.5, DOUBT, "start", 600))
b.append(txt(W - R + 10, T - 12, "δ₁", 10.5, TRUST, "start", 600))
b.append(txt(W - R, H - 12, "evaluation anchor density · fixed Drone-Videos checkpoint", 9.5, FAINT, "end"))
CH["FIG_SPARSITY"] = svg(W, H, "".join(b), "Robustness to anchor density")

# ---------------------------------------------------------------- Fig: ablation deltas
W, H = 780, 470
L, R, T, B = 210, 60, 30, 46
abl = [("RGB only, single stream", 0.138, 1), ("depth only, single stream", 0.101, 1),
       ("no CSPN++ refinement", 0.071, 0), ("no cross-modal attention", 0.053, 0),
       ("dual stream, no CMA", 0.050, 1), ("no deformable conv.", 0.033, 0),
       ("no transformer bottleneck", 0.021, 0), ("no EMA at inference", 0.018, 0),
       ("no CBAM", 0.011, 0), ("no DropPath", 0.007, 0)]
xmax = 0.15
fx = lambda v: L + v / xmax * (W - L - R)
rh = (H - T - B) / len(abl)
b = []
b.append(line(L, T - 6, L, H - B, INK, 1))
b.append(txt(L - 12, T - 14, "full model · 0.240 m", 10, TRUST, "end", 600))
for gx in [0.05, 0.10, 0.15]:
    b.append(line(fx(gx), T - 6, fx(gx), H - B, RULE, 1, "2 4"))
    b.append(txt(fx(gx), H - B + 20, f"+{gx:.2f}", 10.5, FAINT, "middle"))
for i, (name, v, alt) in enumerate(abl):
    y = T + i * rh + rh * 0.24
    h = rh * 0.52
    b.append(rect(L, y, max(2, fx(v) - L), h, DOUBT, .78 if not alt else .38, 1))
    b.append(txt(L - 12, y + h / 2 + 4, name, 12, MUT, "end",
                 family="Source Serif 4, serif", ls="0"))
    b.append(txt(fx(v) + 9, y + h / 2 + 4, f"{v:.3f}", 10.5, FAINT, "start"))
b.append(txt(W - R, H - 10, "Δ validation RMSE (m) · KITTI-uni, epoch 8", 9.5, FAINT, "end"))
b.append(rect(L, H - 24, 12, 9, DOUBT, .78))
b.append(txt(L + 18, H - 16, "component removed", 9.5, FAINT, "start"))
b.append(rect(L + 150, H - 24, 12, 9, DOUBT, .38))
b.append(txt(L + 168, H - 16, "encoder configuration", 9.5, FAINT, "start"))
CH["FIG_ABLATION"] = svg(W, H, "".join(b), "Architecture ablation deltas")

# ---------------------------------------------------------------- Fig: propagation steps
W, H = 380, 250
L, R, T, B = 54, 20, 26, 44
steps = [(1, 0.263), (3, 0.252), (6, 0.240), (9, 0.241)]
fx = lambda v: L + (v - 0) / 10 * (W - L - R)
fy = lambda v: T + (0.270 - v) / (0.270 - 0.234) * (H - T - B)
b = []
for gy in [0.240, 0.250, 0.260, 0.270]:
    b.append(line(L, fy(gy), W - R, fy(gy), RULE, 1, "2 4"))
    b.append(txt(L - 8, fy(gy) + 4, f"{gy:.3f}", 9.5, FAINT, "end"))
b.append(poly([(fx(t), fy(v)) for t, v in steps], MUT, 2))
for t, v in steps:
    best = (t == 6)
    b.append(circ(fx(t), fy(v), 5 if best else 4, TRUST if best else PAPER, MUT if not best else "none", 2))
    b.append(txt(fx(t), H - B + 18, f"T={t}", 9.5, TRUST if best else FAINT, "middle", 600 if best else 400))
b.append(txt(L, T - 10, "val RMSE (m)", 9.5, FAINT, "start"))
b.append(txt(W - R, H - 10, "returns saturate at six steps", 9.5, FAINT, "end"))
CH["FIG_STEPS"] = svg(W, H, "".join(b), "Effect of propagation step count")

# ---------------------------------------------------------------- Fig: REC inversion (two panels)
epochs = list(range(1, 21))
rec = [-0.350, -0.411, -0.447, -0.498, -0.508, -0.330, -0.105, -0.252, -0.267, -0.169,
       -0.348, -0.224, -0.277, -0.289, -0.277, -0.217, -0.258, -0.149, -0.241, -0.187]
vrmse = [15.49, 13.93, 12.35, 13.05, 11.27, 8.11, 5.72, 4.56, 4.44, 3.31,
         7.82, 3.68, 4.44, 5.09, 5.27, 5.00, 4.61, 2.33, 3.59, 3.28]

W, H = 780, 340
L, R, T, B = 60, 24, 30, 52
fx = lambda v: L + (v - 1) / 19 * (W - L - R)
fy = lambda v: T + (0.02 - v) / (0.02 + 0.56) * (H - T - B)
b = [rect(L, fy(0), W - L - R, fy(-0.56) - fy(0), DOUBT, .07)]
for gy in [0, -0.1, -0.2, -0.3, -0.4, -0.5]:
    b.append(line(L, fy(gy), W - R, fy(gy), INK if gy == 0 else RULE, 1, None if gy == 0 else "2 4"))
    b.append(txt(L - 10, fy(gy) + 4, f"{gy:+.1f}" if gy else "0.0", 10.5, FAINT, "end"))
for e in (1, 5, 10, 15, 20):
    b.append(txt(fx(e), H - B + 20, str(e), 10.5, FAINT, "middle"))
b.append(poly([(fx(e), fy(v)) for e, v in zip(epochs, rec)], DOUBT, 2))
for e, v in zip(epochs, rec):
    b.append(circ(fx(e), fy(v), 3.4, DOUBT))
b.append(circ(fx(18), fy(-0.149), 8, "none", TRUST, 2))
b.append(txt(fx(18) - 10, fy(-0.149) - 14, "best ckpt · −0.149", 10, TRUST, "end", 600))
b.append(txt(fx(5) + 10, fy(-0.508) + 16, "worst · −0.508", 10, DOUBT, "start"))
b.append(txt(L - 10, T - 12, "REC (Spearman ρ) — VisDrone, synthetic ground truth", 10.5, FAINT, "start"))
b.append(txt(W - R, H - B + 40, "training epoch", 10.5, FAINT, "end"))
b.append(txt(L + 8, fy(-0.03) + 14, "inverted region", 9.5, DOUBT, "start"))
CH["FIG_INV_A"] = svg(W, H, "".join(b), "REC per epoch on VisDrone")

W, H = 780, 340
L, R, T, B = 60, 24, 30, 52
fx = lambda v: L + (v - 1.5) / (16.5 - 1.5) * (W - L - R)
fy = lambda v: T + (0.02 - v) / (0.02 + 0.56) * (H - T - B)
b = []
for gy in [0, -0.1, -0.2, -0.3, -0.4, -0.5]:
    b.append(line(L, fy(gy), W - R, fy(gy), INK if gy == 0 else RULE, 1, None if gy == 0 else "2 4"))
    b.append(txt(L - 10, fy(gy) + 4, f"{gy:+.1f}" if gy else "0.0", 10.5, FAINT, "end"))
for gx in (2, 4, 6, 8, 10, 12, 14, 16):
    b.append(txt(fx(gx), H - B + 20, str(gx), 10.5, FAINT, "middle"))
n = len(vrmse)
mx, my = sum(vrmse) / n, sum(rec) / n
sxy = sum((a - mx) * (c - my) for a, c in zip(vrmse, rec))
sxx = sum((a - mx) ** 2 for a in vrmse)
sl = sxy / sxx
b.append(poly([(fx(1.8), fy(my + sl * (1.8 - mx))), (fx(16.2), fy(my + sl * (16.2 - mx)))],
              INK, 1.4, dash="5 4"))
for i, (a, c) in enumerate(zip(vrmse, rec)):
    t = i / (n - 1)
    b.append(circ(fx(a), fy(c), 5, DOUBT, PAPER, 1.2))
    b.append(circ(fx(a), fy(c), 5, "none", TRUST, 0))
b.append(txt(W - R - 8, T + 18, "Pearson r = −0.82", 11, INK, "end", 600))
b.append(txt(L - 10, T - 12, "REC (Spearman ρ)", 10.5, FAINT, "start"))
b.append(txt(W - R, H - B + 40, "validation RMSE (m) — the fit improves leftward", 10.5, FAINT, "end"))
CH["FIG_INV_B"] = svg(W, H, "".join(b), "REC against validation RMSE")

for k, v in CH.items():
    open(os.path.join(OUT, k + ".svg"), "w", encoding="utf-8").write(v)
print(json.dumps({k: len(v) for k, v in CH.items()}, indent=0))
