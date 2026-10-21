#!/usr/bin/env node
// Repository documentation checks for Cybermint.
//
// Runs with Node.js 18 or newer and has no dependencies:
//   node scripts/check-docs.mjs
//
// Checks:
//   1. Every relative link and image in Markdown files points at a file that exists,
//      and every in-page or cross-file heading anchor resolves.
//   2. Every SVG under docs/assets is self contained: no <script>, no <foreignObject>,
//      no event handler attributes, no external href, no CSS @import or url() to a remote host.
//   3. Markdown and SVG text contain no em dash characters (house style).
//   4. .env.example assigns no values to names that look like secrets.
//
// Exits with status 1 and prints each problem when any check fails.

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname, resolve, relative, extname } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKIP_DIRS = new Set([".git", "node_modules"]);
const problems = [];
const fail = (file, msg) => problems.push(`${relative(root, file)}: ${msg}`);

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (SKIP_DIRS.has(name)) continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

const files = walk(root);
const markdown = files.filter((f) => extname(f) === ".md");
const svgs = files.filter((f) => extname(f) === ".svg");

// GitHub style heading slugs: lowercase, drop punctuation, spaces to hyphens, dedupe with -1, -2.
function slugs(md) {
  const seen = new Map();
  const out = new Set();
  let inFence = false;
  for (const line of md.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence;
    if (inFence) continue;
    const m = /^(#{1,6})\s+(.*?)\s*#*\s*$/.exec(line);
    if (!m) continue;
    const text = m[2]
      .replace(/<[^>]+>/g, "")
      .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
      .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
      .replace(/`/g, "");
    let slug = text.toLowerCase().trim().replace(/[^\p{L}\p{N}\s_-]/gu, "").replace(/\s/g, "-");
    const n = seen.get(slug) ?? 0;
    seen.set(slug, n + 1);
    if (n > 0) slug = `${slug}-${n}`;
    out.add(slug);
  }
  return out;
}

const slugCache = new Map();
const slugsFor = (file) => {
  if (!slugCache.has(file)) slugCache.set(file, slugs(readFileSync(file, "utf8")));
  return slugCache.get(file);
};

function stripCode(md) {
  return md.replace(/^(```|~~~)[\s\S]*?^\1/gm, "").replace(/`[^`\n]*`/g, "");
}

for (const file of markdown) {
  const raw = readFileSync(file, "utf8");
  if (raw.includes("\u2014")) fail(file, "contains an em dash (U+2014)");
  const md = stripCode(raw);
  const targets = [];
  for (const m of md.matchAll(/!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)/g)) targets.push(m[1]);
  for (const m of md.matchAll(/\b(?:src|href|srcset)="([^"]+)"/g)) targets.push(m[1]);
  for (const t of targets) {
    if (/^(https?:|mailto:)/i.test(t)) continue;
    const [pathPart, anchor] = t.split("#");
    const target = pathPart ? resolve(dirname(file), decodeURIComponent(pathPart)) : file;
    if (!existsSync(target)) {
      fail(file, `broken link or image: ${t}`);
      continue;
    }
    if (anchor && extname(target) === ".md" && !slugsFor(target).has(anchor)) {
      fail(file, `missing anchor #${anchor} in ${relative(root, target)}`);
    }
  }
}

for (const file of svgs) {
  const svg = readFileSync(file, "utf8");
  if (/<script[\s>]/i.test(svg)) fail(file, "contains <script>");
  if (/<foreignObject[\s>]/i.test(svg)) fail(file, "contains <foreignObject>");
  if (/\son[a-z]+\s*=/i.test(svg)) fail(file, "contains an event handler attribute");
  if (/@import/i.test(svg)) fail(file, "contains CSS @import");
  if (/url\(\s*['"]?(https?:)?\/\//i.test(svg)) fail(file, "references a remote url()");
  for (const m of svg.matchAll(/(?:xlink:)?href\s*=\s*"([^"]*)"/g)) {
    if (!m[1].startsWith("#")) fail(file, `external href: ${m[1]}`);
  }
  if (!/<title[\s>]/.test(svg)) fail(file, "missing <title> for accessibility");
  if (svg.includes("\u2014")) fail(file, "contains an em dash (U+2014)");
}

const envFile = join(root, ".env.example");
if (existsSync(envFile)) {
  const secretName = /(SECRET|PRIVATE|KEYPAIR|MNEMONIC|SEED|PASSWORD|TOKEN_KEY|API_KEY)/i;
  for (const [i, line] of readFileSync(envFile, "utf8").split("\n").entries()) {
    const m = /^\s*([A-Z0-9_]+)\s*=\s*(.*)$/.exec(line);
    if (!m) continue;
    if (secretName.test(m[1])) fail(envFile, `line ${i + 1}: secret-like name ${m[1]} must not appear in .env.example`);
    if (/^[1-9A-HJ-NP-Za-km-z]{80,}$/.test(m[2].trim())) fail(envFile, `line ${i + 1}: value looks like an encoded private key`);
  }
}

console.log(`Checked ${markdown.length} Markdown files and ${svgs.length} SVG files.`);
if (problems.length) {
  console.error(`\n${problems.length} problem(s):`);
  for (const p of problems) console.error(`  ${p}`);
  process.exit(1);
}
console.log("All documentation checks passed.");
