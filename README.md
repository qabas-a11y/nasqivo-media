# NASQIVO Media Library

Public marketing assets for [NASQIVO on Instagram](https://www.instagram.com/nasqivo/).

This repository contains **public promotional content only**. It is independent of NASQIVO LIFE, INJAZ and other private projects.

## Contents

- `content/posts.json` — three starter post specifications and Arabic captions.
- `scripts/render.py` — deterministic renderer for 1080×1350 PNG promotional creatives.
- `media/` — public PNG output created by GitHub Actions.
- `.github/workflows/build-media.yml` — renders and commits images. **It never publishes to Instagram.**

## Media URLs (after successful build)
- https://raw.githubusercontent.com/qabas-a11y/nasqivo-media/main/media/post-01.png
- https://raw.githubusercontent.com/qabas-a11y/nasqivo-media/main/media/post-02.png
- https://raw.githubusercontent.com/qabas-a11y/nasqivo-media/main/media/post-03.png

**Important:** These are newly rendered clean templates, **not pixel-for-pixel copies of the earlier 3D images generated in ChatGPT**. Review the results before using them. Do not claim Instagram posts were published without verifying their permalinks.

## Media and publishing architecture
1. ChatGPT drafts branded content for review.
2. This public repository serves the approved image URLs without requiring TinyFish GitHub login.
3. Official Meta Instagram Publishing API or a supported social-publishing integration receives public media URLs and publishes them with authorized credentials.
4. Check publication status and report a verified Instagram link.

A public URL does not make Instagram's **native web file-picker** able to upload the image automatically. Do not upload credentials, tokens, private customer data or unlicensed client media here.

© NASQIVO
