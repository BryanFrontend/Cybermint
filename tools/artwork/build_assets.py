"""Generate the Cybermint repository artwork into docs/assets/.

Usage: python3 tools/artwork/build_assets.py docs/assets tools/artwork/logo-layers.json [name ...]
Names: logo hero status dividers fee shield lifecycle arch (default: all).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import svgkit
from svgkit import (Doc, GRAY, GRAY_D, INK, LINE, MINT, MINT_D, PALE, PANEL, PANEL2, WHITE)

OUT = sys.argv[1]
svgkit.LOGO_JSON = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
only = set(sys.argv[3:])


def want(name):
    return not only or name in only


def reeded_ring(d, cx, cy, r, n=180, inner=10, stroke=LINE, sw=2, opacity=None):
    parts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x1, y1 = cx + r * math.cos(a), cy + r * math.sin(a)
        x2, y2 = cx + (r - inner) * math.cos(a), cy + (r - inner) * math.sin(a)
        parts.append(f"M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}")
    d.path("".join(parts), stroke=stroke, sw=sw, opacity=opacity)


def panel(d, title_eyebrow, heading, sub=None):
    d.rect(0, 0, d.w, d.h, 28, fill=INK)
    # fine blueprint grid
    g = []
    for x in range(40, d.w, 40):
        g.append(f"M{x} 0V{d.h}")
    for y in range(40, d.h, 40):
        g.append(f"M0 {y}H{d.w}")
    d.add(f'<path d="{"".join(g)}" stroke="#15171A" stroke-width="1"/>')
    d.rect(0, 0, d.w, d.h, 28, fill="none", stroke=LINE, sw=2)
    d.rect(70, 62, 14, 14, 3, fill=MINT)
    d.text(title_eyebrow, 98, 76, 17, "monob", MINT, track=2.5)
    d.text(heading, 70, 134, 46, "xbold", WHITE, track=-0.5)
    if sub:
        d.text(sub, d.w - 70, 76, 18, "mono", GRAY, anchor="end", track=0.5)


def chip(d, x, y, label, kind, h=34, size=14):
    """State chip. kind: done, planned, external, verified, pending, notenabled, failed, unknown."""
    w = d.measure(label, size, "monob", 1.2) + 30
    styles = {
        "done": (MINT, INK, None, None),
        "verified": (MINT, INK, None, None),
        "planned": ("none", WHITE, WHITE, "6 5"),
        "pending": ("none", PALE, PALE, None),
        "external": (PANEL2, PALE, GRAY_D, None),
        "notenabled": (GRAY_D, WHITE, None, None),
        "failed": (WHITE, INK, None, None),
        "unknown": (INK, WHITE, GRAY, "3 4"),
        "planned_l": ("none", INK, INK, "6 5"),
        "external_l": ("#DDF7EE", INK, MINT_D, None),
    }
    fill, tc, stroke, dash = styles[kind]
    d.rect(x, y, w, h, h / 2, fill=fill, stroke=stroke, sw=2 if stroke else 0, dash=dash)
    d.text(label, x + 15, y + h / 2 + size * 0.36, size, "monob", tc, track=1.2)
    return w


# ------------------------------------------------------------------ logo
if want("logo"):
    d = Doc(512, 512, "Cybermint logo", "A chunky mint green cent-style C with a black outline and a hard green offset shadow.")
    d.logo(256, 256, 470)
    d.save(f"{OUT}/cybermint-logo.svg")

# ------------------------------------------------------------------ hero
if want("hero"):
    W, H = 1600, 720
    d = Doc(W, H, "Cybermint",
            "Cybermint, the new age of cybercurrency tokens built on Solana. Every launch buys TRUMP, funded by a configured share of creator fees actually collected.")
    d.rect(0, 0, W, H, 32, fill=INK)
    g = []
    for x in range(40, W, 40):
        g.append(f"M{x} 0V{H}")
    for y in range(40, H, 40):
        g.append(f"M0 {y}H{W}")
    d.add(f'<path d="{"".join(g)}" stroke="#141619" stroke-width="1"/>')
    cx, cy = 1218, 352
    # minting die: concentric rings, reeded edge, crosshair
    d.circle(cx, cy, 290, fill=PANEL, stroke=LINE, sw=2)
    reeded_ring(d, cx, cy, 290, n=240, inner=16, stroke="#23272B", sw=3)
    d.circle(cx, cy, 256, stroke="#23272B", sw=2)
    for a in (0, 180):
        r = math.radians(a)
        d.line(cx + 306 * math.cos(r), cy + 306 * math.sin(r), cx + 338 * math.cos(r), cy + 338 * math.sin(r), stroke=GRAY_D, sw=2)
    # degree tick labels
    d.logo(cx - 4, cy, 440)
    # left copy
    d.rect(96, 128, 14, 14, 3, fill=MINT)
    d.text("SOLANA TOKEN LAUNCHPAD", 124, 142, 18, "monob", MINT, track=3)
    d.text("CYBERMINT", 90, 282, 138, "black", WHITE, track=-3)
    d.text("The new age of cybercurrency", 96, 352, 40, "semi", PALE, track=-0.4)
    d.text("tokens built on Solana.", 96, 402, 40, "semi", PALE, track=-0.4)
    # mechanism pill
    label = "EVERY LAUNCH BUYS TRUMP."
    lw = d.measure(label, 30, "black", 0.5) + 60
    d.rect(104, 458, lw, 70, 35, fill=MINT_D)
    d.rect(96, 450, lw, 70, 35, fill=MINT, stroke=INK, sw=4)
    d.text(label, 96 + 30, 496, 30, "black", INK, track=0.5)
    d.text("Purchases are funded by a configured share of creator fees", 98, 572, 19, "med", GRAY)
    d.text("actually collected. No collected fees, no purchase.", 98, 600, 19, "med", GRAY)
    # bottom rail
    d.line(96, 652, 1504, 652, stroke=LINE, sw=2)
    d.text("TRUMP PURCHASE ROUTING", 96, 686, 16, "monob", WHITE, track=2)
    d.text("CYBERMINT SHIELD", 440, 686, 16, "monob", WHITE, track=2)
    d.text("STATUS  DESIGN AND DOCUMENTATION STAGE", 1504, 686, 16, "mono", GRAY, anchor="end", track=1.5)
    d.save(f"{OUT}/hero.svg")

# ------------------------------------------------------------------ status strip
if want("status"):
    W, H = 1600, 380
    d = Doc(W, H, "Implementation status",
            "Documentation and design assets exist. The launch interface, launch transactions, TRUMP purchase routing and Cybermint Shield are planned and not implemented.")
    panel(d, "IMPLEMENTATION STATUS", "What exists in this repository today", "REVIEWED 2026-10-21")
    cols = [
        ("Docs and artwork", "README, docs, SVG artwork", [("IMPLEMENTED", "done")]),
        ("Launch interface", "Browser app, wallet link", [("PLANNED", "planned")]),
        ("Launch transactions", "Mint, metadata, SOL market", [("PLANNED", "planned")]),
        ("TRUMP routing", "Fees, swap, treasury", [("PLANNED", "planned"), ("EXTERNAL", "external")]),
        ("Cybermint Shield", "Escrow, authority, fee checks", [("PLANNED", "planned"), ("EXTERNAL", "external")]),
    ]
    x0, y0, cw, gap = 70, 182, 276, 20
    for i, (name, sub, chips) in enumerate(cols):
        x = x0 + i * (cw + gap)
        done = chips[0][1] == "done"
        d.rect(x, y0, cw, 140, 16, fill=PANEL2 if not done else "#0F2A22", stroke=MINT if done else LINE, sw=2)
        d.fit(name, cw - 40, 21, "bold")
        d.text(name, x + 20, y0 + 42, 21, "bold", WHITE)
        d.fit(sub, cw - 40, 16, "reg")
        d.text(sub, x + 20, y0 + 70, 16, "reg", GRAY)
        cxp = x + 20
        for lab, kind in chips:
            cxp += chip(d, cxp, y0 + 84, lab, kind, h=36, size=15) + 8
    d.save(f"{OUT}/status-strip.svg")

# ------------------------------------------------------------------ dividers
SECTIONS = [f"{i:02d}" for i in range(1, 16)]
if want("dividers"):
    for n in SECTIONS:
        W, H = 1600, 84
        d = Doc(W, H, f"Section {n}", f"Section divider {n}")
        cx, cy = 42, 42
        d.circle(cx + 5, cy + 5, 32, fill=MINT_D)
        d.circle(cx, cy, 32, fill=MINT, stroke=INK, sw=4)
        d.text(n, cx, cy + 9, 26, "black", INK, anchor="middle", track=-0.5)
        # reeded rail, mid gray so it reads on light and dark backgrounds
        d.line(96, 30, W - 2, 30, stroke=GRAY, sw=2, cap="butt")
        d.line(96, 54, W - 2, 54, stroke=GRAY, sw=2, cap="butt")
        ticks = "".join(f"M{x} 36V48" for x in range(104, W - 140, 10))
        d.path(ticks, stroke=GRAY, sw=2, cap="butt", opacity=0.55)
        
        d.text("CYBERMINT", W - 8, 48, 13, "monob", GRAY, anchor="end", track=2.2)
        d.save(f"{OUT}/divider-{n}.svg")

DARK_TXT = "#3A3E44"


def light_card(d, x, y, w, h, num, title, body, chips):
    d.card(x, y, w, h)
    d.rect(x + 20, y + 20, 44, 26, 13, fill=INK)
    d.text(num, x + 42, y + 38, 14, "monob", MINT, anchor="middle", track=1)
    d.fit(title, w - 40, 23, "bold")
    d.text(title, x + 20, y + 84, 23, "bold", INK, track=-0.2)
    d.para(body, x + 20, y + 116, w - 40, 18, "reg", DARK_TXT, lh=1.36)
    cxp = x + 20
    for lab, kind in chips:
        cxp += chip(d, cxp, y + h - 54, lab, kind, h=34, size=14) + 8


# ------------------------------------------------------------------ fee routing
if want("fee"):
    W, H = 1600, 1020
    d = Doc(W, H, "Fee routing diagram",
            "Launched tokens trade in SOL. Creator fees actually collected, F, are split: A equals F times the configured fraction a funds a SOL to TRUMP purchase on an external venue, and the acquired TRUMP goes to a public treasury. The remainder stays with the creator. A purchase counts only once its receipt is reconciled.")
    panel(d, "FEE ROUTING", "Creator fees to TRUMP purchases", "PLANNED MECHANISM")
    xs = [70 + i * 302 for i in range(5)]
    y, cw, ch = 196, 252, 262
    cards = [
        ("01", "Trading in SOL", "Launched tokens trade against SOL. They are not paired with TRUMP.", [("PLANNED", "planned_l")]),
        ("02", "Fees collected", "F lamports actually collected from the fee source. Accrued fees do not count.", [("PLANNED", "planned_l")]),
        ("03", "Allocation split", "A = F × a, computed in integer lamports with floor rounding.", [("PLANNED", "planned_l")]),
        ("04", "Purchase execution", "A, less disclosed costs, is swapped from SOL to TRUMP on an external venue.", [("EXTERNAL", "external_l")]),
        ("05", "Public treasury", "Receives acquired TRUMP. Address not yet designated.", [("PLANNED", "planned_l")]),
    ]
    for x, c in zip(xs, cards):
        light_card(d, x, y, cw, ch, *c)
    for i in range(4):
        d.arrow([(xs[i] + cw + 12, y + ch / 2), (xs[i + 1] - 8, y + ch / 2)], stroke=MINT, sw=4, head=11)
    # creator share branch
    bx = xs[2] + cw / 2
    d.arrow([(bx, y + ch + 12), (bx, 530)], stroke=GRAY, sw=3, head=10)
    d.rect(xs[2], 534, cw, 60, 30, fill=PANEL2, stroke=GRAY_D, sw=2)
    d.text("Creator keeps F − A", bx, 571, 19, "bold", WHITE, anchor="middle")
    # reconciliation bar
    rx0, rx1 = xs[3], xs[4] + cw
    for xx in (xs[3] + cw / 2, xs[4] + cw / 2):
        d.arrow([(xx, y + ch + 12), (xx, 530)], stroke=MINT, sw=3, head=10, dash="7 7")
    d.rect(rx0, 534, rx1 - rx0, 60, 30, fill="#0F2A22", stroke=MINT, sw=2)
    d.text("RECONCILIATION", rx0 + 28, 570, 15, "monob", MINT, track=2)
    d.fit("signature matched to treasury receipt", rx1 - rx0 - 230, 16, "med")
    d.text("signature matched to treasury receipt", rx0 + 200, 570, 16, "med", PALE)
    # worked example
    ex, ey, ew, eh = 70, 640, 760, 330
    d.rect(ex, ey, ew, eh, 18, fill=PANEL2, stroke=LINE, sw=2)
    d.text("WORKED EXAMPLE", ex + 32, ey + 46, 15, "monob", MINT, track=2)
    d.text("ILLUSTRATIVE VALUES ONLY", ex + ew - 32, ey + 46, 15, "mono", GRAY, anchor="end", track=0.5)
    rows = [
        ("F", "3_250_000_000", "lamports collected"),
        ("a", "2_500", "basis points, example only"),
        ("A", "812_500_000", "lamports = F × a / 10_000"),
        ("F − A", "2_437_500_000", "lamports retained by creator"),
    ]
    for i, (k, v, note) in enumerate(rows):
        yy = ey + 100 + i * 44
        d.text(k, ex + 32, yy, 21, "monob", PALE if k != "A" else MINT)
        d.text(v, ex + 330, yy, 21, "monob", WHITE if k != "A" else MINT, anchor="end")
        d.text(note, ex + 356, yy, 17, "mono", GRAY)
    d.line(ex + 32, ey + 262, ex + ew - 32, ey + 262, stroke=LINE, sw=2)
    d.text("Integer math only. 1 SOL = 1_000_000_000 lamports.", ex + 32, ey + 298, 17, "mono", GRAY)
    # settlement states
    sx, sy, sw_, sh = 870, 640, 660, 330
    d.rect(sx, sy, sw_, sh, 18, fill=PANEL2, stroke=LINE, sw=2)
    d.text("SETTLEMENT STATES", sx + 32, sy + 46, 15, "monob", MINT, track=2)

    def flow(labels, x, yy, kinds):
        pos = []
        for lab, kind in zip(labels, kinds):
            w = chip(d, x, yy, lab, kind, h=34, size=14)
            pos.append((x, w))
            x += w + 34
        for (x1, w1), (x2, _) in zip(pos, pos[1:]):
            d.arrow([(x1 + w1 + 6, yy + 16), (x2 - 6, yy + 16)], stroke=GRAY, sw=2, head=7)
        return pos

    flow(["ACCRUED", "COLLECTED", "ALLOCATED", "PENDING"], sx + 32, sy + 82, ["notenabled", "pending", "pending", "pending"])
    p2 = flow(["SUBMITTED", "CONFIRMED", "RECONCILED"], sx + 32, sy + 150, ["pending", "pending", "verified"])
    fx = p2[0][0] + p2[0][1] / 2
    d.arrow([(fx, sy + 192), (fx, sy + 218)], stroke=GRAY, sw=2, head=7, dash="4 5")
    chip(d, p2[0][0], sy + 222, "FAILED", "failed", h=34, size=14)
    d.text("retry policy undecided", p2[0][0] + 112, sy + 245, 16, "mono", GRAY)
    d.para("Allocated is not purchased. A purchase counts only after confirmation and a reconciled treasury receipt.",
           sx + 32, sy + 296, 600, 16, "med", PALE, lh=1.4)
    d.save(f"{OUT}/fee-routing.svg")

# ------------------------------------------------------------------ shield
def icon_lock(d, x, y):
    d.rect(x, y + 14, 34, 26, 6, fill=MINT)
    d.path(f"M{x+7} {y+14}V{y+8}a10 10 0 0 1 20 0V{y+14}", stroke=MINT, sw=4)
    d.circle(x + 17, y + 27, 4, fill=INK)


def icon_key(d, x, y):
    d.circle(x + 11, y + 20, 10, stroke=MINT, sw=4)
    d.path(f"M{x+21} {y+20}H{x+38}M{x+32} {y+20}V{y+28}M{x+38} {y+20}V{y+26}", stroke=MINT, sw=4)


def icon_split(d, x, y):
    d.path(f"M{x+2} {y+20}H{x+16}L{x+34} {y+6}M{x+16} {y+20}L{x+34} {y+34}", stroke=MINT, sw=4)
    d.circle(x + 16, y + 20, 5, fill=MINT)


if want("shield"):
    W, H = 1600, 1100
    d = Doc(W, H, "Cybermint Shield verification diagram",
            "Three planned groups of checks: creator escrow, token authorities and fee routing. Every check reports one of five states: verified, pending, not enabled, failed or unknown. Unknown is never treated as passed. Shield cannot establish creator intent, holdings in undisclosed wallets, coordinated selling, market losses or the future behavior of external programs.")
    panel(d, "CYBERMINT SHIELD", "Verifiable launch protections", "PLANNED  NOT IMPLEMENTED")
    groups = [
        (icon_lock, "Creator escrow", "Creator allocation held in a time locked escrow account.", [
            "Escrowed amount equals disclosure",
            "Unlock schedule read from escrow",
            "Withdrawal authority identified",
            "Cancel and admin withdraw flags",
            "Escrow program on reviewed list",
            "Unescrowed creator balance shown",
        ], "READS  escrow account, token accounts"),
        (icon_key, "Token authorities", "Who can still mint, freeze or reshape the token.", [
            "Mint authority is none",
            "Freeze authority is none",
            "Owner is SPL Token or Token-2022",
            "Token-2022 extensions enumerated",
            "Permanent delegate, hook flagged",
            "Metadata update authority shown",
        ], "READS  mint account, metadata account"),
        (icon_split, "Fee routing", "Whether the TRUMP allocation is configured as disclosed.", [
            "Allocation equals disclosed fraction",
            "Destination equals treasury",
            "Configuration authority identified",
            "Whether config can still change",
            "Purchases reconciled to receipts",
            "Source slot and time recorded",
        ], "READS  fee config, treasury, index"),
    ]
    gx, gy, gw, gh = 70, 190, 460, 520
    for i, (icon, title, sub, checks, foot) in enumerate(groups):
        x = gx + i * (gw + 40)
        d.rect(x, gy, gw, gh, 20, fill=PANEL2, stroke=LINE, sw=2)
        icon(d, x + 32, gy + 30)
        d.text(title, x + 88, gy + 62, 28, "xbold", WHITE, track=-0.3)
        d.para(sub, x + 32, gy + 112, gw - 64, 17, "reg", GRAY, lh=1.35)
        d.line(x + 32, gy + 158, x + gw - 32, gy + 158, stroke=LINE, sw=2)
        for j, c in enumerate(checks):
            yy = gy + 200 + j * 46
            d.rect(x + 32, yy - 15, 18, 18, 4, stroke=MINT, sw=2)
            d.fit(c, gw - 100, 18, "med")
            d.text(c, x + 66, yy, 18, "med", WHITE)
        d.line(x + 32, gy + gh - 62, x + gw - 32, gy + gh - 62, stroke=LINE, sw=2)
        d.text(foot, x + 32, gy + gh - 26, 15, "mono", GRAY)
    # states
    sy = 760
    d.text("VERIFICATION STATES", 70, sy, 15, "monob", MINT, track=2)
    states = [
        ("VERIFIED", "verified", "Ran against finalized state and the condition holds."),
        ("PENDING", "pending", "Started, or waiting for finality or indexing."),
        ("NOT ENABLED", "notenabled", "Protection is not configured for this launch."),
        ("FAILED", "failed", "Ran and the condition does not hold."),
        ("UNKNOWN", "unknown", "Could not be evaluated. Never treated as passed."),
    ]
    for i, (lab, kind, txt) in enumerate(states):
        x = 70 + i * 296
        chip(d, x, sy + 22, lab, kind, h=38, size=15)
        d.para(txt, x, sy + 96, 268, 17, "reg", GRAY if kind != "unknown" else WHITE)
    by = 960
    d.rect(70, by, 1460, 92, 16, fill=PANEL2, stroke=LINE, sw=2)
    d.rect(70, by, 8, 92, 0, fill=WHITE)
    d.text("SHIELD CANNOT ESTABLISH", 106, by + 40, 15, "monob", WHITE, track=2)
    d.text("Creator intent, holdings in undisclosed wallets, coordinated selling, market losses, or the future behavior of external programs.", 106, by + 70, 18, "med", GRAY)
    d.save(f"{OUT}/shield.svg")

# ------------------------------------------------------------------ lifecycle
if want("lifecycle"):
    W, H = 1600, 900
    d = Doc(W, H, "Token launch lifecycle diagram",
            "Draft, validation, wallet connection, transaction preparation, user approval, submission, confirmation, post launch verification, then complete. Failure paths: signature rejected, blockhash expired, and partial completion when launch steps span several transactions.")
    panel(d, "TRANSACTION LIFECYCLE", "From draft to verified launch", "PLANNED FLOW")
    xs = [70 + i * 302 for i in range(5)]
    nw, nh = 252, 140
    r1, r2 = 196, 430
    row1 = [("01", "Draft", "CLIENT"), ("02", "Validation", "CLIENT"), ("03", "Wallet connection", "WALLET"),
            ("04", "Transaction preparation", "CLIENT + RPC"), ("05", "User approval", "WALLET")]
    row2 = [("06", "Submission", "RPC"), ("07", "Confirmation", "RPC"), ("08", "Post launch verification", "INDEXER + RPC"),
            ("09", "Complete", "ALL STEPS VERIFIED")]

    def node(x, y, num, title, actor, done=False):
        fill, stroke, tc = (MINT, INK, INK) if done else (PANEL2, LINE, WHITE)
        if done:
            d.rect(x + 8, y + 8, nw, nh, 16, fill=MINT_D)
        d.rect(x, y, nw, nh, 16, fill=fill, stroke=stroke, sw=2 if not done else 4)
        d.text(num, x + 22, y + 36, 14, "monob", MINT if not done else INK, track=1)
        lines = d.wrap(title, nw - 44, 21, "bold")
        for k, ln in enumerate(lines):
            d.text(ln, x + 22, y + 68 + k * 25, 21, "bold", tc)
        d.text(actor, x + 22, y + nh - 18, 14, "mono", GRAY if not done else INK, track=1.2)

    for x, n in zip(xs, row1):
        node(x, r1, *n)
    for x, n in zip(xs, row2):
        node(x, r2, *n, done=n[0] == "09")
    # failure node
    fx = xs[4]
    d.rect(fx, r2, nw, nh, 16, fill=WHITE, stroke=INK, sw=4)
    d.text("10", fx + 22, r2 + 36, 14, "monob", INK, track=1)
    d.text("Failed or partial", fx + 22, r2 + 68, 21, "bold", INK)
    d.text("STEP STATE RECORDED", fx + 22, r2 + nh - 18, 14, "mono", DARK_TXT, track=1.2)
    for i in range(4):
        d.arrow([(xs[i] + nw + 8, r1 + nh / 2), (xs[i + 1] - 8, r1 + nh / 2)], stroke=MINT, sw=4, head=10)
    for i in range(2):
        d.arrow([(xs[i] + nw + 8, r2 + nh / 2), (xs[i + 1] - 8, r2 + nh / 2)], stroke=MINT, sw=4, head=10)
    d.arrow([(xs[2] + nw + 8, r2 + nh / 2), (xs[3] - 8, r2 + nh / 2)], stroke=MINT, sw=4, head=10)
    # wrap from 05 to 06
    mid = r1 + nh + (r2 - r1 - nh) / 2
    d.arrow([(xs[4] + nw / 2, r1 + nh + 8), (xs[4] + nw / 2, mid), (xs[0] + nw / 2, mid), (xs[0] + nw / 2, r2 - 8)], stroke=MINT, sw=4, head=10)
    # failure feeders
    d.arrow([(xs[1] + nw / 2, r2 + nh + 8), (xs[1] + nw / 2, r2 + nh + 34), (xs[4] + nw / 2, r2 + nh + 34), (xs[4] + nw / 2, r2 + nh + 8)], stroke=GRAY, sw=2, head=8, dash="6 6")
    d.line(xs[2] + nw / 2, r2 + nh + 8, xs[2] + nw / 2, r2 + nh + 34, stroke=GRAY, sw=2, dash="6 6")

    def badge(cx, cy, letter):
        d.circle(cx + 3, cy + 3, 17, fill=MINT_D)
        d.circle(cx, cy, 17, fill=WHITE, stroke=INK, sw=3)
        d.text(letter, cx, cy + 6, 17, "black", INK, anchor="middle")

    badge(xs[4] + nw - 6, r1 + 6, "A")
    badge(xs[1] + nw - 6, r2 + 6, "B")
    badge(xs[2] + nw - 6, r2 + 6, "C")
    notes = [
        ("A", "Signature rejected", "Nothing was broadcast. Return to review with the draft intact. Retry needs a new user action."),
        ("B", "Blockhash expired", "Status stays unknown until block height passes lastValidBlockHeight and the signature is absent. Only then rebuild and re-sign."),
        ("C", "Partial completion", "Launch steps may span several transactions. Persist each confirmed step and resume from it. Never recreate an existing mint."),
    ]
    for i, (L, t, b) in enumerate(notes):
        x = 70 + i * 500
        y = 660
        d.rect(x, y, 460, 196, 18, fill=PANEL2, stroke=LINE, sw=2)
        badge(x + 44, y + 46, L)
        d.text(t, x + 78, y + 54, 23, "bold", WHITE)
        d.para(b, x + 32, y + 100, 396, 18, "reg", GRAY, lh=1.42)
    d.save(f"{OUT}/lifecycle.svg")

# ------------------------------------------------------------------ architecture
if want("arch"):
    W, H = 1600, 1200
    d = Doc(W, H, "System architecture diagram",
            "Four lanes: browser, wallet, proposed server services and Solana or external dependencies. Every application component is proposed. The repository currently contains documentation and artwork only.")
    panel(d, "SYSTEM ARCHITECTURE", "Proposed boundaries around a docs-only repository", None)
    lanes = [("BROWSER", "PROPOSED"), ("WALLET", "EXTERNAL"), ("SERVER", "PROPOSED"), ("SOLANA AND EXTERNAL", "EXTERNAL")]
    lx = [70 + i * 375 for i in range(4)]
    lw = 335
    ly0, ly1 = 180, 1000
    for (name, tag), x in zip(lanes, lx):
        d.rect(x, ly0, lw, ly1 - ly0, 18, fill=PANEL, stroke=LINE, sw=2)
        d.text(name, x + 20, ly0 + 38, 14, "monob", WHITE, track=2)
        d.text(tag, x + lw - 20, ly0 + 38, 14, "mono", GRAY, anchor="end", track=1.5)
    # trust boundaries
    for i, lab in enumerate(["SIGNATURE", "SERVER KEYS", "RPC TRUST"]):
        bx = lx[i] + lw + 20
        d.line(bx, ly0 + 10, bx, ly1 - 10, stroke=GRAY_D, sw=2, dash="3 7")
    bw, bh = 268, 80
    pitch = 106
    ry = [240 + k * pitch for k in range(7)]

    def box(lane, row, title, sub, kind):
        x = lx[lane] + 20
        y = ry[row]
        if kind == "proposed":
            d.rect(x, y, bw, bh, 12, fill=PANEL2, stroke=WHITE, sw=1.5, dash="6 5")
        else:
            d.rect(x, y, bw, bh, 12, fill=PANEL2, stroke=GRAY_D, sw=2)
        d.fit(title, bw - 36, 19, "bold")
        d.fit(sub, bw - 36, 16, "reg")
        d.text(title, x + 18, y + 34, 19, "bold", WHITE)
        d.text(sub, x + 18, y + 59, 16, "reg", GRAY)
        return x, y

    box(0, 0, "Launch interface", "Draft form, review, status", "proposed")
    box(0, 1, "Launch tx adapter", "Builds unsigned transactions", "proposed")
    box(0, 2, "Shield and treasury views", "Renders states with sources", "proposed")
    box(1, 0, "Phantom wallet", "Holds keys, signs or rejects", "external")
    box(2, 1, "Metadata upload", "Validates and stores metadata", "proposed")
    box(2, 2, "Shield verifier", "Reads accounts, emits states", "proposed")
    box(2, 4, "Fee collection worker", "Collects F, records A", "proposed")
    box(2, 5, "Purchase executor", "Swaps A for TRUMP", "proposed")
    box(2, 6, "Indexer and ledger", "Reconciles receipts", "proposed")
    box(3, 0, "Solana RPC", "Reads, simulation, submission", "external")
    box(3, 1, "Metadata storage", "Provider undecided", "external")
    box(3, 2, "SPL Token, Token-2022", "Mint and token accounts", "external")
    box(3, 3, "Escrow program", "Program not selected", "external")
    box(3, 4, "Launch market", "Fee source, design undecided", "external")
    box(3, 5, "Swap venue", "Route not selected", "external")
    box(3, 6, "Treasury account", "Address not designated", "external")

    def h_arrow(row, xa, xb, label, color=MINT, back=False, dy=0):
        y = ry[row] + bh / 2 + dy
        pts = [(xb, y), (xa, y)] if back else [(xa, y), (xb, y)]
        d.arrow(pts, stroke=color, sw=3, head=9)
        lxp = (xa + xb) / 2
        d.fit(label, abs(xb - xa) - 8, 14, "mono")
        d.text(label, lxp, y - 10, 14, "mono", PALE, anchor="middle")

    R = lambda lane: lx[lane] + 20 + bw
    Lf = lambda lane: lx[lane] + 20
    h_arrow(0, R(0) + 6, Lf(1) - 6, "sign")
    h_arrow(0, R(1) + 6, Lf(3) - 6, "signed transaction")
    h_arrow(1, R(0) + 6, Lf(2) - 6, "metadata JSON")
    h_arrow(1, R(2) + 6, Lf(3) - 6, "upload")
    h_arrow(2, R(0) + 6, Lf(2) - 6, "verification states", back=True)
    h_arrow(2, R(2) + 6, Lf(3) - 6, "reads")
    h_arrow(4, R(2) + 6, Lf(3) - 6, "collect F")
    h_arrow(5, R(2) + 6, Lf(3) - 6, "swap A")
    h_arrow(6, R(2) + 6, Lf(3) - 6, "receipts")
    cx2 = Lf(2) + bw / 2
    d.arrow([(cx2, ry[4] + bh + 4), (cx2, ry[5] - 4)], stroke=MINT, sw=3, head=8)
    d.arrow([(cx2, ry[5] + bh + 4), (cx2, ry[6] - 4)], stroke=MINT, sw=3, head=8)
    # lane notes
    d.para("Private keys never leave the wallet. The app receives signatures, never keys.", Lf(1), ry[4] + 30, bw, 17, "reg", GRAY)
    d.para("Browser configuration is public by definition. No secrets in client bundles.", Lf(0), ry[4] + 30, bw, 17, "reg", GRAY)
    d.para("Server keys that sign purchases control treasury inflows. Custody model undecided.", Lf(2), ry[3] + 18, bw, 16, "reg", PALE)
    # repository band
    by = 1030
    d.rect(78, by + 8, 1460, 96, 18, fill=MINT_D)
    d.rect(70, by, 1460, 96, 18, fill=MINT, stroke=INK, sw=4)
    d.text("THIS REPOSITORY TODAY", 102, by + 40, 15, "monob", INK, track=2)
    d.text("Documentation, integration contracts, threat model and SVG artwork. No application, service or onchain program code exists yet.", 102, by + 70, 17, "med", INK)
    # legend
    ly = 1160
    d.rect(70, ly - 16, 40, 22, 6, fill=PANEL2, stroke=WHITE, sw=1.5, dash="6 5")
    d.text("Proposed component", 122, ly, 17, "med", GRAY)
    d.rect(330, ly - 16, 40, 22, 6, fill=PANEL2, stroke=GRAY_D, sw=2)
    d.text("External dependency", 382, ly, 17, "med", GRAY)
    d.line(600, ly - 5, 640, ly - 5, stroke=GRAY_D, sw=2, dash="3 7")
    d.text("Trust boundary", 652, ly, 17, "med", GRAY)
    d.rect(820, ly - 16, 40, 22, 6, fill=MINT)
    d.text("Exists in this repository", 872, ly, 17, "med", GRAY)
    d.save(f"{OUT}/architecture.svg")

print("ok", sorted(os.listdir(OUT)))
